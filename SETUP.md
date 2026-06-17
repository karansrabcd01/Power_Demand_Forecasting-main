# Apex Power Demand Forecasting System - Setup Guide

Complete setup and execution guide for the Apex Power Demand Forecasting System. This guide covers Docker-based deployment and local Python execution.

## Prerequisites

Choose one of the setup methods below based on your preference.

### For Docker Setup (Recommended)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Engine)
- Approximately 2GB of free disk space

### For Local Python Setup
- Python 3.10 or higher
- pip (Python package manager)
- Approximately 1GB of free disk space
- A terminal/command prompt

## Project Structure

```
Power_Demand_Forecasting-main/
├── Data/
│   ├── Utility_consumption.csv              # Raw historical data
│   ├── cleaned_utility_with_features.csv    # Processed data with features
│   └── df_holiday_localized_2017.csv        # Dhanbad holiday calendar
├── Model/
│   ├── xgb_power_forecast_model.pkl         # Trained XGBoost model
│   └── feature_names.pkl                    # Feature metadata
├── static/
│   ├── index.html                           # Frontend dashboard
│   └── style.css                            # Modern styling
├── Power_Demand_Forecasting.ipynb           # Jupyter notebook with EDA & training
├── main.py                                  # FastAPI backend application
├── requirements.txt                         # Python dependencies
├── Dockerfile                               # Docker configuration
├── README.md                                # Project overview
└── SETUP.md                                 # This file
```

---

## Option 1: Docker Setup (Recommended)

Docker provides a consistent, containerized environment that works across Windows, macOS, and Linux.

### Step 1: Verify Docker Installation

Open a terminal/command prompt and run:

```bash
docker --version
```

You should see output like: `Docker version 24.0.0, build 12345678`

### Step 2: Navigate to Project Directory

```bash
cd /path/to/Power_Demand_Forecasting-main
```

### Step 3: Build the Docker Image

Build a Docker image from the Dockerfile:

```bash
docker build -t power-demand-forecast .
```

**What this does:**
- Reads the `Dockerfile` configuration
- Installs Python 3.10 base image
- Installs all dependencies from `requirements.txt`
- Copies the application code
- Creates a container image ready to run

**Expected output:**
```
[+] Building 45.2s (11/11) FINISHED
 => [internal] load build context
 => [base 1/6] FROM python:3.10-slim
 ...
 => => naming to docker.io/library/power-demand-forecast:latest
```

### Step 4: Run the Docker Container

Start a container from the image:

```bash
docker run -d -p 8000:8000 --name power_forecast_app power-demand-forecast
```

**Breakdown:**
- `-d` - Run in background (detached mode)
- `-p 8000:8000` - Map port 8000 from container to host
- `--name power_forecast_app` - Give container a readable name
- `power-demand-forecast` - Image name to run

**Expected output:**
```
a7f8c9d2e1b0a3f4c5d6e7f8a9b0c1d2e3f4a5b6
```
(This is the container ID)

### Step 5: Verify Container is Running

```bash
docker ps
```

You should see `power_forecast_app` listed with status `Up`.

### Step 6: Access the Application

**Frontend Dashboard:**
- URL: `http://127.0.0.1:8000/static/index.html`
- This is the main interface for viewing forecasts

**Backend API Documentation:**
- URL: `http://127.0.0.1:8000/docs`
- Interactive Swagger UI to test API endpoints

**Health Check:**
- URL: `http://127.0.0.1:8000/health`
- Should return: `{"status": "ok"}`

### Step 7: Test the Forecast

1. Open `http://127.0.0.1:8000/static/index.html` in your browser
2. Select a date (default: 2026-04-20)
3. Click "Generate 24-Hour Forecast" button
4. Wait for the forecast table and chart to appear
5. Explore the data:
   - **Chart**: Shows predicted load (MW) and temperature over 24 hours
   - **Table**: Detailed 10-minute block forecast with weather parameters
   - **Holiday Rows**: Highlighted in yellow if the day is a holiday

### Step 8: View Backend API

Open `http://127.0.0.1:8000/docs` to see:
- `/forecast` - POST endpoint to generate predictions
- `/health` - GET endpoint for health check
- Request/response schemas with examples

### Step 9: Stop the Container

When you're done, stop the container:

```bash
docker stop power_forecast_app
```

Remove the container (optional):

```bash
docker rm power_forecast_app
```

### Docker Useful Commands

```bash
# View container logs
docker logs power_forecast_app

# View logs in real-time
docker logs -f power_forecast_app

# List all running containers
docker ps

# List all containers (running and stopped)
docker ps -a

# Restart container
docker restart power_forecast_app

# Remove image (after removing container)
docker rmi power-demand-forecast
```

---

## Option 2: Local Python Setup

Run the application directly on your machine using Python.

### Step 1: Verify Python Installation

```bash
python --version
```

Ensure you have Python 3.10 or higher.

### Step 2: Navigate to Project Directory

```bash
cd /path/to/Power_Demand_Forecasting-main
```

### Step 3: Create Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `xgboost` - ML model library
- `pandas` - Data processing
- `numpy` - Numerical computing
- `requests` - HTTP client for weather API
- `python-multipart` - Form data handling

### Step 5: Start the FastAPI Server

Run the backend application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Parameters:**
- `main:app` - Python module and FastAPI application instance
- `--host 0.0.0.0` - Accept connections from any IP
- `--port 8000` - Listen on port 8000
- `--reload` - Auto-restart on code changes (development only)

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

Keep this terminal open.

### Step 6: Access the Application

**Frontend Dashboard:**
- URL: `http://127.0.0.1:8000/static/index.html`

**Backend API Documentation:**
- URL: `http://127.0.0.1:8000/docs`

**Health Check:**
- URL: `http://127.0.0.1:8000/health`

### Step 7: Test the Forecast

1. Open `http://127.0.0.1:8000/static/index.html`
2. Select a date and click "Generate 24-Hour Forecast"
3. Observe the chart and table with 24-hour predictions

### Step 8: Stop the Server

Press `CTRL+C` in the terminal running the server.

### Step 9: Deactivate Virtual Environment

When finished, deactivate the virtual environment:

```bash
deactivate
```

---

## How the Forecasting System Works

### Model Architecture
- **Model Type**: XGBoost (Extreme Gradient Boosting)
- **Training Data**: Historical power load data with weather variables
- **Output**: 24-hour forecast (144 blocks of 10 minutes each)

### Forecast Process
1. **Input**: User selects a date
2. **Feature Engineering**: System generates time-based features (day of week, month, etc.)
3. **Weather Integration**: Fetches real-time forecast from Open-Meteo API
4. **Prediction**: XGBoost model predicts load for each 10-minute block
5. **Holiday Handling**: Adjusts predictions if the day is a holiday
6. **Visualization**: Displays chart and table with results

### Key Features
- **Temperature Integration**: Accounts for seasonal demand variations
- **Humidity & Wind**: Captures weather-driven load changes
- **Cloud Cover**: Reflects solar radiation impact on demand
- **Holiday Detection**: Special handling for local holidays in Dhanbad
- **Recursive Forecasting**: Each prediction feeds into the next for sequential accuracy

---

## Performance Metrics

The trained model achieves excellent accuracy:

| Metric | Value |
|--------|-------|
| MAE (Mean Absolute Error) | 319.39 MW |
| RMSE (Root Mean Squared Error) | 471.35 MW |
| MAPE (Mean Absolute Percentage Error) | 0.52% |
| R² Score | 0.9989 (99.89% variance explained) |

This means predictions are typically within ±320 MW of actual load.

---

## Testing Different Dates

The system works with any date. Try these to see different patterns:

- **Weekdays (Mon-Fri)**: Higher baseline demand
- **Weekends**: Lower demand, flatter curves
- **Summer Dates**: Higher temperature-driven load
- **Winter Dates**: Lower temperature but higher heating demand
- **Holidays**: Special patterns if in the holiday calendar

---

## Troubleshooting

### Port 8000 Already in Use

**Docker:**
```bash
docker run -d -p 8001:8000 --name power_forecast_app power-demand-forecast
```
Then access at `http://127.0.0.1:8001/static/index.html`

**Python:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

### "Connection Refused" Error

Ensure:
1. Server is running (`uvicorn` command succeeded)
2. Port 8000 is not blocked by firewall
3. Wait a few seconds for server to fully start

### Weather API Failures

The system gracefully handles API failures by using default weather values. Forecasts will still work but may be less accurate if weather data is unavailable.

### "ModuleNotFoundError: No module named 'xgboost'"

Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Docker Image Build Fails

Try clearing Docker cache:
```bash
docker build --no-cache -t power-demand-forecast .
```

### Notebook Analysis Not Working

Open `Power_Demand_Forecasting.ipynb` with Jupyter:
```bash
pip install jupyter
jupyter notebook
```

---

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "ok"}
```

### Generate Forecast
```
POST /forecast
Request body: {"date": "2026-04-20"}
Response: Array of 144 forecast objects with load and weather data
```

See `http://localhost:8000/docs` for interactive testing.

---

## Next Steps

1. **Experiment with Dates**
   - Try different seasons and days of week
   - Observe patterns in the forecasts

2. **Review Notebook**
   - Open `Power_Demand_Forecasting.ipynb` to understand EDA and training
   - Modify features or retrain model if desired

3. **Integrate with External Systems**
   - Use the `/forecast` API endpoint in your applications
   - Build alerts for high-load predictions

4. **Production Deployment**
   - Use Docker for cloud deployment
   - Scale with container orchestration (Kubernetes)
   - Add authentication and rate limiting

5. **Model Improvements**
   - Incorporate additional weather variables
   - Add demand response scenarios
   - Implement ensemble models

---

## Files Reference

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with forecast endpoints |
| `Model/xgb_power_forecast_model.pkl` | Trained XGBoost model artifact |
| `Data/cleaned_utility_with_features.csv` | Historical training data |
| `static/index.html` | Frontend dashboard UI |
| `static/style.css` | Modern responsive styling |
| `Power_Demand_Forecasting.ipynb` | Full EDA and model training notebook |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Container configuration |

---

## Support & Documentation

- **API Docs**: `http://localhost:8000/docs` (when running)
- **Notebook**: Open `Power_Demand_Forecasting.ipynb` for detailed analysis
- **Code Comments**: Check `main.py` for implementation details
- **README.md**: Project overview and architecture

---

**Happy forecasting!** ⚡

For questions or issues, review the logs and ensure all prerequisites are installed correctly.
