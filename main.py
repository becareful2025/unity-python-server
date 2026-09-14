import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI()

# Simple HTTP endpoint test
@app.get("/")
def read_root():
    return {"status": "Server is running on Render!"}

# Example HTTP POST model to handle Unity commands
class CommandRequest(BaseModel):
    action: str
    value: float = 0.0

@app.post("/api/command")
def handle_command(cmd: CommandRequest):
    print(f"Received action: {cmd.action} with value: {cmd.value}")
    # Execute logic here (e.g., update game state)
    return {
        "success": True,
        "message": f"Action '{cmd.action}' executed successfully",
        "received_value": cmd.value
    }

# Example WebSocket endpoint for real-time Unity communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Unity client connected via WebSocket.")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from Unity: {data}")
            # Echo back or respond to Unity
            await websocket.send_text(f"Server acknowledged: {data}")
    except WebSocketDisconnect:
        print("Unity client disconnected.")

# Entry point for local testing or direct running
if __name__ == "__main__":
    import uvicorn
    # Render provides the PORT environment variable dynamically
    port = int(os.environ.get("PORT", 10000))
    # Must bind to 0.0.0.0 for external access on Render
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
