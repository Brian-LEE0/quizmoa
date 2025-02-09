# Python 3.11 이미지를 기반으로 합니다
FROM python:3.11-slim

# 작업 디렉토리를 설정합니다
WORKDIR /app

# 현재 디렉토리의 파일들을 컨테이너의 /app 디렉토리로 복사합니다
COPY . /app

# 필요한 패키지를 설치합니다
# requirements.txt 파일이 있다면 주석을 해제하고 사용하세요
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너가 시작될 때 main.py를 실행합니다
CMD ["python", "main.py"]