
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

from redis import asyncio as aioredis
redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
@router.get("/test_redis")
async def get_product():
    cache_key = "_product"
    cached_product = await redis_client.get(cache_key)
    if cached_product:
        product_data = json.loads(cached_product)
        product_data["source"] = "This info is from cache"
        return product_data
        
    db_product = {'name': 'headphone 1', 'price': 45.6}
    if not db_product:
        return None
    await redis_client.setex(
        name=cache_key,
        time=30,    #30 sec
        value=json.dumps(db_product)
    )
    db_product["source"] = "This info from db"
    return db_product


from groq import Groq
groq_client = Groq(api_key="xxx")
def call_llm(system: str, prompt: str) -> str:
    chat_completion = await groq_client.chat.completions.create(
        messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile"
        )
    ai_text = chat_completion.choices[0].message.content
    return ai_text


def _generate_cache_key(ai_model_name, prompt: str) -> str:
    clean_prompt = prompt.strip().lower()
    prompt_hash = hashlib.sha256(clean_prompt.encode('utf-8')).hexdigest()
    return f"llm:cache:{ai_model_name}:{prompt_hash}"

