# Limitations & Disclaimer

**Repository Mirror** analyzes software repositories using heuristic patterns derived from industry best practices. While highly accurate for assessing architectural discipline and workflow maturity, it has inherent limitations.

## 1. Scope of Evaluation
The system evaluates **repository health**, not executing functionality.
*   **What we DO measure:** Modularity, documentation quality, testing coverage, commit hygiene, and configuration standards.
*   **What we DO NOT measure:** Runtime bugs, algorithm efficiency, business logic correctness, or UI/UX experience.
*   **Implication:** A project may score poorly (e.g., "Beginner") due to poor structure even if it contains brilliant algorithms. Conversely, a structurally perfect project may still fail to run.

## 2. Platform constraints
The analysis is limited to metadata available via the GitHub API. 
*   Heavy "Mono-repos" may be penalized for complexity.
*   Projects relying on external/private submodules may appear incomplete.

## 3. Heuristic Bias
Scoring relies on deterministic proxies for quality (e.g., "Has a `tests` folder").
*   **Risk:** It is possible to "game" the system by creating empty folders or generating automated commits.
*   **Mitigation:** The system flags suspicious patterns (e.g., "Bus Factor" alerts), but human review is always required to verify intent.

## 4. Usage Guidance
**This tool is a signal, not a decision.**
*   **For Recruiters:** Use the score to filter candidates *in*, not out. Use the "Roadmap" as a conversation starter during interviews.
*   **For Students:** Use the feedback to professionalize your work. A high score means your code is "Review Ready", not necessarily that you are hired.

*Repository Mirror does not replace the judgement of a Senior Engineer. It optimizes their time.*
