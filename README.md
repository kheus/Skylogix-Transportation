# 🌦️ SkyLogix Weather Data Pipeline

## 📌 Project Overview

**SkyLogix Weather Data Pipeline** is a real-time data engineering project designed to help **SkyLogix Transportation**, a logistics company operating across major African cities, make **data-driven operational decisions** based on weather conditions.

The pipeline ingests live weather data from the **OpenWeather API**, stores raw data in **MongoDB**, transforms it into a clean analytical format, and loads it into **PostgreSQL**. The entire workflow is orchestrated using **Apache Airflow**.

---

## 🏢 Business Context

SkyLogix Transportation manages over **1,200 delivery trucks** operating in:

* Nairobi (Kenya)
* Lagos (Nigeria)
* Accra (Ghana)
* Johannesburg (South Africa)

Weather volatility in these regions directly impacts:

* Delivery delays
* Road safety
* Fuel consumption
* Insurance and operational costs

This pipeline provides a **centralized, queryable, and automated weather data system** to support smarter routing, risk mitigation, and analytics.

---

## 🎯 Project Objectives

The pipeline aims to:

1. Ingest real-time weather data from OpenWeatherMap
2. Store raw JSON payloads in MongoDB (staging layer)
3. Transform raw data into a structured analytical format
4. Load clean data into PostgreSQL (data warehouse)
5. Orchestrate the entire workflow using Apache Airflow

---

## 🗂️ Data Source

* **API**: OpenWeatherMap
* **Endpoint**: [https://api.openweathermap.org/data/2.5/weather](https://api.openweathermap.org/data/2.5/weather)
* **Update Frequency**: Every 15 minutes or hourly (configurable)

---

## 🌍 Target Cities

* Nairobi, KE
* Lagos, NG
* Accra, GH
* Johannesburg, ZA

These cities represent SkyLogix’s highest operational impact zones.

---

## 🏗️ Architecture Overview

```
OpenWeather API
       ↓
Python Ingestion Script
       ↓
MongoDB (weather_raw - raw JSON)
       ↓
Apache Airflow (orchestration)
       ↓
PostgreSQL (weather_readings - analytics)
       ↓
Dashboards / Analytics / ML Models
```

---

## 🧠 Data Handling Strategy

### 1️⃣ Ingestion & MongoDB Staging

* Weather data is fetched via Python using the OpenWeather API
* Raw JSON responses are stored **unchanged** in MongoDB
* Documents are **upserted** using a stable key
* Each document includes an `updatedAt` timestamp for incremental processing

**MongoDB Collection**: `weather_raw`

Recommended indexes:

```js
{ city: 1 }
{ updatedAt: 1 }
```

---

### 2️⃣ Transformation Logic (MongoDB → PostgreSQL)

Transformation is applied downstream in Python (not in MongoDB).

Raw documents are normalized and flattened into tabular columns suitable for analytics.

Derived metrics include:

* Temperature
* Humidity
* Pressure
* Wind speed & direction
* Cloud coverage
* Visibility
* Rain & snow volume
* Weather conditions

---

### 3️⃣ PostgreSQL Data Warehouse

**Table**: `weather_readings`

| Column                | Type      | Description            |
| --------------------- | --------- | ---------------------- |
| city                  | VARCHAR   | City name              |
| country               | VARCHAR   | Country code           |
| observed_at           | TIMESTAMP | Observation time       |
| lat                   | NUMERIC   | Latitude               |
| lon                   | NUMERIC   | Longitude              |
| temp_c                | NUMERIC   | Temperature (°C)       |
| feels_like_c          | NUMERIC   | Feels-like temperature |
| pressure_hpa          | INTEGER   | Atmospheric pressure   |
| humidity_pct          | INTEGER   | Humidity (%)           |
| wind_speed_ms         | NUMERIC   | Wind speed             |
| wind_deg              | INTEGER   | Wind direction         |
| cloud_pct             | INTEGER   | Cloud cover (%)        |
| visibility_m          | INTEGER   | Visibility (m)         |
| rain_1h_mm            | NUMERIC   | Rain volume            |
| snow_1h_mm            | NUMERIC   | Snow volume            |
| condition_main        | VARCHAR   | Main condition         |
| condition_description | VARCHAR   | Detailed description   |
| ingested_at           | TIMESTAMP | Load timestamp         |

Indexes:

```sql
CREATE INDEX idx_weather_city_time
ON weather_readings (city, observed_at);
```

---

## ⏱️ Airflow Orchestration

The pipeline is orchestrated using **Apache Airflow**.

### DAG Structure

1. **task_fetch_and_upsert_raw**

   * Calls OpenWeather API
   * Upserts raw JSON into MongoDB

2. **task_transform_and_load_postgres**

   * Reads incremental data from MongoDB
   * Transforms and loads data into PostgreSQL

The DAG can be scheduled to run every **15 minutes** or **hourly**.

---

## 📁 Project Structure

```
skylogix-weather-pipeline/
│── ingestion.py
│── transform_load.py
│── weather_pipeline_dag.py
│── create_table.sql
│── requirements.txt
│── .env.example
│── README.md
```

---

## ⚙️ Environment Variables

Create a `.env` file using `.env.example`:

```env
OPENWEATHER_API_KEY=your_api_key
MONGO_URI=mongodb://localhost:27017
POSTGRES_URI=postgresql://user:password@localhost/Database-name
```

---

## 🚀 How to Run the Project

### 1️⃣ Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Ingestion Script

```bash
python ingestion.py
```

### 4️⃣ Run Transformation & Load

```bash
python transform_load.py
```

### 5️⃣ Run with Airflow (Recommended)

```bash
airflow webserver --port 8080
airflow scheduler
```

Access UI:

```
http://localhost:8080
```

---

## 📊 Analytics Use Cases

* Weather trends per city
* Detection of extreme conditions (heavy rain, strong winds)
* Correlation with delivery delays and route risks
* Input features for ML models (ETA prediction, risk scoring)

---

## 📊 Real-Time Weather Dashboard

The project includes an interactive Streamlit dashboard for monitoring weather conditions across SkyLogix operational cities.

### Dashboard Features
- **Real-time weather monitoring** for all operational cities
- **Temperature trends** visualization over time
- **Weather alerts** for extreme conditions affecting logistics
- **Analytics integration** with sample SQL queries
- **Automatic refresh** every 5 minutes

### Access the Dashboard
1. Ensure the pipeline is running (MongoDB and PostgreSQL are active)
2. Install dashboard dependencies:
   ```bash
   pip install streamlit pandas plotly psycopg2-binary python-dotenv

<img width="1887" height="903" alt="image" src="https://github.com/user-attachments/assets/bc33b347-9b0f-42ed-bad9-1eeab90edeac" />


## 🧾 Deliverables

* Fully working ETL pipeline
* MongoDB staging layer
* PostgreSQL analytics warehouse
* Airflow DAG
* Documentation & architecture diagram

---

## 👤 Author

**Cheikh Bou Mohamed Kanté**

---

## 🏁 Conclusion

This project demonstrates a **production-ready data engineering pipeline** using modern tools and best practices, suitable for real-world logistics and analytics use cases.

---

✅ Ready for academic and professional evaluation
