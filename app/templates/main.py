from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import psycopg2
import calendar

# SQLAlchemy imports for ORM usage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import RiskUser  # Make sure this model is defined
from database import Base  # Ensure Base is properly defined

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection info
DATABASE_URL = "postgresql://postgres:Bentjun25$@localhost:5432/momo_db"

def get_db_connection():
    return psycopg2.connect(
        dbname="momo_db", user="postgres", password="Bentjun25$", host="localhost", port="5432"
    )

# SQLAlchemy setup for ORM endpoints
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/transaction_volume/")
def get_transaction_volume():
    try:
        today = datetime.today()
        start_of_year = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT SUM(amount) 
            FROM prediction_analysis 
            WHERE trxdate::date BETWEEN %s AND %s 
              AND prediction_description = 'Fraud';
        """
        cursor.execute(query, (start_of_year, end_date))
        result = cursor.fetchone()
        volume = float(result[0]) if result[0] is not None else 0.0
        return {"from": start_of_year, "to": end_date, "volume": volume}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

@app.get("/transaction_type_distribution/")
def get_transaction_type_distribution():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT type, COUNT(*) 
            FROM prediction_analysis 
            GROUP BY type
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return {"data": [{"type": row[0], "count": row[1]} for row in results]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

@app.get("/high_risk_users/")
def get_high_risk_users(limit: int = 10):
    try:
        session = SessionLocal()
        users = session.query(RiskUser).order_by(RiskUser.risk_score.desc()).limit(limit).all()
        return {
            "data": [{"username": u.username, "risk_score": u.risk_score} for u in users]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

@app.get("/quarterly_transactions/")
def get_quarterly_transactions(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> Dict[str, Any]:
    try:
        today = datetime.today()

        # Default to first and last day of current month
        if not start_date:
            start = today.replace(day=1)
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")

        if not end_date:
            last_day = calendar.monthrange(today.year, today.month)[1]
            end = today.replace(day=last_day)
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT type, COUNT(type)
            FROM prediction_analysis
            WHERE trxdate BETWEEN %s AND %s
              AND prediction_description = 'Fraud'
            GROUP BY type;
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
        rows = cursor.fetchall()
        labels = [row[0] for row in rows]
        series = [row[1] for row in rows]
        return {
            "start_date": start.strftime('%Y-%m-%d'),
            "end_date": end.strftime('%Y-%m-%d'),
            "labels": labels,
            "series": series
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()


@app.get("/suspicious_transactions_by_day/")

def suspicious_transactions_by_day(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> Dict[str, List[Any]]:
    try:
        today = datetime.today()
        default_start = today.replace(month=1, day=1)
        default_end = today

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else default_start
            end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else default_end
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                DATE_TRUNC('month', trxdate)::date AS month,
                CASE 
                    WHEN EXTRACT(DAY FROM trxdate) BETWEEN 1 AND 7 THEN '1-7'
                    WHEN EXTRACT(DAY FROM trxdate) BETWEEN 8 AND 14 THEN '8-14'
                    WHEN EXTRACT(DAY FROM trxdate) BETWEEN 15 AND 22 THEN '15-22'
                    ELSE '23-31'
                END AS week_range,
                SUM(amount) AS total_volume
            FROM prediction_analysis
            WHERE trxdate::date BETWEEN %s AND %s
              AND prediction_description = 'Fraud'
            GROUP BY month, week_range
            ORDER BY month, week_range;
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
        results = cursor.fetchall()

        labels = [f"{row[0].strftime('%Y-%m')} ({row[1]})" for row in results]
        values = [float(row[2]) for row in results]

        return {"labels": labels, "values": values}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

@app.get("/top_high_risk_users/")
def get_top_high_risk_users(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: int = Query(10, description="Number of users to return")
) -> Dict[str, Any]:
    try:
        today = datetime.today()

        # Default to first and last day of current month
        if not start_date:
            start = today.replace(day=1)
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")

        if not end_date:
            last_day = calendar.monthrange(today.year, today.month)[1]
            end = today.replace(day=last_day)
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT namedest, MAX(fraud_probability) AS max_fraud_prob
            FROM prediction_analysis
            WHERE trxdate::date BETWEEN %s AND %s
              AND LOWER(prediction_description) = 'fraud'
              AND fraud_probability IS NOT NULL
            GROUP BY namedest
            ORDER BY max_fraud_prob DESC
            LIMIT %s
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), limit))
        rows = cursor.fetchall()

        return {
            "start_date": start.strftime('%Y-%m-%d'),
            "end_date": end.strftime('%Y-%m-%d'),
            "users": [{"name": row[0], "risk_score": row[1]} for row in rows]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()


@app.get("/detail_high_risk_users/")
def get_detail_top_high_risk_users(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: int = Query(10, description="Number of users to return")
) -> Dict[str, Any]:
    try:
        today = datetime.today()

        # Default to first and last day of current month
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else today.replace(day=1)
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else today.replace(day=calendar.monthrange(today.year, today.month)[1])

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT trxdate, nameorig, type, amount, namedest, fraud_probability
            FROM prediction_analysis
            WHERE trxdate::date BETWEEN %s AND %s
              AND LOWER(prediction_description) = 'fraud'
              AND fraud_probability IS NOT NULL
            ORDER BY trxdate DESC
            LIMIT %s
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), limit))
        rows = cursor.fetchall()

        results = [
            {
                "trxdate": row[0].strftime('%Y-%m-%d'),
                "nameorig": row[1],
                "type": row[2],
                "amount": float(row[3]),
                "namedest": row[4],
                "fraud_probability": float(row[5])
            }
            for row in rows
        ]

        return {"data": results}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()
            
            
@app.get("/suspicious_location/")
def get_locations_of_users(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> Dict[str, Any]:
    try:
        today = datetime.today()
        year_start = today.replace(month=1, day=1)
        year_end = today.replace(month=12, day=31)

        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else year_start
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else year_end

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT latitude, longitude, fraud_probability
            FROM prediction_analysis
            WHERE trxdate::date BETWEEN %s AND %s
              AND LOWER(prediction_description) = 'fraud'
              AND latitude IS NOT NULL AND longitude IS NOT NULL
              AND fraud_probability IS NOT NULL
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
        rows = cursor.fetchall()

        results = [
            {
                "x": float(row[1]),  # longitude
                "y": float(row[0]),  # latitude
                "r": max(4, float(row[2]) * 10)  # scale bubble size
            }
            for row in rows
        ]

        return {"data": results}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

            
