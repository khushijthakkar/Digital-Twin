def predict_student_outcome(data):
    old_gpa = data.get('current_gpa', 0.0)
    old_credits = data.get('total_credits_earned', 0.0)
    
    semester_points = sum(g * c for g, c in zip(data.get('grades', []), data.get('credits', [])))
    semester_credits = sum(data.get('credits', []))
    
    total_points = (old_gpa * old_credits) + semester_points
    total_sum_credits = old_credits + semester_credits
    
    final_gpa = total_points / total_sum_credits if total_sum_credits > 0 else old_gpa
    gpa_range_str = f"{max(0, final_gpa-0.05):.2f} - {min(4.0, final_gpa+0.05):.2f}"

    return {
        "projected_gpa": f"{final_gpa:.2f}",
        "projected_gpa_range": gpa_range_str,
        "risk_score": 15 if final_gpa >= 3.0 else 45,
        "burnout_rate": int((data.get('work_hours', 0) * 2.2) + (data.get('stress', 5) * 4)),
        "advice": "Excellent trajectory! Your GPA is showing growth." if final_gpa > old_gpa else "Solid standing."
    }
