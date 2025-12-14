# Why Transparency Improves Trust in AI Evaluations
## The Black Box Problem
Traditional AI scoring models often function as "black boxes"—outputting a number (e.g., "72/100") without explanation. This creates friction:
1.  **Skepticism**: Students doubt the validity of the score ("Did it just hallucinate?").
2.  **Confusion**: Users don't know *what* to fix to improve.
3.  **Rejection**: Recruiters hesitate to trust a score they can't verify.

## The Glass Box Solution
Repository Mirror adopts a "Glass Box" engineering philosophy.

### 1. Deterministic Signals > Probabilistic Guesses
By exposing the specific signals that triggered points (e.g., "Gained 5 pts for having .gitignore"), we prove the model is grounded in reality.
*   **Result**: Users trust they are being graded on *their work*, not an AI's whim.

### 2. Actionable Feedback Loop
Transparency converts simple grading into **mentorship**.
*   *Opaque*: "Your score is low." (User feels bad)
*   *Transparent*: "You lost 5 points because your root directory has 15 files." (User takes action)

### 3. Auditable Fairness
When the scoring logic is visible:
*   Users can verify fairness ("Okay, I *did* miss the tests").
*   Biases are harder to hide (e.g., if we accidentally penalized a specific language, the breakdown would reveal it immediately).

## Implementation in Methodology
We display the exact math:
`Score = Structure(20) + Docs(20) + Hygiene(20) + Standards(20) + Stack(20)`
Each category explicitly lists **Reasons** (✅/❌) and **Hints**.

Transparency isn't just a UI feature; it is the core ethical requirement for any automated evaluation system.
