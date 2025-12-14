from typing import List

class RoadmapService:
    def generate_roadmap(self, weaknesses: List[str]) -> List[str]:
        """
        Generates an actionable, strict improvement roadmap based on specific weaknesses.
        """
        roadmap = []
        
        # Default strict advice if list is empty or minimal
        if not weaknesses:
            return [
                "Maintain this standard by automating your CI/CD pipeline.",
                "Start contributing to larger open-source projects to test your skills at scale.",
                "Implement strict linting rules (e.g., flake8, ruff) to enforce style consistency.",
                "Add comprehensive API documentation using tools like Swagger/OpenAPI.",
                "Explore containerization (Docker) to ensure environment reproducibility."
            ]

        for weakness in weaknesses:
            w_lower = weakness.lower()
            
            if "readme" in w_lower:
                roadmap.append("Documentation First: Create a README.md immediately. Include installation steps, usage examples, and a clear project description. No code exists if it's not documented.")
                
            if "test" in w_lower:
                roadmap.append("Zero Tolerance for Untested Code: Set up pytest (or equivalent). Write unit tests for your core logic. Aim for at least 60% coverage before adding new features.")
                
            if "folder" in w_lower or "structure" in w_lower:
                roadmap.append("Refactor Architecture: Move your source code into a `src` or `app` directory. Separate implementation from configuration. Don't dump files in the root.")
                
            if "commit" in w_lower and "count" in w_lower:
                roadmap.append("Commit Granularity: Stop pushing massive updates. Break work into small, atomic commits. Each commit should handle ONE specific task or fix.")
                
            if "concentrated" in w_lower or "days" in w_lower:
                roadmap.append("Show Consistency: Coding is a habit, not a sprint. Commit code on at least 3 separate days this week. Prove you can maintain a project over time.")

        # Fill with general best practices if we have fewer than 5 items
        generic_advice = [
            "Clean Code Audit: Remove all commented-out code and unused imports. If you don't need it, delete it. That's what version control is for.",
            "Git Hygiene: Use a `.gitignore` file. Never commit virtual environments, system files, or secrets (API keys).",
            "Environment Management: Freeze your dependencies into a `requirements.txt` or `pyproject.toml`. Your project must run on another machine with one command.",
            "Linter Enforcement: format your code. Use `black` or `prettier` to automate formatting. Inconsistent style screams 'amateur'."
        ]
        
        needed = 5 - len(roadmap)
        if needed > 0:
            roadmap.extend(generic_advice[:needed])
            
        return roadmap[:7] # Cap at 7 items
