from langchain.agents import Tool
from mcp_tool.vs_code import *
vs_code_tools = [
    Tool(
        name="new_window",
        func=new_window,
        description="Open a new VS Code window"
    ),
    Tool(
        name="close_window",
        func=close_window,
        description="Close all VS Code windows"
    ),
    Tool(
        name="create_new_project_folder",
        func=new_project,
        description="Create a new project folder and open it in VS Code"
    ),
    Tool(
    name="CreatePythonFile",
    func=python_file_tool,  # func에 함수 전달r
    description="사용자가 요청한 파이썬 코드를 생성하여 VS Code로 여는 도구"
    )
]
