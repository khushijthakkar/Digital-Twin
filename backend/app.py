import os
import json
from flask import Flask, render_template, request, jsonify
from model import predict_student_outcome
import anthropic

app = Flask(__name__)
# API setup remains untouched
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/simulator")
def index():
    return render_template("index.html")

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    try:
        # 1. Extract raw credit data and identify semester
        raw_credits = [float(c) for c in request.form.getlist("credits[]") if c]
        total_semester_credits = sum(raw_credits)
        semester_type = request.form.get("semester", "Fall")

        # 2. Build the data dictionary for the model
        data = {
            "student_name": request.form.get("student_name", "Student"),
            "major": request.form.get("major", "Information Technology"),
            "semester": semester_type,
            "current_gpa": float(request.form.get("current_gpa", 0)),
            "total_credits_earned": float(request.form.get("total_credits_earned", 0)),
            "grades": [float(g) for g in request.form.getlist("grades[]") if g],
            "credits": raw_credits,
            "work_hours": float(request.form.get("work_hours", 0)),
            "stress": float(request.form.get("stress", 5)),
            "course_names": request.form.getlist("course_names[]"),
            "target_gpa": float(request.form.get("target_gpa", 0)) if request.form.get("target_gpa") else None,
            "sleep_hours": float(request.form.get("sleep_hours", 7)),
        }
        
        # 3. Run prediction logic
        res = predict_student_outcome(data)
        
        # 4. Map keys for result.html and burnout battery
        prediction = {
            "projected_gpa": res.get("projected_gpa", 0.0),
            "projected_gpa_range": res.get("projected_gpa_range", "N/A"),
            "risk_score": res.get("risk_score", 0),
            "burnout_probability": res.get("burnout_rate", 0),
            "recommendations": res.get("recommendations", [])
        }

        # 5. Logic for the Caution Box warning (UCF Limits: 15 Fall/Spring, 8 Summer)
        warning_msg = None
        if "Summer" in semester_type and total_semester_credits > 8:
            warning_msg = f"CREDIT OVERLOAD: You are taking {int(total_semester_credits)} credits. Summer max is 8!"
        elif ("Fall" in semester_type or "Spring" in semester_type) and total_semester_credits > 15:
            warning_msg = f"CREDIT OVERLOAD: You are taking {int(total_semester_credits)} credits. Fall/Spring max is 15!"
        
        return render_template("result.html", student=data, prediction=prediction, warning=warning_msg)

    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/chat", methods=["POST"])
def chat():
    # Chat logic remains exactly as you have it
    pass

if __name__ == "__main__":
    # Standard Flask port
    app.run(host="0.0.0.0", port=5000, debug=True)
