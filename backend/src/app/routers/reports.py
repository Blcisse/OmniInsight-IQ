from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io
from datetime import datetime

from ..core.database import get_db
from ..models.sales import SaleORM
from ..models.marketing import CampaignORM


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/generate")
async def generate_report(
    fmt: str = Query("csv", regex="^(csv|pdf)$"),
    start_date: str | None = None,
    end_date: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Compile aggregated DB data into a downloadable CSV or PDF.

    Aggregates include:
      - Sales by day (date, total_revenue, orders)
      - Campaign ROI summary (avg_roi)
    Date filters apply to sales by `SaleORM.date` (ISO string).
    """
    # Sales by day
    sales_q = select(
        SaleORM.date.label("date"),
        func.coalesce(func.sum(SaleORM.revenue), 0.0).label("total_revenue"),
        func.count(SaleORM.id).label("orders"),
    ).group_by(SaleORM.date)
    if start_date:
        sales_q = sales_q.where(SaleORM.date >= start_date)
    if end_date:
        sales_q = sales_q.where(SaleORM.date <= end_date)
    sales_q = sales_q.order_by(SaleORM.date.asc())

    sales_res = await db.execute(sales_q)
    sales_rows = [(d, float(rev), int(cnt)) for d, rev, cnt in sales_res.all()]

    # Marketing avg ROI
    avg_roi = float((await db.execute(select(func.coalesce(func.avg(CampaignORM.roi), 0.0)))).scalar_one())

    generated_at = datetime.utcnow().isoformat() + "Z"

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["generated_at", generated_at])
        writer.writerow([])
        writer.writerow(["Sales By Day"]) 
        writer.writerow(["date", "total_revenue", "orders"]) 
        for d, rev, cnt in sales_rows:
            writer.writerow([d, f"{rev:.2f}", cnt])
        writer.writerow([])
        writer.writerow(["Marketing Summary"]) 
        writer.writerow(["avg_roi"]) 
        writer.writerow([f"{avg_roi:.2f}"])

        mem = io.BytesIO(output.getvalue().encode("utf-8"))
        filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(mem, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})

    # Minimal PDF generation (plain text) if reportlab/jspdf not available
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        mem = io.BytesIO()
        c = canvas.Canvas(mem, pagesize=letter)
        width, height = letter
        y = height - 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "OmniInsightIQ Report")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Generated at: {generated_at}")
        y -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Sales By Day")
        y -= 16
        c.setFont("Helvetica", 10)
        for d, rev, cnt in sales_rows[:40]:
            c.drawString(40, y, f"{d}  revenue: ${rev:.2f}  orders: {cnt}")
            y -= 12
            if y < 60:
                c.showPage(); y = height - 40
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Marketing Summary")
        y -= 16
        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Average ROI: {avg_roi:.2f}x")
        c.showPage()
        c.save()
        mem.seek(0)
        filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(mem, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception:
        raise HTTPException(status_code=400, detail="PDF generation requires reportlab installed")

