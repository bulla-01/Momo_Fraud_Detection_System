# suspicious_transactions_by_day.py

from fastapi import APIRouter, Query
from datetime import datetime
import psycopg2
from typing import List, Dict, Any, Optional

router = APIRouter()
DATABASE_URL = "postgresql://postgres:Bentjun25%24@localhost:5432/momo_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@router.get("/suspicious_transactions_by_day/")
def suspicious_transactions_by_day(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> Dict[str, List[Any]]:
    try:
        today = datetime.today()
        default_start = today.replace(month=1, day=1)
        default_end = today

        # Parse query params or use defaults
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else default_start
            end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else default_end
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT trxdate::date AS day, SUM(amount) as total_volume
            FROM prediction_analysis
            WHERE trxdate::date BETWEEN %s AND %s 
              AND prediction_description = 'Fraud'
            GROUP BY day
            ORDER BY day ASC;
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
        results = cursor.fetchall()
        conn.close()

        labels = [row[0].strftime('%Y-%m-%d') for row in results]
        values = [float(row[1]) for row in results]

        return {"labels": labels, "values": values}
    except Exception as e:
        return {"error": str(e)}
