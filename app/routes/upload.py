
from fastapi import APIRouter, UploadFile, File
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
