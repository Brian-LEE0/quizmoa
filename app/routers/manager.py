import datetime
import os
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import os

from pydantic import BaseModel

from app.core.db import get_engine

router = APIRouter()

# 업로드된 파일을 저장할 디렉토리 설정
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Topic(BaseModel):
    name: str

@router.post("/topics")
async def create_topic(topic: Topic):
    conn = get_engine()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO topics (name) VALUES (?)", (topic.name,))
    conn.commit()
    topic_id = cursor.lastrowid
    return JSONResponse(content={"message": "주제가 성공적으로 생성되었습니다.", "topic_id": topic_id})

@router.get("/topics")
async def get_topics():
    conn = get_engine()
    cursor = conn.cursor()

    # 모든 토픽을 조회
    cursor.execute("SELECT id, name FROM topics")
    topics = cursor.fetchall()

    topic_list = [{"id": topic_id, "name": name} for topic_id, name in topics]

    return JSONResponse(content={"topics": topic_list})


@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: int):
    conn = get_engine()
    cursor = conn.cursor()

    # 주제가 존재하는지 확인
    cursor.execute("SELECT id FROM topics WHERE id = ?", (topic_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")
    
    # 퀴즈 삭제 (주제를 삭제하기 전에 해당 주제에 속한 퀴즈도 삭제)
    cursor.execute("DELETE FROM quizzes WHERE topic_id = ?", (topic_id,))
    
    # 주제 삭제
    cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    conn.commit()

    return JSONResponse(content={"message": "주제가 성공적으로 삭제되었습니다."})


# 퀴즈 API

@router.get("/topics/{topic_id}/quizzes")
async def get_quizzes(topic_id: int):
    conn = get_engine()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM topics WHERE id = ?", (topic_id,))
    topic = cursor.fetchone()
    if not topic:
        raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")

    cursor.execute("SELECT id, idx, quiz_type, question, correct_answer FROM quizzes WHERE topic_id = ? ORDER BY idx ASC", (topic_id,))
    quizzes = cursor.fetchall()

    quiz_list = []
    for quiz in quizzes:
        quiz_id, idx, quiz_type, question, correct_answer = quiz
        options = []

        if quiz_type == "objective":
            cursor.execute("SELECT text, image_path FROM options WHERE quiz_id = ?", (quiz_id,))
            options = [{"text": row[0], "image": row[1]} for row in cursor.fetchall()]

        quiz_list.append({
            "id": quiz_id,
            "idx": idx,
            "quizType": quiz_type,
            "question": question,
            "correctAnswer": correct_answer,
            "options": options
        })

    return JSONResponse(content={"quizzes": quiz_list})

@router.get("/topics/{topic_id}/quizzes/{quiz_id}")
async def get_quiz(topic_id: int, quiz_id: int):
    conn = get_engine()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM topics WHERE id = ?", (topic_id,))
    topic = cursor.fetchone()
    if not topic:
        raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")

    cursor.execute("SELECT idx, quiz_type, question, correct_answer FROM quizzes WHERE id = ? AND topic_id = ?", (quiz_id, topic_id))
    quiz = cursor.fetchone()
    if not quiz:
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    idx, quiz_type, question, correct_answer = quiz
    options = []

    cursor.execute("SELECT text, image_path FROM options WHERE quiz_id = ?", (quiz_id,))
    options = cursor.fetchall()
    optionsText = [row[0] for row in options]
    optionsImagePath = [row[1] for row in options]

    return JSONResponse(content={
        "idx": idx,
        "quizType": quiz_type,
        "question": question,
        "correctAnswer": correct_answer,
        "optionsText": optionsText,
        "optionsImagePath": optionsImagePath
    })
    
import json
@router.post("/topics/{topic_id}/quizzes")
async def upload_quiz(
    topic_id: int,
    idx: Optional[int] = Form(None),
    quizType: str = Form(...),
    question: str = Form(...),
    correctAnswer: str = Form(...),
    optionsText: Optional[str] = Body(None),
    optionsImagePath: Optional[str] = Body(None)
):
    print(optionsText)
    # json unmarsal
    if optionsText is not None:
        optionsText = json.loads(optionsText)
    else:
        optionsText = []
        
    if optionsImagePath is not None:
        optionsImagePath = json.loads(optionsImagePath)
    else:
        optionsImagePath = []
    try:
        conn = get_engine()
        cursor = conn.cursor()

        # 주제 존재 여부 확인
        cursor.execute("SELECT id FROM topics WHERE id = ?", (topic_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")
        
        # get last idx
        cursor.execute("SELECT max(idx) FROM quizzes WHERE topic_id = ?", (topic_id,))
        idx = cursor.fetchone()[0]
        if idx is None:
            idx = 1
        else:
            idx += 1
        
        # 퀴즈 삽입
        cursor.execute(
            "INSERT INTO quizzes (idx, topic_id, quiz_type, question, correct_answer) VALUES (?, ?, ?, ?, ?)",
            (idx, topic_id, quizType, question, correctAnswer)
        )
        quiz_id = cursor.lastrowid

        # 옵션 삽입
        for text, image_path in zip(optionsText, optionsImagePath):
            cursor.execute(
                "INSERT INTO options (quiz_id, text, image_path) VALUES (?, ?, ?)",
                (quiz_id, text, image_path)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()

    return JSONResponse(content={"message": "퀴즈가 성공적으로 업로드되었습니다.", "quiz_id": quiz_id})

@router.put("/topics/{topic_id}/quizzes/{quiz_id}")
async def update_quiz(
    topic_id: int,
    quiz_id: int,
    idx: Optional[int] = Form(None),
    quizType: str = Form(...),
    question: str = Form(...),
    correctAnswer: str = Form(...),
    optionsText: Optional[str] = Body(None),
    optionsImagePath: Optional[str] = Body(None)
):
    # json unmarsal
    if optionsText is not None:
        optionsText = json.loads(optionsText)
    else:
        optionsText = []
        
    if optionsImagePath is not None:
        optionsImagePath = json.loads(optionsImagePath)
    else:
        optionsImagePath = []

    conn = get_engine()
    cursor = conn.cursor()

    # 주제 존재 여부 확인
    cursor.execute("SELECT id FROM topics WHERE id = ?", (topic_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")

    # 퀴즈 존재 여부 확인
    cursor.execute("SELECT id FROM quizzes WHERE id = ? AND topic_id = ?", (quiz_id, topic_id))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    # 퀴즈 업데이트
    cursor.execute(
        "UPDATE quizzes SET idx = ?, quiz_type = ?, question = ?, correct_answer = ? WHERE id = ?",
        (idx, quizType, question, correctAnswer, quiz_id)
    )

    # 기존 옵션 삭제
    cursor.execute("DELETE FROM options WHERE quiz_id = ?", (quiz_id,))

    # 옵션 삽입
    for text, image_path in zip(optionsText, optionsImagePath):
        cursor.execute(
            "INSERT INTO options (quiz_id, text, image_path) VALUES (?, ?, ?)",
            (quiz_id, text, image_path)
        )
    conn.commit()

    return JSONResponse(content={"message": "퀴즈가 성공적으로 업데이트되었습니다."})

@router.patch("/topics/{topic_id}/quizzes/{quiz_id}")
async def update_quiz_idx(
    topic_id: int,
    quiz_id: int,
    idx: int = Form(...),
):
    conn = get_engine()
    cursor = conn.cursor()

    # 퀴즈 존재 여부 확인
    cursor.execute("SELECT id FROM quizzes WHERE id = ?", (quiz_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    # 퀴즈 순서 업데이트
    cursor.execute("UPDATE quizzes SET idx = ? WHERE id = ?", (idx, quiz_id))
    conn.commit()

    return JSONResponse(content={"message": "퀴즈 순서가 성공적으로 업데이트되었습니다."})

@router.delete("/topics/{topic_id}/quizzes/{quiz_id}")
def delete_quiz(topic_id: int, quiz_id: int):
    conn = get_engine()
    cursor = conn.cursor()

    # 주제 존재 여부 확인
    cursor.execute("SELECT id FROM topics WHERE id = ?", (topic_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")

    # 퀴즈 존재 여부 확인
    cursor.execute("SELECT id FROM quizzes WHERE id = ? AND topic_id = ?", (quiz_id, topic_id))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    # 퀴즈 삭제
    cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()

    return JSONResponse(content={"message": "퀴즈가 성공적으로 삭제되었습니다."})

@router.post("/images")
async def upload_image(image: UploadFile = File(...)):
    image_path = f"{UPLOAD_DIR}/{datetime.datetime.now()}{image.filename}"
    with open(image_path, "wb") as f:
        f.write(image.file.read())
    return JSONResponse(content={"message": "이미지가 성공적으로 업로드되었습니다.", "image_path": image_path})