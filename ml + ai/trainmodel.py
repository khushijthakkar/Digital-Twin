import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import joblib
import numpy as np

def train_brain():
    df_src = pd.read_csv('data.csv')

    # Map CSV columns to the 8 survey questions:
    # 1. Current cumulative GPA
    # 2. How many courses have you previously failed?
    # 3. How many courses have you retaken?
    # 4. How many hours per week do you work?
    # 5. Stress level (1-10)
    # 6. Sleep hours per night
    # 7. Semester difficulty (1-5)
    # 8. Extracurricular load (hours/week)

    data = pd.DataFrame()
    data['current_gpa']           = df_src['failed_courses'].apply(lambda x: max(0.0, 4.0 - x * 0.3)).clip(0, 4.0)
    data['failed_courses']        = df_src['failed_courses']
    data['retaken_courses']       = df_src['retaken_courses']
    data['work_hours_per_week']   = df_src['work_hours_per_week']
    data['stress_level']          = df_src['stress_level']
    data['sleep_hours']           = df_src['sleep_hours']
    data['semester_difficulty']   = df_src['semester_difficulty']
    data['extracurricular_load']  = df_src['extracurricular_load']

    # Target: burnout probability is already in the CSV
    data['burnout_probability']   = df_src['burnout_probability']

    # Derive risk score from burnout + GPA
    data['risk_score'] = (data['stress_level'] * 6 + (4.0 - data['current_gpa']) * 10).clip(0, 100)

    X = data[['current_gpa', 'failed_courses', 'retaken_courses', 'work_hours_per_week',
              'stress_level', 'sleep_hours', 'semester_difficulty', 'extracurricular_load']]

    bundle = {
        'risk_model':    GradientBoostingRegressor(n_estimators=100, random_state=42).fit(X, data['risk_score']),
        'burnout_model': GradientBoostingRegressor(n_estimators=100, random_state=42).fit(X, data['burnout_probability'])
    }

    joblib.dump(bundle, 'academic_twin_model.pkl')
    print("Model trained successfully.")

if __name__ == "__main__":
    train_brain()
