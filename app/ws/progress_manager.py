from typing import Dict, Set
from fastapi import WebSocket
import threading
import json

class RepoProgressManager:
    def __init__(self):
        self.connections: Dict[int, Set[WebSocket]] = {}
        self.lock = threading.Lock()

    async def connect(self, repo_id: int, websocket: WebSocket):
        await websocket.accept()
        with self.lock:
            self.connections.setdefault(repo_id, set()).add(websocket)

    def disconnect(self, repo_id: int, websocket: WebSocket):
        with self.lock:
            if repo_id in self.connections:
                self.connections[repo_id].discard(websocket)
                if not self.connections[repo_id]:
                    del self.connections[repo_id]

    async def broadcast(self, repo_id: int, payload: dict):
        message = json.dumps(payload)

        with self.lock:
            sockets = list(self.connections.get(repo_id, []))

        for ws in sockets:
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(repo_id, ws)


repo_progress_manager = RepoProgressManager()
