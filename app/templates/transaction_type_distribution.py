from fastapi import APIRouter, Query
from datetime import datetime
import psycopg2
from typing import List, Dict

router = APIRouter()
DATABASE_URL = "postgresql://postgres:Bentjun25%24@localhost:5432/momo_db"

@router.get("/transaction_type_distribution/", response_model=Dict[str, List[Dict[str, int]]])
def get_transaction_type_distribution(month: str = Query(default=None)):
    """
    Returns transaction type distribution filtered by month (format: YYYY-MM).
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if month:
            start_date = f"{month}-01"
            end_date = f"{month}-31"  # Simplified assumption
            query = """
                SELECT type, COUNT(*) 
                FROM prediction_analysis 
                WHERE trxdate::date BETWEEN %s AND %s
                GROUP BY type;
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = "SELECT type, COUNT(*) FROM prediction_analysis GROUP BY type;"
            cursor.execute(query)

        results = cursor.fetchall()
        conn.close()

        return {"data": [{"type": r[0], "count": r[1]} for r in results]}
    except Exception as e:
        return {"error": str(e)}
