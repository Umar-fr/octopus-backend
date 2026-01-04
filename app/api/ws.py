from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.progress_manager import repo_progress_manager

router = APIRouter()

@router.websocket("/ws/progress/{repo_id}")
async def ws_repo_progress(websocket: WebSocket, repo_id: int):
    await repo_progress_manager.connect(repo_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        repo_progress_manager.disconnect(repo_id, websocket)
