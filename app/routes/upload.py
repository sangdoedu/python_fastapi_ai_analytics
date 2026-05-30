
from fastapi import APIRouter, UploadFile, File, Response, Request
import pandas as pd
import uuid
import json
import hashlib

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

#refresh cache in Cloudflare
# cdn_api_url = "https://api.cloudflare.com/client/v4/zones/zone_id/purge_cache"
# headers = {"Authorization": "Bearer CDN_SECRET_TOKEN"}
# payload = {
#     "files": [f"https://api.myproject.com/products/{product_id}"]
# }
# async with httpx.AsyncClient() as client:
# # Tell the CDN edge servers worldwide to delete their cached copy of this URL
#     await client.post(cdn_api_url, json=payload, headers=headers)

#BE checks old and new cache
@router.get("/live-dashboard")
async def get_dashboard(request: Request, response: Response):
    db_data = {"status": "all_systems_operational", "version": 42}
    data_string = json.dumps(db_data, sort_keys=True)
    current_etag = f'W/"{hashlib.md5(data_string.encode()).hexdigest()}"'
    # 3. Check if the client sent an old ETag matching the current one
    client_etag = request.headers.get("if-none-match")
    if client_etag == current_etag:
        # Data hasn't changed! Return instantly with NO body data.
        return Response(status_code=304)
    # 4. If data changed, set headers and send new data
    
    response.headers["Cache-Control"] = "no-cache" # Must revalidate every time
    response.headers["ETag"] = current_etag
    return db_data