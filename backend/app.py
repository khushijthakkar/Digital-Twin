import os
import json
from flask import Flask, render_template, request, jsonify
from model import predict_student_outcome
import anthropic

app = Flask(__name__)
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
            "current_gpa": float(request.form.get("current_gpa", 0)),
            "total_credits_earned": float(request.form.get("total_credits_earned", 0)),
            "grades": [float(g) for g in request.form.getlist("grades[]") if g],
            "credits": [float(c) for c in request.form.getlist("credits[]") if c],
            "work_hours": float(request.form.get("work_hours", 0)),
            "stress": float(request.form.get("stress", 5)),
            "target_gpa": float(request.form.get("target_gpa", 0)) if request.form.get("target_gpa") else None
        }
        res = predict_student_outcome(data)
        prediction = {
            "projected_gpa": res["projected_gpa"],
            "projected_gpa_range": res["projected_gpa_range"],
            "risk_score": res["risk_score"],
            "burnout_probability": res["burnout_rate"],
            "recommendations": [res["advice"]]
        }
        return render_template("result.html", student=data, prediction=prediction)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        body = request.get_json()
        question = body.get("question", "").strip()
        student = body.get("student", {})
        prediction = body.get("prediction", {})

        if not question:
            return jsonify({"error": "No question provided"}), 400

        grades = student.get("grades", [])
        credits = student.get("credits", [])
        courses = []
        for i, (g, c) in enumerate(zip(grades, credits)):
            letter = {4.0: "A", 3.0: "B", 2.0: "C", 1.0: "D", 0.0: "F"}.get(float(g), str(g))
            courses.append(f"  Course {i+1}: {letter} ({c} credits)")
        courses_text = "\n".join(courses) if courses else "  No courses entered"

        target_gpa = student.get("target_gpa")
        target_line = f"Target GPA Goal: {target_gpa}" if target_gpa else "Target GPA Goal: Not specified"

        system_prompt = f"""You are an academic advisor AI for a student's Digital Twin simulation. You have access to the student's full academic profile and simulation results. Answer scenario-based questions precisely, showing your calculations when relevant (e.g., GPA impact of failing a class, what grades are needed to hit a target GPA).

STUDENT PROFILE:
- Name: {student.get('student_name', 'Student')}
- Current Cumulative GPA: {student.get('current_gpa')}
- Total Credits Earned (before this semester): {student.get('total_credits_earned')}
- Work Hours Per Week: {student.get('work_hours')}
- Stress Level (1-10): {student.get('stress')}
- {target_line}

CURRENT SEMESTER COURSES:
{courses_text}

SIMULATION RESULTS:
- Projected GPA (after this semester): {prediction.get('projected_gpa')}
- GPA Range: {prediction.get('projected_gpa_range')}
- Academic Risk Score: {prediction.get('risk_score')}%
- Burnout Probability: {prediction.get('burnout_probability')}%

HOW TO CALCULATE GPA:
Cumulative GPA = (sum of grade points x credits for ALL courses ever taken) / total credits
When answering "what if I fail X", recalculate using 0.0 for that course grade.
When answering "what grades do I need", solve algebraically for the required GPA points.

Keep responses concise, friendly, truthful, and specific. Show math when doing GPA calculations. Always give a correct direct answer first, then the explanation.

IMPORTANT: Write response in plain conversational text only."""

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": question}]
        )

        return jsonify({"response": message.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
