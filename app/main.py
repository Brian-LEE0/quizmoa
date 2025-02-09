from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI( title="CVE API", description="API for CVE data", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers.manager import router as manager_router, UPLOAD_DIR
from app.routers.statics import router as statics_router

app.include_router(manager_router, prefix="/api/v1/manager")

app.include_router(statics_router)

@app.get("/uploads/{image_path}")
async def get_image(image_path: str):
    print(image_path)
    return FileResponse(UPLOAD_DIR + "/" + image_path)