from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

TRADE_LOG = []
CURRENT_MODE = "evaluation"
AUTO_MODE = True

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "mode": CURRENT_MODE,
            "auto": AUTO_MODE,
            "log": TRADE_LOG[-10:]
        }
        await websocket.send_text(json.dumps(data))
        await websocket.receive_text()

@app.post("/mode/{new_mode}")
async def change_mode(new_mode: str):
    global CURRENT_MODE
    CURRENT_MODE = new_mode
    return {"mode": CURRENT_MODE}

@app.post("/toggle-auto")
async def toggle_auto():
    global AUTO_MODE
    AUTO_MODE = not AUTO_MODE
    return {"auto": AUTO_MODE}

@app.post("/reset")
async def reset():
    global TRADE_LOG
    TRADE_LOG = []
    return {"log": []}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    TRADE_LOG.append(data)
    with open("bot_memory.json", "a") as f:
        f.write(json.dumps(data) + "\n")
    return {"status": "received", "data": data}

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)