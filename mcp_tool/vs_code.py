import subprocess
import os
import json
from langchain_community.chat_models import ChatOpenAI
from core.config import EMBEDDING_API

base_path = r"C:\Users\leegy\Desktop\mcp_test"

def new_window(*args, **kwargs):
    try:
        subprocess.Popen([r"C:\Users\leegy\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd", "--new-window"])
        return {"status": "VS Code opened in new window"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def close_window(*args, **kwargs):
    try:
        subprocess.run("taskkill /IM Code.exe /F", shell=True)  # Code.exe 프로세스를 강제로 종료
        return {"status": "All VS Code windows closed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def new_project(*args, **kwargs):
    try:
        # 예시 프로젝트 이름
        project_name = "NewProject"
        project_path = os.path.join(base_path, project_name)


        if not os.path.exists(project_path):
            os.makedirs(project_path)

        subprocess.Popen([r"C:\Users\leegy\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd", "--new-window", project_path])

        return {"status": "New project folder created and opened in VS Code"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_python_file_from_llm(user_input, project_folder_path=base_path, *args, **kwargs):
    try:
        # LLM 객체 초기화
        llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=EMBEDDING_API)

        prompt = f"사용자가 요청한 파이썬 코드를 작성해 주세요: {user_input}"
        response = llm(prompt)
        python_code = response

        python_file_path = os.path.join(project_folder_path, "script.py")
        with open(python_file_path, 'w', encoding='utf-8') as f:
            f.write(python_code)

        subprocess.Popen([
            r"C:\Users\leegy\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd",
            python_file_path
        ])

        return {
            "status": "Python code file 'script.py' created and opened in VS Code",
            "code": python_code
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool 정의
def python_file_tool(input: str) -> dict:
    try:
        # JSON 문자열로 들어온 input을 딕셔너리로 파싱
        input_data = json.loads(input)
        user_input = input_data.get("user_input")
        project_folder_path = input_data.get("project_folder_path", base_path)

        # LLM 응답 받아서 코드 생성
        llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=EMBEDDING_API)
        prompt = f"사용자가 요청한 파이썬 코드를 작성해 주세요: {user_input}"
        response = llm(prompt)
        python_code = response

        # 코드 저장
        python_file_path = os.path.join(project_folder_path, "script.py")
        os.makedirs(project_folder_path, exist_ok=True)
        with open(python_file_path, 'w', encoding='utf-8') as f:
            f.write(python_code)

        # VS Code로 열기
        subprocess.Popen([
            r"C:\Users\leegy\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd",
            python_file_path
        ])

        return {
            "status": "Python code file 'script.py' created and opened in VS Code",
            "code": python_code
        }

    except json.JSONDecodeError:
        return {"status": "error", "message": "입력은 JSON 문자열 형식이어야 합니다."}
    except Exception as e:
        return {"status": "error", "message": str(e)}