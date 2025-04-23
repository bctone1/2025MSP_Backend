from fastapi import APIRouter, FastAPI, Request
from schemas.mcp import *
import subprocess

mcp_router = APIRouter()

@mcp_router.post("/vscode-command")
async def handle_command(cmd: VSCodeCommand):
    print("📥 명령 수신:", cmd.dict())

    if cmd.action == "open_file" and cmd.filename:
        subprocess.Popen([r"C:\Users\leegy\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd", cmd.filename])
        return {"status": "opened", "file": cmd.filename}

    elif cmd.action == "run_command" and cmd.command:
        subprocess.run(cmd.command, shell=True)
        return {"status": "command executed", "command": cmd.command}

    elif cmd.action == "close_vscode":
        subprocess.run("taskkill /IM Code.exe /F", shell=True)  # Windows 전용
        return {"status": "VSCode closed"}

    return {"status": "invalid or incomplete command"}