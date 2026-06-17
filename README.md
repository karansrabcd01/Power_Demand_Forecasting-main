# Apex Power Demand Forecasting System

## Overview
This project is a **Machine Learning & Full Stack**, simplified power demand forecasting system built for Apex Power & Utilities. It predicts power load in 10-minute blocks for the next 24 hours(Total 144 blocks) in Dhanbad, Jharkhand.

The system consists of:
1. **Analysis & Modeling**: A documented Jupyter Notebook containing Exploratory Data Analysis (EDA), Data Cleaning, Feature Engineering, Model Training, and validation using XGBoost.
2. **Backend API**: A FastAPI application that serves the trained XGBoost model and integrates real-time weather data and localized holidays for predicting future demand.
3. **Frontend Dashboard**: A minimal single-page web application (HTML/JS/CSS) utilizing Chart.js to visualize the 24-hour forecast alongside weather parameters.
4. **Docker Containerization**: A complete Docker setup to easily package and run the Backend API, Model, and Frontend in a unified container.

## Repository Structure

```text
├── Data/
│   ├── Utility_consumption.csv               # Original mock dataset
│   ├── cleaned_utility_with_features.csv     # Historical data used by API for forecasting
│   └── df_holiday_localized_2017.csv         # Localized holiday list for Dhanbad
├── Model/
│   ├── xgb_power_forecast_model.pkl          # Trained XGBoost model artifact
│   └── feature_names.pkl                     # Expected feature layout for the model
├── static/
│   ├── index.html                            # Frontend dashboard UI
│   └── style.css                             # Frontend styling
├── Power_Demand_Forecasting.ipynb            # Comprehensive EDA, training & modeling notebook
├── main.py                                   # FastAPI backend logic and endpoints
├── requirements.txt                          # Python dependencies required
├── Dockerfile                                # Docker configuration for deployment
└── README.md                                 # This documentation file
```
##  Model Performance

###  Regression Metrics (Load Forecasting)

The regression model demonstrates high accuracy in predicting power demand:

* **MAE (Mean Absolute Error):** 319.39 MW
* **RMSE (Root Mean Squared Error):** 471.35 MW
* **MAPE (Mean Absolute Percentage Error):** 0.52%
* **R² Score:** 0.9989 *(~99.9% variance explained)*

---

###  Classification Metrics (High Load vs Normal Load)

A classification layer is used to identify high load conditions based on a threshold.

* **Accuracy:** 0.9948

* **Precision:** 0.9733

* **Recall:** 0.9970

* **F1 Score:** 0.9850


---

### Summary

* The regression model achieves **extremely low error rates** and near-perfect variance explanation.
* The classification model maintains **high precision and recall**, ensuring reliable detection of high-load scenarios.
* Overall, the system is robust and suitable for **real-time power demand forecasting and alerting**.

---

## Setup & Execution via Docker (Recommended)

The system is containerized to ensure cross-platform compatibility. Follow these steps to get everything running locally via Docker.

### Prerequisites
- [Docker Desktop](https://docs.docker.com/get-docker/) installed and running on your machine.
- Git installed on your system.

### 1. Build the Docker Image
Open your terminal at the root directory of this repository and run the following command to build the image:
```bash
docker build -t power-demand-forecast .
```

### 2. Run the Docker Container
Once the image is built, start the container on port 8000:
```bash
docker run -d -p 8000:8000 --name power_forecast_app power-demand-forecast
```

### 3. Access the Application
- **Interactive Web Dashboard**: Navigate to [http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html) in your browser.
- **FastAPI Interactive Docs (Swagger UI)**: Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test API endpoints directly.

To stop the container later, run:
```bash
docker stop power_forecast_app
docker rm power_forecast_app
```

---

## Local Python Execution (Alternative)

If you'd prefer to run the system directly using Python without Docker:
1. Ensure you have Python 3.10+ installed.
2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. Access the web interface at `http://127.0.0.1:8000/static/index.html`

---

## Technical Highlights & Features

- **Predictive Engine**: Utilizes XGBoost with robust feature engineering (calendar embeddings, lagged variables, cyclic time encodings).
- **Recursive Forecasting**: The `main.py` server fetches the last known load and continuously estimates future load up to 144 blocks (24 hours).
- **Dynamic Weather API Integration**: Forecast endpoints internally call the `open-meteo` API to fetch real-time upcoming localized weather to dynamically feed the model. 
- **Graceful Fallbacks**: In case of a weather API failure, default climate parameters are used to ensure uninterrupted system operations.
