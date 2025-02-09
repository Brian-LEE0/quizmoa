import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter()

# HTML 파일 서빙
@router.get("/{name}", response_class=HTMLResponse)
async def serve_html(
    name: str
):
    # HTML 파일을 직접 반환하는 방법
    print(name)
    html_content = open(f"app/statics/{name}.html").read()
    return HTMLResponse(content=html_content)