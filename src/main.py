
from fastapi import FastAPI, Response 
from routes import base, data

app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)



