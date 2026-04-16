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
        
        res = predict_student_outcome(data)
        
        # Mapped keys to match result.html requirements
        prediction = {
            "projected_gpa": res["projected_gpa"],
            "projected_gpa_range": res["projected_gpa_range"],
            "risk_score": res["risk_score"],
            "burnout_probability": res["burnout_rate"], # This fills the battery!
            "recommendations": res["recommendations"]
        }
        
        return render_template("result.html", student=data, prediction=prediction)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/chat", methods=["POST"])
def chat():
    # ... (Keep your existing Chat route code, it is working well!) ...
    pass

if __name__ == "__main__":
    # Port 5001 avoids the macOS AirPlay conflict
    app.run(host="0.0.0.0", port=5001, debug=True)
