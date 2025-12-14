import os
import requests
import logging
import time
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GitHubService:
    """
    Service to interact with GitHub REST API safely and securely.
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHubService with a token.
        If no token is provided, tries to load GITHUB_TOKEN from environment.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            logger.warning("GITHUB_TOKEN not found in environment variables. Rate limits will be restricted.")
            
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _handle_rate_limit(self, response: requests.Response):
        """
        Check for rate limit headers and sleep if necessary.
        This is a basic implementation. For production, consider using a task queue or more sophisticated backoff.
        """
        if response.status_code == 403 and "rate limit" in response.text.lower():
            # Check for reset time
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            current_time = int(time.time())
            sleep_time = reset_time - current_time + 1
            if sleep_time > 0:
                logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                return True
        return False

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Union[Dict, List]]:
        """
        Internal method to make GET requests with error handling and rate limit management.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            
            # Handle rate limiting (simple retry logic for demonstration)
            if response.status_code == 403:
                if self._handle_rate_limit(response):
                    # Retry once after sleeping
                    response = self.session.get(url, params=params)

            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as ignored:
            if response.status_code == 404:
                logger.error(f"Resource not found: {url}")
                return None
            logger.error(f"HTTP Error fetching {url}: {ignored}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_repo_metadata(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Fetch repository metadata (stars, forks, description, etc.)
        """
        return self._make_request(f"repos/{owner}/{repo}")

    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> Optional[Union[Dict, List]]:
        """
        Fetch file or directory contents.
        Returns a list of items if path is a directory, or file content dict if path is a file.
        """
        return self._make_request(f"repos/{owner}/{repo}/contents/{path}")

    def get_commit_history(self, owner: str, repo: str, page: int = 1, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch commit history with pagination.
        """
        params = {"page": page, "per_page": per_page}
        result = self._make_request(f"repos/{owner}/{repo}/commits", params=params)
        if isinstance(result, list):
            return result
        return []

    def get_languages(self, owner: str, repo: str) -> Optional[Dict[str, int]]:
        """
        Fetch languages used in the repository and their byte counts.
        """
        return self._make_request(f"repos/{owner}/{repo}/languages")

    def get_git_tree(self, owner: str, repo: str, branch: str = "main", recursive: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch the full git tree recursively.
        """
        recursive_flag = "1" if recursive else "0"
        return self._make_request(f"repos/{owner}/{repo}/git/trees/{branch}?recursive={recursive_flag}")

    def get_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """
        Fetch the content of the README.md file.
        """
        # GitHub API has a specialized endpoint for README
        data = self._make_request(f"repos/{owner}/{repo}/readme")
        if data and "content" in data:
            import base64
            try:
                return base64.b64decode(data["content"]).decode("utf-8")
            except Exception:
                return None
        return None

# Example usage (can be removed or moved to main.py):
if __name__ == "__main__":
    service = GitHubService()
    # Test with a public repo, e.g., 'octocat/Hello-World'
    # print(service.get_repo_metadata("octocat", "Hello-World"))
