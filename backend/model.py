def calculate_gpa(current_gpa, total_credits_earned, grades, credits):
    # Calculate points already earned
    prior_total_points = current_gpa * total_credits_earned
    
    # Calculate new points from this semester
    semester_points = sum(g * c for g, c in zip(grades, credits))
    semester_credits = sum(credits)
    
    # Combined totals
    total_points = prior_total_points + semester_points
    total_credits = total_credits_earned + semester_credits
    
    if total_credits == 0:
        return current_gpa
        
    return total_points / total_credits

def predict_student_outcome(data):
    current_gpa = data.get('current_gpa', 0.0)
    total_credits_earned = data.get('total_credits_earned', 0.0)
    grades = data.get('grades', [])
    credits = data.get('credits', [])
    work_hours = data.get('work_hours', 0)
    stress = data.get('stress', 5)
    
    final_gpa = calculate_gpa(current_gpa, total_credits_earned, grades, credits)
    
    # Formatting to 2 decimal places ensures you see 3.77 instead of 3.8
    gpa_str = f"{final_gpa:.2f}"
    gpa_range_str = f"{max(0.0, final_gpa - 0.05):.2f} - {min(4.0, final_gpa + 0.05):.2f}"

    # Risk and Burnout Logic
    work_penalty = max(0, (work_hours - 15) * 1.5)
    stress_penalty = max(0, (stress - 5) * 5)
    burnout_rate = max(5, min(95, int(work_penalty + stress_penalty + (sum(credits) * 2))))
    
    risk_score = 10 if final_gpa >= current_gpa else 40
    risk_score = max(5, min(95, risk_score + int(stress_penalty)))

    # Advice Logic
    if final_gpa >= current_gpa:
        advice = f"Charging On! Your GPA is trending up to {gpa_str}. Balancing {work_hours}h of work is standard professional prep."
    else:
        advice = "The data shows a slight dip. Consider utilizing SARC tutoring to protect your target GPA."

    return {
        "projected_gpa": gpa_str,
        "projected_gpa_range": gpa_range_str,
        "risk_score": risk_score,
        "burnout_rate": burnout_rate,
        "recommendations": [advice]
    }
