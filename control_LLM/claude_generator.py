import anthropic
from sentence_transformers import SentenceTransformer
import torch
import psycopg2
import numpy as np
import datetime

client = anthropic.Anthropic(
    api_key="YOUR API KEY"
)

def connect_to_DB():
    conn = psycopg2.connect(
        dbname="msp_database",
        user="postgres",
        password="3636",
        host="localhost",
        port="5433"
    )
    cursor = conn.cursor()
    return conn, conn.cursor()

def setproject_response(description: str):
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0.0,
        system="""
        프로젝트 설명이 주어졌습니다. 이를 분석하고, 다음과 같은 형식으로 요약해주세요.

        프로젝트명:
        설명:
        목적:
        """,
        messages=[
            {"role": "user", "content": f"프로젝트 설명:{description}"}
        ])
    sections = message.content[0].text.strip().split("\n\n")
    project_info = {}
    for section in sections:
        if section.startswith("프로젝트명:"):
            project_info["projectname"] = section.replace("프로젝트명:", "").strip()
        elif section.startswith("설명:"):
            project_info["description"] = section.replace("설명:", "").strip()
        elif section.startswith("목적:"):
            project_info["purpose"] = section.replace("목적:", "").strip()
    return project_info


def set_requirements_response(description: str):
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0.0,
        system="""
        프로젝트 설명이 주어졌습니다. 이를 분석하고, 아래 예시와 똑같은 양식으로 작성해주세요.

        기능 제목: 사용자 로그인 기능
        기능 설명: 사용자가 시스템에 로그인할 수 있는 기능을 제공
        기능 분류: 웹 애플리케이션 기능
        사용 사례: {"로그인 페이지로 이동","로그인 정보 입력","로그인 성공 시 대시보드 화면으로 이동"}
        제약 사항: {"아이디와 비밀번호가 유효한지 확인","로그인 실패 시 오류 메시지 표시"}
        """,
        messages=[
            {"role": "user", "content": f"프로젝트 설명:{description}"}
        ])
    sections = message.content[0].text.strip().split("\n\n")
    print(sections)
    requirement = {}
    for section in sections:
        if section.startswith("기능 제목:"):
            requirement["title"] = section.replace("기능 제목:", "").strip()
        elif section.startswith("기능 설명:"):
            requirement["description"] = section.replace("기능 설명:", "").strip()
        elif section.startswith("기능 분류:"):
            requirement["category"] = section.replace("기능 분류:", "").strip()
        elif section.startswith("사용 사례:"):
            requirement["use_cases"] = section.replace("사용 사례:", "").strip()
        elif section.startswith("제약 사항:"):
            requirement["constraints"] = section.replace("제약 사항:", "").strip()
    print(requirement)
    return requirement

def get_device():
    device = 'cuda'
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"GPU Connected: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        print("GPU not found : CPU connected")

def text_embedding(project_name, cursor, origin_prompt, origin_response, embedding_model = 'all-MiniLM-L6-v2'):
    model = SentenceTransformer(embedding_model)
    vector_prompt = model.encode(origin_prompt)
    prompt = np.array(vector_prompt).tolist()
    vector_response = model.encode(origin_response)
    response = np.array(vector_response).tolist()
    cursor.execute("SELECT project_id FROM project WHERE project_name = %s;", (project_name,))
    project_id = cursor.fetchone()
    cursor.execute("""
            INSERT INTO session (project_id, content, role, embedding) 
            VALUES (%s, %s, %s, %s);
        """, (project_id, origin_prompt, 'user', prompt))
    cursor.execute("""
                INSERT INTO session (project_id, content, role, embedding) 
                VALUES (%s, %s, %s, %s);
        """, (project_id, origin_response, 'assistant', response))
    cursor.connection.commit()
    print("saved")

def get_history(project_name, cursor):
    cursor.execute("SELECT project_id FROM project WHERE project_name = %s;", (project_name,))
    project_id = cursor.fetchone()
    cursor.execute("""
        SELECT session_id, role, content 
        FROM session 
        WHERE project_id = %s 
        ORDER BY session_id;
    """, (project_id,))
    session_data = cursor.fetchall()

    history = ""
    for session_id, role, content in session_data:
        if role == "user":
            history += f"사용자: {content}\n"
        elif role == "assist":
            history += f"AI: {content}\n"
    return history