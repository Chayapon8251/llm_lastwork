import json
import threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .agent import chat, configuration, retriever
from .inventory import query_inventory
from .schemas import ChatRequest

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="GearMate", version="0.1.0", description="Equipment lending assistant. Synthetic data; demo mode is not an LLM.")
slots = threading.BoundedSemaphore(2)
app.mount("/assets", StaticFiles(directory=ROOT / "static"), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "static/index.html")


@app.get("/api/status")
def status():
    return {**configuration(), "synthetic_data": True, "policy_count": len(retriever().documents), "inventory_count": query_inventory()["count"]}


@app.get("/api/policies")
def policies():
    return retriever().documents


@app.get("/api/inventory")
def inventory():
    return query_inventory()


@app.get("/api/evaluation")
def evaluation():
    path = ROOT / "results/retrieval.json"
    if not path.exists():
        raise HTTPException(404, "Run python -m scripts.evaluate first")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/chat")
def ask(request: ChatRequest):
    if not slots.acquire(blocking=False):
        raise HTTPException(429, "กำลังประมวลผลคำถามอื่น กรุณาลองอีกครั้ง")
    try:
        return chat(request.message, [m.model_dump() for m in request.history], request.mode)
    except RuntimeError as exc:
        # Only the known configuration error is shown; never echo a proxy response or secret.
        if "ยังไม่ได้ตั้ง" in str(exc):
            raise HTTPException(503, "ยังไม่ได้ตั้ง OPENAI_API_KEY และ OPENAI_BASE_URL ใน .env") from None
        raise HTTPException(502, "ประมวลผลไม่สำเร็จ กรุณาตรวจการตั้งค่า server") from None
    except Exception:
        raise HTTPException(502, "ติดต่อ class proxy หรือประมวลผลคำตอบไม่สำเร็จ ไม่มีการสลับเป็นคำตอบจำลอง กรุณาลองใหม่หรือตรวจการตั้งค่า") from None
    finally:
        slots.release()
