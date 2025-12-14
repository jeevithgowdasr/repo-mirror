from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, List
import logging
from urllib.parse import urlparse

from app.services.github_service import GitHubService
from app.services.scoring_service import ScoringService
from app.services.summary_service import SummaryService
from app.services.roadmap_service import RoadmapService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... (Previous code)

app = FastAPI(
    title="Repository Mirror API",
    description="AI-powered GitHub repository analyzer and mentor.",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, best to list specific domains like ["https://your-frontend.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# (Services init...)

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

# ... (Rest of the code)
from app.services.report_service import ReportService

# Services Init
github_service = GitHubService()
scoring_service = ScoringService(github_service)
summary_service = SummaryService()
roadmap_service = RoadmapService()
report_service = ReportService()

class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl

class AnalyzeResponse(BaseModel):
    github_url: str
    owner: str
    repo_name: str
    total_score: int
    level: str
    summary: Dict[str, str]
    roadmap: List[str]
    details: Dict[str, Any]
    report: str

def parse_github_url(url: str) -> tuple[str, str]:
    """
    Parses a GitHub URL to extract owner and repo name.
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub URL format. Expected 'https://github.com/owner/repo'")
    
    owner = path_parts[0]
    repo = path_parts[1]
    
    if repo.endswith(".git"):
        repo = repo[:-4]
        
    return owner, repo

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest):
    """
    Analyzes a GitHub repository and provides a score, mentor evaluation, and roadmap.
    """
    url_str = str(request.repo_url)
    logger.info(f"Received analysis request for: {url_str}")
    
    try:
        owner, repo_name = parse_github_url(url_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 1. Analyze Core Metrics
    try:
        repo_data = scoring_service.analyze_repository(owner, repo_name)
    except Exception as e:
        logger.error(f"Error fetching repo data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch repository data from GitHub.")

    if "error" in repo_data:
         raise HTTPException(status_code=404, detail=repo_data["error"])

    # 2. Calculate Score
    score_result = scoring_service.calculate_score(repo_data)
    
    score = score_result["total_score"]
    level = score_result["level"]
    weaknesses = score_result["weaknesses"]
    breakdown = score_result["breakdown"]
    flags = score_result.get("flags", {})
    simulation = score_result.get("simulation", {})

    # 3. Generate Evaluation Summary
    summary_dict = summary_service.generate_evaluation(score, level, weaknesses)

    # 4. Generate Improvement Roadmap
    roadmap = roadmap_service.generate_roadmap(weaknesses)

    # 5. Generate Full Audit Report
    report_content = report_service.generate_audit_report(url_str, score_result, summary_dict["recruiter"], roadmap)

    return AnalyzeResponse(
        github_url=url_str,
        owner=owner,
        repo_name=repo_name,
        total_score=score,
        level=level,
        summary=summary_dict,
        roadmap=roadmap,
        details={
            "breakdown": breakdown,
            "weaknesses": weaknesses,
            "flags": flags,
            "simulation": simulation,
            "repo_stats": repo_data
        },
        report=report_content
    )

class CompareRequest(BaseModel):
    repo_url_1: HttpUrl
    repo_url_2: HttpUrl

class CompareResponse(BaseModel):
    winner: str
    summary: str
    repo_1: Dict[str, Any]
    repo_2: Dict[str, Any]

@app.post("/compare", response_model=CompareResponse)
async def compare_repos(request: CompareRequest):
    """
    Compares two repositories and identifies the stronger one based on engineering standards.
    """
    urls = [str(request.repo_url_1), str(request.repo_url_2)]
    results = []

    for url in urls:
        try:
            owner, repo_name = parse_github_url(url)
            repo_data = scoring_service.analyze_repository(owner, repo_name)
            
            if "error" in repo_data:
                 results.append({"error": repo_data["error"], "name": repo_name, "score": 0})
                 continue
                 
            score_res = scoring_service.calculate_score(repo_data)
            results.append({
                "name": repo_name,
                "owner": owner,
                "score": score_res["total_score"],
                "level": score_res["level"],
                "flags": score_res.get("flags", {}),
                "weaknesses": score_res["weaknesses"]
            })
        except Exception as e:
            logger.error(f"Error comparing {url}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze {url}")

    if len(results) != 2:
        raise HTTPException(status_code=400, detail="Could not analyze both repositories.")

    r1 = results[0]
    r2 = results[1]

    # Determine Winner
    if r1["score"] > r2["score"]:
        winner = r1["name"]
        diff = r1["score"] - r2["score"]
        better = r1
        worse = r2
    elif r2["score"] > r1["score"]:
        winner = r2["name"]
        diff = r2["score"] - r1["score"]
        better = r2
        worse = r1
    else:
        winner = "Draw"
        diff = 0
        better = r1 # Arbitrary for summary generation
        worse = r2

    # Generate Concise Summary
    if winner == "Draw":
        summary = f"Both repositories are evenly matched with a score of {r1['score']}. They exhibit similar engineering maturity levels."
    else:
        reasons = []
        # Check specific flags for the 'Why'
        if not better['flags'].get('no_tests', {}).get('value') and worse['flags'].get('no_tests', {}).get('value'):
            reasons.append("includes automated tests")
        if not better['flags'].get('missing_readme', {}).get('value') and worse['flags'].get('missing_readme', {}).get('value'):
            reasons.append("has better documentation")
        
        # Fallback to general score
        reason_text = f"superior engineering standards ({', '.join(reasons)})" if reasons else "overall better structural hygiene"
        
        summary = (
            f"**{winner}** is the stronger repository (Score: {better['score']} vs {worse['score']}). "
            f"It outperforms **{worse['name']}** due to {reason_text}."
        )

    return CompareResponse(
        winner=winner,
        summary=summary,
        repo_1=r1,
        repo_2=r2
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Repository Mirror API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
