# การ deploy GearMate บน Render

## สถานะ

Deploy บน Render Free สำเร็จแล้ว: [เปิด GearMate](https://gearmate.onrender.com) ตรวจเมื่อ 27 ตุลาคม 2569 ว่า `/healthz` ตอบสถานะ ok ในโหมด live และหน้าเว็บเรียก class proxy จริงพร้อม SQL และค้นคู่มือได้ ผลตรวจอยู่ใน `results/deployment-smoke.json` ส่วน smoke test บนเครื่อง 3 สถานการณ์เดิมอยู่ใน `results/live-smoke.json`

## เหตุผลที่เลือก Render

โฮสต์ Python/FastAPI เดิมได้โดยตรง จึงคง `from openai import OpenAI` และ SQLite tool เดิม ไม่เปลี่ยน backend เป็น JavaScript เพื่อส่งขึ้น static hosting ตัวข้อมูลเป็น read-only snapshot ที่สร้างจาก JSON ใหม่ได้ จึงไม่ต้องมีฐานข้อมูล cloud เพิ่ม

## วิธีทำจาก GitHub

1. ใช้บัญชี Render ของผู้ส่งและเชื่อม repo Chayapon8251/llm_lastwork
2. สร้าง Blueprint จาก render.yaml หรือใช้ปุ่ม Deploy to Render ใน README
3. ตรวจว่า service เป็น Web, runtime Python, plan Free และ region Singapore
4. Build command: `pip install -r requirements.lock.txt && python -m scripts.evaluate`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers`
6. ใส่ OPENAI_API_KEY ใน environment ของ Render เท่านั้น ค่าอื่นกำหนดใน Blueprint ได้ ห้าม commit .env หรือใส่ key ใน frontend
7. รอ deployment เป็น Live และ `/healthz` ตอบ 200

ถ้าใช้ integration ใน Codex ต้องติดตั้งและเชื่อม Render ก่อนจึงจะสร้าง service ในนามบัญชีของผู้ส่งได้ การเสนอ integration ไม่ได้แปลว่าติดตั้งหรือเชื่อมแล้ว

## ตรวจเว็บก่อนใช้ส่งงาน

- เปิด URL ของ service ที่ Render ให้จริง เช่นโดเมน `.onrender.com` ไม่ใช่ URL ของ dashboard
- ตรวจป้าย Class proxy แล้วถาม “กล้องว่างกี่ตัว และต้องวางเงินประกันเท่าไร” ต้องเห็น SQL และคู่มือ และจำนวนตรง snapshot
- ทักทายเพื่อดูกรณีไม่ใช้ tool
- ถามโดรนและอธิบายว่าเป็นหมวดที่ schema ไม่รองรับ ไม่ใช่หลักฐานว่าค้น inventory แล้วเหลือศูนย์
- เปิดหน้าผลประเมินและดู failure t27
- ตรวจบนมือถือและจอใหญ่ รวมทั้งทดลองเปิดจากเครื่องที่ไม่ได้รัน server อยู่
- จึงนำ URL ที่ยืนยันแล้วไปใส่ README และ Q3 โดยคงผลการทดลองบนเครื่องแยกจากผลบนโฮสต์

## ข้อจำกัดของการโฮสต์เดโม

Free instance พักเมื่อไม่มี inbound traffic ประมาณ 15 นาที และอาจใช้เวลาประมาณหนึ่งนาทีเมื่อเปิดใหม่ อย่าเปิดอุ่นเครื่องด้วยระบบยิง request อัตโนมัติเพื่อเลี่ยงข้อจำกัดของผู้ให้บริการ

GEARMATE_PUBLIC_DEMO=true เปิด request budgets 6/นาทีต่อ client, 40/ชั่วโมงรวม และ 120/วันรวม พร้อม body limit 64 KiB และ concurrency 2 โดยใช้ worker เดียว การนับอยู่ในหน่วยความจำและ reset เมื่อ restart ไม่ใช่ durable quota หรือระบบป้องกันการใช้งานผิดวัตถุประสงค์ระดับ production แต่ละ request ยังมีขีดจำกัด agent turns และ tool calls ของตัวเอง

ถ้า health check ไม่ผ่านเพราะตั้ง live แต่ไม่มี credentials ให้แก้ environment แล้ว deploy ใหม่ ถ้า 401 ให้ตรวจ key โดยไม่แปะ key ลง log หาก proxy ล้มเหลว แอปจะคืน error ไม่สลับเป็น demo เพื่อทำให้ดูเหมือนเรียกโมเดลสำเร็จ

## ลิงก์ทางการ

- https://render.com/docs/deploy-fastapi
- https://render.com/docs/blueprint-spec
- https://render.com/docs/free
