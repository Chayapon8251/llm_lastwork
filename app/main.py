import json
import os
import threading
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .agent import chat, configuration, retriever
from .inventory import query_inventory
from .schemas import ChatRequest
from .limits import DemoLimiter

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="GearMate", version="0.1.0", description="Equipment lending assistant. Synthetic data; demo mode is not an LLM.")
slots = threading.BoundedSemaphore(2)
limiter = DemoLimiter()
app.mount("/assets", StaticFiles(directory=ROOT / "static"), name="assets")


def public_demo():
    return os.getenv("GEARMATE_PUBLIC_DEMO", "false").lower() in {"1", "true", "yes"}


@app.middleware("http")
async def public_request_budget(request: Request, call_next):
    if public_demo() and request.method == "POST" and request.url.path == "/api/chat":
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                if int(declared) > 65536:
                    return JSONResponse({"detail": "คำขอมีขนาดเกิน 64 KiB"}, status_code=413)
            except ValueError:
                return JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)
        body = await request.body()
        if len(body) > 65536:
            return JSONResponse({"detail": "คำขอมีขนาดเกิน 64 KiB"}, status_code=413)
        client = request.client.host if request.client else "unknown"
        allowed, retry = limiter.allow(client)
        if not allowed:
            return JSONResponse({"detail": "ครบจำนวนคำถามสำหรับเดโมในช่วงนี้ กรุณาลองอีกครั้งภายหลัง"}, status_code=429, headers={"Retry-After": str(retry)})
    return await call_next(request)


@app.get("/healthz", include_in_schema=False)
def health():
    config = configuration()
    if config["mode"] == "live" and not config["configured"]:
        raise HTTPException(503, "Live mode requires proxy configuration")
    return {"status": "ok", "mode": config["mode"]}


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
