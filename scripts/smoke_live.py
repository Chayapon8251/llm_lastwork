"""Explicit real-proxy smoke run; do not run without configured class credentials."""
import json
from pathlib import Path
from app.agent import chat, configuration


def main():
    if not configuration()["configured"]:
        raise SystemExit("Missing OPENAI_API_KEY or OPENAI_BASE_URL. No requests made.")
    questions = ["สวัสดีครับ", "กล้องว่างกี่ตัว และต้องวางเงินประกันเท่าไร", "มีโดรนให้ยืมไหม"]
    output=[]
    for question in questions:
        result=chat(question,mode="live")
        output.append({"question":question,"result":result})
        print(question)
        print(result["answer"])
        print("tools:",[x["tool"] for x in result["trace"]],"stop:",result["stop_reason"])
    path=Path(__file__).resolve().parents[1]/"runtime/live-smoke.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Saved to runtime/live-smoke.json (ignored by Git). Review answers manually; this is not an automatic faithfulness score.")


if __name__=="__main__":
    main()
