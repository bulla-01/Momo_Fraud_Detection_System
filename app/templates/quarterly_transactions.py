from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pandas as pd
from datetime import datetime

app = FastAPI()

# Allow frontend access (CORS setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your transactions dataset (replace with your actual data source)
df = pd.read_csv("transactions.csv")  # Make sure 'trxdate' column exists

# Ensure 'trxdate' is a datetime object
df["trxdate"] = pd.to_datetime(df["trxdate"])

@app.get("/quarterly_transactions/")
def get_quarterly_transactions(start_date: str = Query(...), end_date: str = Query(...)):
    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # Filter transactions by date
        filtered_df = df[(df["trxdate"] >= start) & (df["trxdate"] <= end)]

        # You can transform or aggregate data here if needed
        return filtered_df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
