from flask import Flask, render_template, request
from model import predict_student_outcome

app = Flask(__name__)

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
            "stress": float(request.form.get("stress", 5))
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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
