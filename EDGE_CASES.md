# Edge Case Analysis for Repository Mirror

The following repository types represent "stress tests" for the automated scoring engine. Here is how the system interprets risks and handles anomalies.

---

## 1. Massive Monorepos (e.g., Turborepo / Nx Workspaces)
*   **The Scenario:** A single repository containing frontend, backend, and mobile apps in packages/ sub-folders.
*   **Risk:** The directory depth often exceeds 10 levels, and file counts are massive. This triggers the "Bad Organization" flags for depth and complexity.
*   **System Handling:**
    *   **Flag:** `Directory depth (>8 levels) falls outside standard range`.
    *   **Outcome:** The system penalizes the *Organization* score. This is intentional for the "Student/Junior" profile target, as beginners rarely maintain clean monorepos. However, the score remains valid for *complexity*.

## 2. "One-Shot" Framework Dumps (e.g., `create-react-app`)
*   **The Scenario:** A user runs a generator script and pushes the result in a single commit.
*   **Risk:** The repo looks "perfect" (tests exist, structure is standard), but the user did zero work.
*   **System Handling:**
    *   **Flag:** `Activity concentrated in single day` and `Commit count < 5`.
    *   **Outcome:** The **Commit Hygiene** score tanks. Even if the code is Pro-level, the project is flagged as a "Starter Template Dump" via the Bus Factor risk logic.

## 3. The "Forked" Repository
*   **The Scenario:** A student forks a popular repo (e.g., `facebook/react`) to their profile without changing anything.
*   **Risk:** The system scores it 100/100, falsely attributing "Senior" status to the student.
*   **System Handling:**
    *   **Current Limitation:** The system scores the *code*, not the *authorship*.
    *   **Mitigation:** The "Commit Hygiene" section analyzes recent activity. If the student hasn't contributed active commits to the fork, the **Recent Activity** and **Consistency** scores will be low, distinguishing it from an active project.

## 4. Documentation-Only Repos (e.g., "Awesome-Lists")
*   **The Scenario:** A repository that contains only `README.md` and links, with no code.
*   **Risk:** Fails checks for `src/` folders, tests, and CI/CD, resulting in a failing grade for a valid project.
*   **System Handling:**
    *   **Outcome:** Accurate "Low Engineering" score.
    *   **Reasoning:** Only appropriate. Repository Mirror evaluates *Engineering Proficiency* (Architecture, Testing, CI). A list of links—while useful—is not an engineering artifact that demonstrates hiring readiness.

## 5. "Dotfile" Configurations
*   **The Scenario:** A repo storing `.bashrc`, `.vimrc`, etc., in the root directory.
*   **Risk:** Triggers "Root Dumping" penalty because all files are at the top level.
*   **System Handling:**
    *   **Flag:** `High file concentration in root directory`.
    *   **Outcome:** Penalized for organization. This is acceptable behavior; dotfile repos are utility storage, not software products, and typically generally don't require "Architecture" scoring.

## 6. Legacy / Archived Spagetti Code
*   **The Scenario:** A 5-year-old PHP project with no folders, just 50 `.php` files in root.
*   **Risk:** Might have "working" logic but horrific structure.
*   **System Handling:**
    *   **Flags:** `Standard architecture folders not detected` + `Missing .gitignore` + `No CI/CD`.
    *   **Outcome:** The "Glass Box" scoring perfectly identifies this as "High Technical Debt". The Score (likely <40) accurately reflects that the code needs modernization before a team can work on it.
