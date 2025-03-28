from langchain.agents import tool
import subprocess
import tempfile
import os

@tool
def execute_python_code(code: str) -> str:
    """
    주어진 Python 코드를 실행하고 결과를 반환하는 도구입니다.
    :param code: 실행할 Python 코드
    :return: 실행 결과 또는 오류 메시지
    """
    try:
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
            temp.write(code.encode('utf-8'))
            temp_name = temp.name

        result = subprocess.run(
            ['python3', temp_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        os.unlink(temp_name)

        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Error executing code: {str(e)}"

@tool
def get_database_schema(session_id: int) -> str:
    """
    주어진 프로젝트 ID에 대한 데이터베이스 스키마 정보를 반환하는 도구입니다.
    :param project_id: 프로젝트 ID
    :return: 데이터베이스 스키마 정보
    """
    return f"데이터베이스 스키마 정보 (세션 ID: {session_id})"