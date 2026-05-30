
from fastapi import APIRouter, UploadFile, File, Response
import pandas as pd
import uuid

router = APIRouter()
DATA_STORE = {}

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    session_id = str(uuid.uuid4())
    DATA_STORE[session_id] = df

    return {
        "session_id": session_id,
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(),
        "filename": file.filename
    }

#sample API to set cache control
@router.get("/heavy-catalog")
async def get_heavy_catalog(response: Response):
    catalog_data = {"categories": ["Electronics", "Books", "Clothing"], "version": "1.0.4"}
    response.headers["Cache-Control"] = "public, max-age=600"
    response.headers["ETag"] = "v1-catalog-hash-777" 
    return catalog_data