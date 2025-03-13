import anthropic
from sentence_transformers import SentenceTransformer
import torch
import psycopg2
import numpy as np
import datetime

"""
해당 세션의 모든 대화 기록을 전부 넘겨서 질문
"""

device = 'cuda'

if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f"GPU Connected: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device('cpu')
    print("GPU Unconnected")

model = SentenceTransformer('all-MiniLM-L6-v2')

conn = psycopg2.connect(
    dbname="msp_database",
    user="postgres",
    password="3636",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

client = anthropic.Anthropic(
    api_key="YOUR API KEY"
)

user_prompt = """history
제 프로젝트를 위해 설치해야할 것들을 정리해주세요.
"""

vector2 = model.encode(user_prompt)
vector_array2 = np.array(vector2).tolist()

cursor.execute("SELECT role, content FROM testsession ORDER BY date, session_id;")
rows = cursor.fetchall()

# 대화 히스토리 구성


chat_history = ""
for role, content in rows:
    if role == "user":
        chat_history += f"사용자: {content}\n"
    elif role == "assist":
        chat_history += f"AI: {content}\n"
# 현재 사용자 입력 추가
chat_history += f"사용자: {user_prompt}\n"

cursor.execute("""
    INSERT INTO testsession (date, content, role, embedding) 
    VALUES (%s, %s, %s, %s);
""", (datetime.date.today(), user_prompt, "user", vector_array2))

message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=4096,
    temperature=0.0,
    system= f"이전 대화 맥락을 참고해주세요. 이전 대화 기록 : {chat_history}",
    messages=[
        {"role": "user", "content": user_prompt}
    ])

prompt_case = message.content[0].text.strip()

vector = model.encode(prompt_case)
vector_array = np.array(vector).tolist()

cursor.execute("""
    INSERT INTO testsession (date, content, role, embedding) 
    VALUES (%s, %s, %s, %s);
""", (datetime.date.today(), prompt_case, "assist", vector_array))

conn.commit()
cursor.close()
conn.close()

# 결과 출력
print("Claude Response:", prompt_case)
print("Embedding Vector:", vector)






