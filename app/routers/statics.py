import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers.manager import UPLOAD_DIR

router = APIRouter()

# HTML 파일 서빙
@router.get("/{name}", response_class=HTMLResponse)
async def serve_html(
    name: str
):
    print(name)
    if not os.path.exists(f"app/statics/{name}"):
        return RedirectResponse(url="/topic-list.html")
    html_content = open(f"app/statics/{name}").read()
    return HTMLResponse(content=html_content)

@router.get("/uploads/{image_path}")
async def get_image(image_path: str):
    print(image_path)
    return FileResponse(UPLOAD_DIR + "/" + image_path)

@router.get("/")
async def root():
    return RedirectResponse(url="/topic-list.html")

