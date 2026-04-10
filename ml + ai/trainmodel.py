import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import numpy as np

def train_brain():
    
    df_src = pd.read_csv('data.csv')
    
    data = pd.DataFrame()
    data['current_gpa'] = (df_src['exam_score'] / 25.0).clip(0, 4.0)
    data['failed_courses'] = df_src['exam_score'].apply(lambda x: 1 if x < 40 else 0)
    data['retaken_courses'] = df_src['exam_score'].apply(lambda x: 1 if x < 55 else 0)
    data['work_hours_per_week'] = df_src['part_time_job'].apply(lambda x: 15 if x == 'Yes' else 0)
    data['stress_level'] = (11 - df_src['mental_health_rating']).clip(1, 10)
    data['sleep_hours'] = df_src['sleep_hours']
    data['semester_difficulty'] = (df_src['age'] % 5) + 1
    data['extracurricular_load'] = df_src['extracurricular_participation'].apply(lambda x: 3 if x == 'Yes' else 1)

    data['projected_gpa'] = (data['current_gpa'] + np.random.normal(0, 0.1, len(df_src))).clip(0, 4.0)
    data['risk_score'] = (data['stress_level'] * 8).clip(0, 100)
    data['burnout_probability'] = (data['stress_level'] * 7 + (8 - data['sleep_hours']) * 5).clip(0, 100)

    X = data[['current_gpa', 'failed_courses', 'retaken_courses', 'work_hours_per_week', 
             'stress_level', 'sleep_hours', 'semester_difficulty', 'extracurricular_load']]

    bundle = {
        'gpa_model': LinearRegression().fit(X, data['projected_gpa']),
        'risk_model': LinearRegression().fit(X, data['risk_score']),
        'burnout_model': LinearRegression().fit(X, data['burnout_probability'])
    }

    joblib.dump(bundle, 'academic_twin_model.pkl')
    print("✅ Model trained successfully.")


if __name__ == "__main__":
    train_brain()
