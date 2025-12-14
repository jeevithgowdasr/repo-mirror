from typing import List, Dict, Any

class SummaryService:
    def generate_evaluation(self, score: int, level: str, weaknesses: List[str]) -> Dict[str, str]:
        """
        Generates dual-view evaluations:
        1. Student View: Educational and growth-oriented.
        2. Recruiter View: Signal-oriented and risk-focused.
        """
        weakness_text = weaknesses[0].lower() if weaknesses else "minor details"
        
        # --- Recruiter View (Hiring Signal) ---
        if level == "Pro":
            recruiter_text = (
                f"✅ **Signal: Strong Hire.** This candidate demonstrates production-ready capability ({score}/100). "
                f"The repository adheres to rigorous industry standards. "
                "The work suggests a developer who can integrate into a team with minimal onboarding."
            )
        elif level == "Advanced":
            recruiter_text = (
                f"⚠️ **Signal: Potential Hire.** The submission is solid ({score}/100) but lacks final production polish. "
                f"Issues with {weakness_text} prevent top-tier classification. "
                "Suitable for mid-level roles, but probe on architectural decisions during interview."
            )
        elif level == "Intermediate":
            recruiter_text = (
                f"🛑 **Signal: High Risk.** Foundational knowledge is present ({score}/100), but professional standards are missing. "
                f"Gaps in {weakness_text} suggest habit-forming is still in progress. "
                "Likely requires significant mentorship to reach production velocity."
            )
        else: # Beginner
            recruiter_text = (
                f"⛔ **Signal: Do Not Progress.** The submission ({score}/100) fails to meet baseline engineering expectations. "
                f"Deficiencies in {weakness_text} indicate a lack of familiarity with professional workflows. "
                "Not recommended for technical review."
            )

        # --- Student View (Growth Mindset) ---
        if level == "Pro":
            student_text = (
                f"🚀 **Outstanding work!** You are coding at a professional level ({score}/100). "
                "Your structure and habits are excellent. "
                f"To push for perfection, double-check your {weakness_text} and consider adding CI/CD pipelines if missing."
            )
        elif level == "Advanced":
            student_text = (
                f"💪 **Great job.** You are well above average ({score}/100), but there is a clear path to the next level. "
                f"Your logic is good, but your {weakness_text} is holding you back from a perfect score. "
                "Polish these edges to turn this project into a star portfolio piece."
            )
        elif level == "Intermediate":
            student_text = (
                f"🔧 **Good start, but needs structure.** You have written working code ({score}/100), but it's hard for others to read or maintain. "
                f"Your biggest opportunity for growth is fixing {weakness_text}. "
                "Focus on 'Clean Code' principles and file organization next."
            )
        else: # Beginner
            student_text = (
                f"🎓 **Learning Opportunity.** Right now, this project looks more like a scratchpad than a product ({score}/100). "
                f"Don't worry about complex algorithms yet—focus on the basics: {weakness_text}. "
                "Structure and documentation are just as important as the code itself."
            )

        return {
            "recruiter": recruiter_text,
            "student": student_text
        }
