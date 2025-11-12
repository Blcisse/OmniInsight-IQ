from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io
import json

from ..core.database import get_db
from ..models.sales import SaleORM
from sqlalchemy import insert


router = APIRouter(prefix="/api/data", tags=["data-ingest"])


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    type: Literal["sales"] = "sales",
    db: AsyncSession = Depends(get_db),
):
    """Upload CSV or JSON to populate DB tables.

    Currently supports type="sales" with columns/keys: product_id, date,
    region, units_sold, revenue, profit_margin.
    """
    content = await file.read()
    filename = (file.filename or "").lower()

    try:
        if filename.endswith(".csv"):
            text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
        elif filename.endswith(".json"):
            payload = json.loads(content.decode("utf-8"))
            rows = payload if isinstance(payload, list) else [payload]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .csv or .json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    inserted = 0
    if type == "sales":
        batch = []
        for r in rows:
            try:
                batch.append(
                    dict(
                        product_id=str(r.get("product_id")),
                        date=str(r.get("date")),
                        region=(r.get("region") or None),
                        units_sold=int(r.get("units_sold", 0)),
                        revenue=float(r.get("revenue", 0.0)),
                        profit_margin=(float(r.get("profit_margin")) if r.get("profit_margin") not in (None, "") else None),
                    )
                )
            except Exception:
                # skip invalid row
                continue

        if batch:
            stmt = insert(SaleORM).values(batch)
            await db.execute(stmt)
            await db.commit()
            inserted = len(batch)
    else:
        raise HTTPException(status_code=400, detail="Unsupported type")

    return {"status": "ok", "inserted": inserted}

