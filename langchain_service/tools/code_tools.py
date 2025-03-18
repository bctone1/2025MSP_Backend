from langchain.agents import tool
import subprocess
import tempfile
import os

@tool
def execute_python_code(code: str) -> str:
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
def get_database_schema(project_id: int) -> str:
    return f"데이터베이스 스키마 정보 (프로젝트 ID: {project_id})..."

