# Repository Mirror – AI-Based GitHub Code Evaluator

**Repository Mirror** is an intelligent auditing tool designed to evaluate student GitHub repositories against industry standards. It generates a deterministic score, a recruiter-style evaluation, and a strict, actionable roadmap for improvement.

---

## 🚀 The Problem

Student developers often build impressive projects but fail to present them professionally. Common issues include:
*   ❌ **Poor Structure**: Flat directories and lack of modularity.
*   ❌ **Missing Documentation**: No README or vague instructions.
*   ❌ **Inconsistent Activity**: "Code dumps" instead of a healthy commit history.
*   ❌ **Zero Testing**: Lack of unit or integration tests.

For recruiters and hiring managers, these are immediate red flags. **Repository Mirror** acts as an automated mentor, identifying these gaps before a human reviewer does.

## 💡 Why This Matters

In a competitive job market, code quality > code quantity. This tool bridges the gap between academic coding and production engineering by forcing students to adhere to best practices like proper git hygiene, testing, and documentation.

---

## 🏗️ System Architecture

The system is built as a modular FastAPI backend service:

1.  **GitHub Service**: Securely fetches metadata, file trees, and commit history via the GitHub REST API (with rate limit handling).
2.  **Scoring Engine**: A deterministic rule-based engine that evaluates the repository across 5 key dimensions.
3.  **Mentor Agent**: Generates a ruthless but helpful summary using template-based logic (simulating a senior engineer's review).
4.  **Roadmap Generator**: Maps specific weaknesses to actionable steps (e.g., "Missing tests" -> "Setup Pytest").

---

## 📊 Scoring Methodology (0-100)

The score is calculated based on **5 pillars** (20 points each):

1.  **Code Organization**: Folder structure depth, file separation, and modularity.
2.  **Documentation**: Presence and quality of `README.md`.
3.  **Commit Consistency**: Commit frequency, volume, and spread over time.
4.  **Review Readiness**: Presence of test suites (`tests/` folder).
5.  **Tech Stack & Relevance**: Diversity of languages and use of standard file extensions.

**Levels:**
*   🏆 **Pro (80-100)**: Production-ready.
*   🥇 **Advanced (60-79)**: Solid, needs polish.
*   🥈 **Intermediate (40-59)**: Functional but messy.
*   🥉 **Beginner (0-39)**: Needs fundamental restructuring.

---

## 🛠️ Technologies Used

*   **Backend**: Python 3.9+, FastAPI
*   **API Client**: Requests (with Session management)
*   **Validation**: Pydantic
*   **Environment**: Python-dotenv
*   **Server**: Uvicorn

---

## ⚡ How to Run Locally

### Prerequisites
*   Python 3.9+
*   A GitHub Personal Access Token (for higher rate limits)

### Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/repository-mirror.git
    cd repository-mirror
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    GITHUB_TOKEN=your_github_token_here
    ```

5.  **Run the Server**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

---

## 🧪 Sample Usage

**Request:**
`POST /analyze`
```json
{
  "repo_url": "https://github.com/octocat/Hello-World"
}
```

**Response:**
```json
{
  "total_score": 45,
  "level": "Intermediate",
  "summary": "This repository demonstrates foundational knowledge (45/100) but falls short of professional software engineering standards. The evident gaps in no testing structure detected suggest a need for more rigorous development habits.",
  "roadmap": [
    "Zero Tolerance for Untested Code: Set up pytest (or equivalent). Write unit tests for your core logic.",
    "Refactor Architecture: Move your source code into a `src` or `app` directory.",
    "Show Consistency: Coding is a habit, not a sprint. Commit code on at least 3 separate days this week."
  ]
}
```

---

## 🔮 Future Product Roadmap

1.  **Resume-to-GitHub Matching**: Upload a resume PDF and get a "Credibility Score" based on whether your repos match your claimed skills.
2.  **Classroom Dashboard**: A teacher view to track the engineering growth of an entire cohort over a semester.
3.  **Mentor Feedback Loops**: Allow human mentors to annotate the automated report with specific code reviews.
4.  **Open Source Contribution Scoring**: Bonus points for merged PRs to external major repositories (e.g., React, Django).
5.  **Multi-Platform Support**: Expand beyond GitHub to support GitLab and Bitbucket repositories.
6.  **LLM Fine-Tuning**: Train a custom small-language model (SLM) on 10,000 "Staff Engineer" code reviews for hyper-realistic feedback.

---
*Built with ❤️ for better code.*
