import joblib
import os

# Grade letter to GPA 
GRADE_MAP = {
    "A":  4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B":  3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C":  2.0,
    "D":  1.0,
    "F":  0.0
}

def calculate_gpa(current_gpa, total_credits_earned, grades, credits):
    """
    Proper GPA calculation:
    1. Convert letter grades to grade points
    2. Multiply each grade point by its credit hours
    3. Sum all grade points from current semester
    4. Add to existing total grade points (current_gpa * total_credits_earned)
    5. Divide by total credits (old + new)
    """
    # Calculate grade points for this semester
    semester_points = 0.0
    semester_credits = 0.0

    for grade, credit in zip(grades, credits):
        if credit > 0:
            # grade values come in as numeric from the form
            semester_points += grade * credit
            semester_credits += credit

    #  total grade points from prior GPA
    prior_total_points = current_gpa * total_credits_earned

    # join old and new
    total_points = prior_total_points + semester_points
    total_credits = total_credits_earned + semester_credits

    if total_credits == 0:
        return current_gpa

    new_gpa = total_points / total_credits
    
    if new_gpa > 4.0:
        new_gpa = 4.0
    if new_gpa < 0.0:
        new_gpa = 0.0

    return new_gpa


def predict_student_outcome(data):
    current_gpa = data.get('current_gpa', 0.0)
    total_credits_earned = data.get('total_credits_earned', 0.0)
    grades = data.get('grades', [])
    credits = data.get('credits', [])
    work_hours = data.get('work_hours', 0)
    stress = data.get('stress', 5)
    sleep = data.get('sleep', 7)

    # Correct GPA calculation
    final_gpa = calculate_gpa(current_gpa, total_credits_earned, grades, credits)
    gpa_range_str = f"{max(0.0, final_gpa - 0.05):.2f} - {min(4.0, final_gpa + 0.05):.2f}"

    # trained ML models if available
    model_path = 'academic_twin_model.pkl'
    risk_score = 0
    burnout_rate = 0

    if os.path.exists(model_path):
        try:
            bundle = joblib.load(model_path)
            failed = data.get('failed', 0)
            retake = data.get('retake', 0)
            difficulty = data.get('difficulty', 3)
            extra = data.get('extra', 0)

            import numpy as np
            X = np.array([[current_gpa, failed, retake, work_hours,
                           stress, sleep, difficulty, extra]])

            risk_score = int(bundle['risk_model'].predict(X)[0])
            burnout_rate = int(bundle['burnout_model'].predict(X)[0])

            # clamp accordingly
            risk_score = max(0, min(100, risk_score))
            burnout_rate = max(0, min(100, burnout_rate))
        except Exception:
            # Fallback to rule-based if model fails
            risk_score = 15 if final_gpa >= 3.0 else 45
            burnout_rate = int((work_hours * 2.2) + (stress * 4))
            burnout_rate = max(0, min(100, burnout_rate))
    else:
        # Rule-based fallback
        risk_score = 15 if final_gpa >= 3.0 else 45
        burnout_rate = int((work_hours * 2.2) + (stress * 4))
        burnout_rate = max(0, min(100, burnout_rate))

    advice = "Excellent trajectory! Your GPA is showing growth." if final_gpa > current_gpa else "Solid standing. Keep up your current habits."

    return {
        "projected_gpa": f"{final_gpa:.2f}",
        "projected_gpa_range": gpa_range_str,
        "risk_score": risk_score,
        "burnout_rate": burnout_rate,
        "advice": advice
    }
