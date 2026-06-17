# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import requests
import xgboost as xgb
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Apex Power Demand Forecasting API")

# Mount static folder
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

try:
    model_path = os.path.join(BASE_DIR, "Model", "xgb_power_forecast_model.pkl")
    model = joblib.load(model_path)
    
    feature_path = os.path.join(BASE_DIR, "Model", "feature_names.pkl")
    feature_names = joblib.load(feature_path)
    
    print("Model loaded successfully!")
    print(f"   Model: power_demand_xgboost.pkl")
    print(f"   Features: {len(feature_names)} loaded")

except Exception as e:
    print(f" Model loading failed: {e}")
    model = None
    feature_names = []

class ForecastRequest(BaseModel):
    date: str  

@app.get("/")
async def root():
    return HTMLResponse("""
    <h1> Apex Power & Utilities - Demand Forecasting API</h1>
    <p>Frontend: <a href="/static/index.html">/static/index.html</a></p>
    <p>API Docs: <a href="/docs">/docs</a></p>
    """)

@app.post("/forecast")
async def get_forecast(request: ForecastRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Check server logs.")

    try:
        target_date = pd.to_datetime(request.date.strip())
        print(f"Forecast requested for: {target_date.date()}")

        # Load historical data
        hist_path = os.path.join(BASE_DIR, "Data", "cleaned_utility_with_features.csv")
        hist = pd.read_csv(hist_path, parse_dates=['Datetime'])
        hist = hist.set_index('Datetime').sort_index()

        last_load = float(hist['Total_Load_Capped'].iloc[-1])

        # Create future timeline (144 blocks = 24 hours)
        future_times = pd.date_range(start=target_date, periods=144, freq='10T')
        df_future = pd.DataFrame(index=future_times)

        # Time & Calendar Features
        df_future['Hour'] = df_future.index.hour
        df_future['DayOfWeek'] = df_future.index.dayofweek
        df_future['Month'] = df_future.index.month
        df_future['IsWeekend'] = df_future['DayOfWeek'].isin([5, 6]).astype(int)
        df_future['IsNight'] = df_future['Hour'].isin([22,23,0,1,2,3,4,5]).astype(int)

        df_future['Hour_sin'] = np.sin(2 * np.pi * df_future['Hour'] / 24)
        df_future['Hour_cos'] = np.cos(2 * np.pi * df_future['Hour'] / 24)
        df_future['DayOfWeek_sin'] = np.sin(2 * np.pi * df_future['DayOfWeek'] / 7)
        df_future['DayOfWeek_cos'] = np.cos(2 * np.pi * df_future['DayOfWeek'] / 7)

        # Weather Data (Temperature, Humidity, WindSpeed, CloudCover)
        LAT, LON = 23.7957, 86.4304
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,cloud_cover&timezone=Asia/Kolkata"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            hourly = pd.DataFrame({
                'Datetime': pd.to_datetime(data['hourly']['time']),
                'Temperature': data['hourly']['temperature_2m'],
                'Humidity': data['hourly']['relative_humidity_2m'],
                'WindSpeed': data['hourly']['wind_speed_10m'],
                'CloudCover': data['hourly']['cloud_cover']
            })

            hourly = hourly.set_index('Datetime').resample('10T').ffill().interpolate(method='linear')
            hourly = hourly.reindex(df_future.index, method='nearest')

            df_future['Temperature'] = hourly['Temperature']
            df_future['Humidity'] = hourly['Humidity']
            df_future['WindSpeed'] = hourly['WindSpeed']
            df_future['CloudCover'] = hourly['CloudCover']

            print(" Weather data fetched successfully")

        except Exception as e:
            print(f"Weather API failed: {e}. Using fallback values.")
            df_future['Temperature'] = 27.0
            df_future['Humidity'] = 68.0
            df_future['WindSpeed'] = 4.0
            df_future['CloudCover'] = 50.0

        # Holiday Data
        try:
            hol_path = os.path.join(BASE_DIR, "Data", "df_holiday_localized_2017.csv")
            holidays = pd.read_csv(hol_path, parse_dates=['Datetime'])
            holiday_dates = set(holidays['Datetime'].dt.date)
            df_future['IsHoliday'] = df_future.index.date.isin(holiday_dates).astype(int)
        except:
            df_future['IsHoliday'] = 0
            print("Warning: Holiday file not found.")

        # Derived Features
        df_future['Temp_Humidity_Index'] = df_future['Temperature'] * df_future['Humidity'] / 100
        df_future['FeelsLike'] = df_future['Temperature'] - 0.5 * (df_future['Humidity'] / 100) * (df_future['Temperature'] - 14)

        # Recursive Forecasting
        predictions = []
        current_load = last_load

        for i in range(144):
            row = df_future.iloc[i:i+1].copy()

            for lag in [1, 2, 6, 12, 144]:
                row[f'Lag_Load_{lag}'] = current_load

            for w in [6, 12, 36, 144]:
                row[f'Roll_Mean_{w}'] = current_load
                row[f'Roll_Std_{w}'] = 0.0
                row[f'Roll_Max_{w}'] = current_load

            # Fill missing Temp_ bin columns
            for col in [c for c in feature_names if c.startswith('Temp_')]:
                if col not in row.columns:
                    row[col] = 0

            X_pred = pd.DataFrame(0.0, index=[0], columns=feature_names)
            for col in feature_names:
                if col in row.columns:
                    X_pred[col] = float(row[col].iloc[0])

            pred = model.predict(X_pred)[0]
            predictions.append(float(pred))
            current_load = pred

        # Build Response
        result = []
        for i in range(144):
            result.append({
                "Datetime": future_times[i].strftime('%Y-%m-%d %H:%M'),
                "Block": i + 1,
                "Predicted_Total_Load_MW": round(predictions[i], 2),
                "Temperature_C": round(float(df_future['Temperature'].iloc[i]), 2),
                "Humidity_%": round(float(df_future['Humidity'].iloc[i]), 1),
                "WindSpeed_m/s": round(float(df_future['WindSpeed'].iloc[i]), 1),
                "CloudCover_%": round(float(df_future['CloudCover'].iloc[i]), 1),
                "IsHoliday": int(df_future['IsHoliday'].iloc[i])
            })

        return result

    except Exception as e:
        print(f"Error during forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting Apex Power Demand Forecasting API...")
    print("[INFO] Open browser at: http://127.0.0.1:8000/static/index.html")
    uvicorn.run(app, host="0.0.0.0", port=8000)