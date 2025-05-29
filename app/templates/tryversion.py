@app.get("/suspicious_location/")
def get_locations_of_users(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
    ) -> Dict[str, Any]:
    try:
        today = datetime.today()

        # Default to first and last day of current year
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else today.replace(day=1)
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else today.replace(day=calendar.monthrange(today.year, today.month)[1])

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT trxdate, nameorig, latitude, longitude
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
            SELECT DATE_TRUNC('month', trxdate) AS month, COUNT(*) as fraud_count
            FROM prediction_analysis
            WHERE trxdate::date BETWEEN %s AND %s
              AND LOWER(prediction_description) = 'fraud'
              AND fraud_probability IS NOT NULL
            GROUP BY month
            ORDER BY month;
        """
        cursor.execute(query, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
        rows = cursor.fetchall()

        results = [
            {
                "month": row[0].strftime('%Y-%m'),
                "fraud_count": row[1]
            }
            for row in rows
        ]

        return {"data": results}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()