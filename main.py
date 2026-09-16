import os
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI()

# Connection Manager to track all connected Unity clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str, sender: WebSocket):
        # Relay movement data to every client EXCEPT the one who sent it
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"status": "Server is running on Render!"}

class CommandRequest(BaseModel):
    action: str
    value: float = 0.0

@app.post("/api/command")
def handle_command(cmd: CommandRequest):
    print(f"Received action: {cmd.action} with value: {cmd.value}")
    return {
        "success": True,
        "message": f"Action '{cmd.action}' executed successfully",
        "received_value": cmd.value
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"[INFO] Unity client connected. Active clients: {len(manager.active_connections)}")
    try:
        while True:
            data = await websocket.receive_text()
            
            # Print to console so it streams live in Render Logs
            print(f"[MOVE LOG] {data}")
            
            # Broadcast position to all other connected Unity instances
            await manager.broadcast(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"[INFO] Unity client disconnected. Active clients: {len(manager.active_connections)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
