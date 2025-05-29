from fastapi.responses import StreamingResponse
from io import BytesIO
import openpyxl
from xhtml2pdf import pisa
from fastapi.responses import Response

@app.get("/export/high_risk_users/excel")
def export_high_risk_users_excel():
    session = SessionLocal()
    try:
        users = session.query(RiskUser).order_by(RiskUser.risk_score.desc()).limit(10).all()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "High Risk Users"
        ws.append(["Username", "Risk Score"])

        for user in users:
            ws.append([user.username, user.risk_score])

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename=high_risk_users.xlsx"})
    finally:
        session.close()


@app.get("/export/high_risk_users/pdf")
def export_high_risk_users_pdf():
    session = SessionLocal()
    try:
        users = session.query(RiskUser).order_by(RiskUser.risk_score.desc()).limit(10).all()
        html = "<h2>High Risk Users</h2><table border='1'><tr><th>Username</th><th>Risk Score</th></tr>"
        for user in users:
            html += f"<tr><td>{user.username}</td><td>{user.risk_score}</td></tr>"
        html += "</table>"

        result = BytesIO()
        pisa.CreatePDF(html, dest=result)
        result.seek(0)
        return StreamingResponse(result, media_type="application/pdf",
                                 headers={"Content-Disposition": "attachment; filename=high_risk_users.pdf"})
    finally:
        session.close()
