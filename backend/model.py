import joblib
import os
import numpy as np

GRADE_MAP = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "D": 1.0, "F": 0.0
}

def calculate_gpa(current_gpa, total_credits_earned, grades, credits):
    semester_points = 0.0
    semester_credits = 0.0

    for grade, credit in zip(grades, credits):
        if credit > 0:
            semester_points += grade * credit
            semester_credits += credit

    prior_total_points = current_gpa * total_credits_earned
    total_points = prior_total_points + semester_points
    total_credits = total_credits_earned + semester_credits

    if total_credits == 0:
        return current_gpa

    new_gpa = total_points / total_credits
    return max(0.0, min(4.0, new_gpa))

def predict_student_outcome(data):
    current_gpa = data.get('current_gpa', 0.0)
    total_credits_earned = data.get('total_credits_earned', 0.0)
    grades = data.get('grades', [])
    credits = data.get('credits', [])
    work_hours = data.get('work_hours', 0)
    stress = data.get('stress', 5)
    sleep = data.get('sleep_hours', 7) 

    final_gpa = calculate_gpa(current_gpa, total_credits_earned, grades, credits)
    gpa_range_str = f"{max(0.0, final_gpa - 0.05):.2f} - {min(4.0, final_gpa + 0.05):.2f}"

    model_path = 'academic_twin_model.pkl'
    
    # Initialize these so they always exist
    risk_score = 0
    burnout_rate = 0
    use_fallback = False 

    if os.path.exists(model_path):
        try:
            bundle = joblib.load(model_path)
            X = np.array([[current_gpa, data.get('failed', 0), 0, work_hours, stress, sleep, 3, 0]])
            risk_score = int(bundle['risk_model'].predict(X)[0])
            burnout_rate = int(bundle['burnout_model'].predict(X)[0])
        except:
            use_fallback = True
    else:
        use_fallback = True

    if use_fallback:
        # Penalty for sleep under 7 hours (10% increase per hour missing)
        sleep_penalty = max(0, (7 - sleep) * 10) 
        burnout_rate = int((work_hours * 1.5) + (stress * 5) + sleep_penalty)
        
        # Risk scales based on how far you are from a 4.0
        gpa_deficit = max(0, 4.0 - final_gpa) * 15
        risk_score = int(gpa_deficit + (stress * 3))

    # Safety clamping
    risk_score = max(5, min(95, risk_score))
    burnout_rate = max(5, min(98, burnout_rate))

    return {
        "projected_gpa": f"{final_gpa:.2f}",
        "projected_gpa_range": gpa_range_str,
        "risk_score": risk_score,
        "burnout_rate": burnout_rate,
        "advice": "Growth Mode" if final_gpa > current_gpa else "Maintenance Mode"
    }
