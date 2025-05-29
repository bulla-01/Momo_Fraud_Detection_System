from fastapi import APIRouter, Query
from datetime import datetime
import psycopg2
from typing import List, Dict

router = APIRouter()
DATABASE_URL = "postgresql://postgres:Bentjun25%24@localhost:5432/momo_db"

@router.get("/high_risk_users/", response_model=Dict[str, List[Dict[str, int]]])
def get_top_high_risk_users(month: str = Query(default=None)):
    """
    Returns transaction type distribution filtered by month (format: YYYY-MM).
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

@app.get("/high_risk_users/")
def top_high_risk_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT trxdate::date AS day, SUM(amount) as total_volume
            FROM prediction_analysis
            WHERE prediction_response = 1
            GROUP BY day
            ORDER BY day ASC;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        # Prepare data for chart.js
        labels = [row[0].strftime('%Y-%m-%d') for row in results]
        values = [float(row[1]) for row in results]

        return {"labels": labels, "values": values}
    except Exception as e:
        return {"error": str(e)}
