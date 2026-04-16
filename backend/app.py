import os
import json
from flask import Flask, render_template, request, jsonify
from model import predict_student_outcome
import anthropic

app = Flask(__name__)
# Leaving your original API setup exactly as it was
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
        # Merged data: includes your original fields + your friend's sleep_hours
        data = {
            "student_name": request.form.get("student_name", "Student"),
            "major": request.form.get("major", "Information Technology"),
            "semester": request.form.get("semester"),
            "current_gpa": float(request.form.get("current_gpa", 0)),
            "total_credits_earned": float(request.form.get("total_credits_earned", 0)),
            "grades": [float(g) for g in request.form.getlist("grades[]") if g],
            "credits": [float(c) for c in request.form.getlist("credits[]") if c],
            "work_hours": float(request.form.get("work_hours", 0)),
            "stress": float(request.form.get("stress", 5)),
            "course_names": request.form.getlist("course_names[]"),
            "target_gpa": float(request.form.get("target_gpa", 0)) if request.form.get("target_gpa") else None,
            "sleep_hours": float(request.form.get("sleep_hours", 7)),
        }
        
        # Runs the logic from your model.py
        res = predict_student_outcome(data)
        
        # Mapped keys to match result.html requirements
        # Added .get() to recommendations to prevent the 'recommendations' error crash
        prediction = {
            "projected_gpa": res.get("projected_gpa", 0.0),
            "projected_gpa_range": res.get("projected_gpa_range", "N/A"),
            "risk_score": res.get("risk_score", 0),
            "burnout_probability": res.get("burnout_rate", 0), # This fills the battery!
            "recommendations": res.get("recommendations", []) # Safely handles the missing key
        }
        
        return render_template("result.html", student=data, prediction=prediction)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/chat", methods=["POST"])
def chat():
    # ... (Keep your existing Chat route code, it is working well!) ...
    pass

if __name__ == "__main__":
    # Using port 5001 to avoid the macOS AirPlay/Control Center conflict
    app.run(host="0.0.0.0", port=5000, debug=True)
