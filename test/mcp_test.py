import websockets
from fastapi import FastAPI, HTTPException

app = FastAPI()

async def send_command_to_unity(command: str):
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        await websocket.send(command)

@app.post("/execute-unity-command")
async def execute_unity_command(command: str):
    try:
        await send_command_to_unity(command)
        return {"status": "success", "command": command}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

