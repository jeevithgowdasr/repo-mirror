from datetime import datetime
from collections import Counter
from typing import Dict, Any, List
from .github_service import GitHubService

class ScoringService:
    def __init__(self, github_service: GitHubService):
        self.github = github_service

    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Analyzes a GitHub repository and extracts detailed metrics for advanced scoring.
        """
        # 1. Fetch Basic Metadata
        metadata = self.github.get_repo_metadata(owner, repo)
        if not metadata:
            return {"error": "Repository not found"}

        default_branch = metadata.get("default_branch", "main")
        
        # 2. Fetch File Tree (Recursive)
        tree_data = self.github.get_git_tree(owner, repo, branch=default_branch)
        tree_items = tree_data.get("tree", []) if tree_data else []

        # 3. Analyze File Structure
        files_count = 0
        folders_count = 0
        max_depth = 0
        has_readme = False
        has_tests = False
        has_gitignore = False
        has_ci = False # .github/workflows etc.
        extensions = []
        standard_folders_detected = []
        root_files_count = 0
        
        standard_folders = {"src", "app", "lib", "utils", "services", "components", "api", "routes", "models"}

        for item in tree_items:
            path = item.get("path", "")
            item_type = item.get("type")
            low_path = path.lower()
            
            # Depth calculation
            depth = path.count("/") + 1
            if depth > max_depth:
                max_depth = depth

            if item_type == "blob":  # File
                files_count += 1
                if "/" not in path:
                    root_files_count += 1
                
                if low_path.endswith("readme.md"):
                    has_readme = True
                if ".gitignore" in low_path:
                    has_gitignore = True
                
                # Extension tracking
                if "." in path.rsplit("/", 1)[-1]:
                    ext = path.rsplit(".", 1)[-1].lower()
                    extensions.append(ext)

            elif item_type == "tree":  # Directory
                folders_count += 1
                folder_name = path.split("/")[-1].lower()
                
                if folder_name in standard_folders:
                    standard_folders_detected.append(folder_name)
                    
                if "test" in folder_name:
                    has_tests = True
                
                if ".github" in low_path or ".circleci" in low_path:
                    has_ci = True

        # 4. Fetch Commit History & Messages
        commits = self.github.get_commit_history(owner, repo, per_page=100)
        commit_count = len(commits)
        
        # 5. Analyze Commits
        commit_dates = []
        commit_messages = []
        
        for commit in commits:
            c_info = commit.get("commit", {})
            author_date = c_info.get("author", {}).get("date")
            message = c_info.get("message", "")
            
            commit_messages.append(message)
            
            if author_date:
                try:
                    date_obj = datetime.strptime(author_date, "%Y-%m-%dT%H:%M:%SZ")
                    commit_dates.append(date_obj)
                except ValueError:
                    pass
        
        active_days = set(d.date() for d in commit_dates)
        
        # 6. Readme Content Analysis
        readme_content = ""
        if has_readme:
             readme_content = self.github.get_readme_content(owner, repo) or ""

        # 7. Fetch Languages
        languages = self.github.get_languages(owner, repo) or {}

        return {
            "structure": {
                "file_count": files_count,
                "folder_count": folders_count,
                "root_files_count": root_files_count,
                "max_depth": max_depth,
                "has_readme": has_readme,
                "has_tests": has_tests,
                "has_gitignore": has_gitignore,
                "has_ci": has_ci,
                "standard_folders": list(set(standard_folders_detected))
            },
            "activity": {
                "analyzed_commit_count": commit_count,
                "unique_active_days": len(active_days),
                "commit_messages": commit_messages,
                "latest_commit": commit_dates[0].isoformat() if commit_dates else None,
            },
            "documentation": {
                "readme_content": readme_content
            },
            "tech_stack": {
                "languages": list(languages.keys()),
                "language_distribution": languages,
                "detected_extensions": list(set(extensions))
            }
        }

    def calculate_score(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a deterministic score (0-100) using advanced heuristics.
        Now returns a transparent breakdown with reasons and improvement hints.
        """
        score = 0
        weaknesses = []
        breakdown = {}
        
        structure = repo_data.get("structure", {})
        activity = repo_data.get("activity", {})
        documentation = repo_data.get("documentation", {})
        stack = repo_data.get("tech_stack", {})

        # Helper to structure valid category output
        def create_category(name, current, max_pts, reasons, hint):
            return {
                "score": current,
                "max_score": max_pts,
                "reasons": reasons,
                "hint": hint
            }

        # --- 1. Code Organization (Max 20 pts) ---
        org_current = 0
        org_reasons = []
        
        # H1: Standard Folder Structure (5 pts)
        if structure.get("standard_folders"):
             org_current += 5
             org_reasons.append("✅ Detected standard folders (src/app/utils)")
        else:
             org_reasons.append("❌ Standard architecture folders (src, app, utils) not detected")
             weaknesses.append("Standard architecture folders (src, app, utils) not detected")
             
        # H2: Avoiding Root Dumping (5 pts)
        total_files = structure.get("file_count", 0)
        root_files = structure.get("root_files_count", 0)
        if total_files > 3 and (root_files / total_files) < 0.5:
            org_current += 5
            org_reasons.append("✅ Modular file distribution")
        elif total_files > 3:
            org_reasons.append("❌ High file concentration in root directory")
            weaknesses.append("High file concentration in root directory")
            
        # H3: General Structure (5 pts)
        if structure.get("folder_count", 0) > 2:
             org_current += 5
        else:
             org_reasons.append("⚠️ Directory structure appears flat")
             
        # H4: Depth (5 pts)
        depth = structure.get("max_depth", 0)
        if 2 <= depth <= 8:
            org_current += 5
        else:
            org_reasons.append(f"⚠️ Directory depth ({depth} levels) falls outside standard range")
        
        score += org_current
        breakdown["Code Organization"] = create_category(
            "Code Organization", org_current, 20, org_reasons, 
            "Refactor code into logical subdirectories (e.g., /src, /components) to improve modularity."
        )

        # --- 2. Documentation Quality (Max 20 pts) ---
        doc_current = 0
        doc_reasons = []
        readme_text = documentation.get("readme_content", "").lower()
        
        # H1: Existence (5 pts)
        if structure.get("has_readme"):
            doc_current += 5
            doc_reasons.append("✅ README.md is present")
        else:
            doc_reasons.append("❌ README.md file is absent")
            weaknesses.append("README.md file is absent")

        # H2: Completeness (15 pts - 5 per section)
        required_sections = ["usage", "install", "setup", "getting started"]
        found_sections = [s for s in required_sections if s in readme_text]
        
        if len(found_sections) >= 2:
            doc_current += 10
            doc_reasons.append(f"✅ 'Installation/Usage' sections identified")
        elif len(found_sections) == 1:
            doc_current += 5
            doc_reasons.append(f"⚠️ Documentation incomplete (missing sections)")
        else:
            if structure.get("has_readme"):
                 doc_reasons.append("❌ Documentation omits 'Usage' or 'Installation' steps")
                 weaknesses.append("Documentation omits 'Usage' or 'Installation' steps")
        
        if len(readme_text) > 200: 
            doc_current += 5
        else:
            doc_reasons.append("⚠️ Documentation content is brief")
            
        score += doc_current
        breakdown["Documentation"] = create_category(
            "Documentation", doc_current, 20, doc_reasons, 
            "Expand documentation to include setup steps and usage examples."
        )

        # --- 3. Commit Hygiene & Consistency (Max 20 pts) ---
        git_current = 0
        git_reasons = []
        messages = activity.get("commit_messages", [])
        
        # H1: Semantic Commits (5 pts)
        semantic_prefixes = ["feat", "fix", "chore", "docs", "refactor", "style", "test"]
        semantic_count = sum(1 for m in messages if any(m.lower().startswith(p) for p in semantic_prefixes))
        
        if len(messages) > 0 and (semantic_count / len(messages)) > 0.2:
             git_current += 5
             git_reasons.append("✅ Semantic prefixes detected")
        else:
             git_reasons.append("❌ Commit messages do not follow semantic conventions")
             weaknesses.append("Commit messages do not follow semantic conventions (e.g., feat:, fix:)")

        # H2: Volume & Frequency (10 pts)
        if activity.get("analyzed_commit_count", 0) > 10:
             git_current += 5
             git_reasons.append("✅ Sufficient commit volume")
        
        if activity.get("unique_active_days", 0) > 3:
             git_current += 5
             git_reasons.append("✅ Consistent development activity")
        elif activity.get("analyzed_commit_count", 0) > 5 and activity.get("unique_active_days", 0) == 1:
             git_reasons.append("⚠️ Activity concentrated in single day")
             weaknesses.append("Activity concentrated in single day")
             
        # H3: Avoid generic messages (5 pts)
        bad_messages = ["update", "file", "upload", "changes", "fix"]
        lazy_count = sum(1 for m in messages if m.lower().strip() in bad_messages)
        if len(messages) > 5 and lazy_count == 0:
             git_current += 5
        elif lazy_count > 0:
             git_reasons.append(f"❌ Generic commit messages detected ({lazy_count})")
             weaknesses.append("Generic commit messages detected (e.g., 'Update file')")

        score += git_current
        breakdown["Commit Hygiene"] = create_category(
            "Commit Hygiene", git_current, 20, git_reasons, 
            "Adhere to conventional commits (feat: ...) and commit incrementally."
        )

        # --- 4. Engineering Standards (Max 20 pts) ---
        eng_current = 0
        eng_reasons = []
        
        # H1: Testing (10 pts)
        if structure.get("has_tests"):
            eng_current += 10
            eng_reasons.append("✅ Automated tests identified")
        else:
            eng_reasons.append("❌ Testing framework not detected")
            weaknesses.append("Testing framework not detected")
            
        # H2: CI/CD (5 pts)
        if structure.get("has_ci"):
            eng_current += 5
            eng_reasons.append("✅ CI/CD configuration present")
        else:
            eng_reasons.append("⚠️ CI/CD pipeline not configured")
            
        # H3: Gitignore (5 pts)
        if structure.get("has_gitignore"):
            eng_current += 5
            eng_reasons.append("✅ .gitignore detected")
        else:
            eng_reasons.append("❌ .gitignore file is missing")
            weaknesses.append(".gitignore file is missing")
            
        score += eng_current
        breakdown["Engineering Standards"] = create_category(
            "Engineering Standards", eng_current, 20, eng_reasons, 
            "Initialize a test suite and ensure version control excludes binaries."
        )

        # --- 5. Tech Stack & Complexity (Max 20 pts) ---
        tech_current = 0
        tech_reasons = []
        
        langs = stack.get("languages", [])
        if len(langs) > 1:
             tech_current += 10
             tech_reasons.append(f"✅ Multi-language architecture ({len(langs)})")
        elif len(langs) == 1:
             tech_current += 5
             tech_reasons.append("✅ Single language architecture")
        
        if len(stack.get("detected_extensions", [])) > 3:
             tech_current += 10
             tech_reasons.append("✅ Varied asset types detected")
        else:
             tech_current += 5
             
        score += tech_current
        breakdown["Tech Stack"] = create_category(
            "Tech Stack", tech_current, 20, tech_reasons, 
            "Demonstrate complexity through diverse tooling or asset management."
        )

        # Determine Level
        level = "Beginner"
        if score >= 85:
            level = "Pro"
        elif score >= 65:
            level = "Advanced"
        elif score >= 40:
             level = "Intermediate"
        
        # Calculate Health Flags
        health_flags = self._calculate_health_flags(structure, activity)
        
        # Calculate Score Simulation
        simulation = self._calculate_score_simulation(score, weaknesses)
             
        return {
            "total_score": score,
            "level": level,
            "breakdown": breakdown,
            "weaknesses": list(set(weaknesses)), # Remove dupes
            "flags": health_flags,
            "simulation": simulation
        }

    def _calculate_score_simulation(self, current_score: int, weaknesses: List[str]) -> Dict[str, Any]:
        """
        Simulates potential score improvements based on fixing specific weaknesses.
        Returns the new simulated score and the top 3 high-impact actions.
        """
        potential_gain = 0
        impacts = []
        
        # Define Point Deltas for specific fixes
        deltas = {
            "CRITICAL: Missing README.md": {"points": 20, "label": "Create comprehensive README documentation"},
            "README.md file is absent": {"points": 20, "label": "Create comprehensive README documentation"},
            "Documentation omits 'Usage' or 'Installation' steps": {"points": 10, "label": "Document installation and usage steps"},
            "No automated tests detected": {"points": 15, "label": "Implement automated test suite"},
            "Testing framework not detected": {"points": 15, "label": "Implement automated test suite"},
            "Missing standard folders (e.g., src, app, utils)": {"points": 10, "label": "Structure code into modular directories (src/)"},
            "Standard architecture folders (src, app, utils) not detected": {"points": 10, "label": "Structure code into modular directories (src/)"},
            "Commit messages lack semantic prefixes (feat:, fix:)": {"points": 10, "label": "Adopt semantic commit message convention"},
            "Commit messages do not follow semantic conventions (e.g., feat:, fix:)": {"points": 10, "label": "Adopt semantic commit message convention"},
            "Missing .gitignore (security/cleanliness risk)": {"points": 5, "label": "Add .gitignore to exclude build artifacts"},
            ".gitignore file is missing": {"points": 5, "label": "Add .gitignore to exclude build artifacts"}
        }
        
        for w in weaknesses:
            if w in deltas:
                d = deltas[w]
                potential_gain += d["points"]
                impacts.append({
                    "action": d["label"],
                    "points_gain": f"+{d['points']}"
                })
        
        # Cap score at 100
        simulated_score = min(100, current_score + potential_gain)
        
        # Sort impacts by points descending and take top 3
        top_impacts = sorted(impacts, key=lambda x: int(x["points_gain"].replace("+", "")), reverse=True)[:3]
        
        return {
            "current_score": current_score,
            "potential_score": simulated_score,
            "points_gap": simulated_score - current_score,
            "top_improvements": top_impacts
        }

    def _calculate_health_flags(self, structure: Dict[str, Any], activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates specific boolean health flags for the repository.
        """
        flags = {}
        
        # 1. Missing README
        flags["missing_readme"] = {
            "value": not structure.get("has_readme", False),
            "description": "Documentation entry point (README.md) is missing."
        }
        
        # 2. No Tests
        flags["no_tests"] = {
            "value": not structure.get("has_tests", False),
            "description": "No test configuration or test files identified."
        }
        
        # 3. Inactive (6 months)
        latest_str = activity.get("latest_commit")
        is_inactive = False
        if latest_str:
            try:
                # Basic ISO parsing - assuming UTC from GitHub or similar
                # Remove Z if present for fromisoformat in older pythons, though 3.7+ handles it usually
                latest_date = datetime.fromisoformat(latest_str.replace("Z", "+00:00"))
                days_diff = (datetime.now(latest_date.tzinfo) - latest_date).days
                if days_diff > 180:
                    is_inactive = True
            except ValueError:
                pass # Fail safe
        
        flags["is_inactive"] = {
            "value": is_inactive,
            "description": "No contribution activity recorded in the last 180 days."
        }

        # 4. Dump / Single Commit
        commit_count = activity.get("analyzed_commit_count", 0)
        flags["is_dump"] = {
            "value": commit_count <= 1,
            "description": "Entire codebase appears committed in a single transaction."
        }

        # 5. Overengineered (Too many folders for few files)
        file_count = structure.get("file_count", 0)
        folder_count = structure.get("folder_count", 0)
        is_overengineered = (file_count < 10 and folder_count > 4)
        flags["is_overengineered"] = {
            "value": is_overengineered,
            "description": "Directory nesting depth exceeds typical norms for project size."
        }

        # 6. Empty / Placeholder
        is_empty = file_count <= 2
        flags["is_empty"] = {
            "value": is_empty,
            "description": "Repository content is minimal or placeholder-only."
        }
        
        # Calculate Confidence Score
        confidence = self._calculate_confidence(structure, activity)
        flags["confidence_score"] = confidence

        return flags

    def _calculate_confidence(self, structure: Dict[str, Any], activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines how confident the system is in the score based on data availability.
        """
        commits = activity.get("analyzed_commit_count", 0)
        active_days = activity.get("unique_active_days", 0)
        file_count = structure.get("file_count", 0)
        has_readme = structure.get("has_readme", False)
        
        level = "High"
        reason = "Sufficient data points across history and structure."
        
        # Logic Hierarchy (Low overrides Medium)
        if commits < 3 or file_count < 3:
            level = "Low"
            reason = "Insufficient data: Repository has too few files or commits for reliable analysis."
        elif not has_readme:
             level = "Medium"
             reason = "Medium confidence: Missing documentation limits intent analysis."
        elif active_days < 2 and commits > 5:
            level = "Medium"
            reason = "Medium confidence: Activity compressed into single day reduces behavioral insights."
            
        return {
            "level": level,
            "description": reason
        }
