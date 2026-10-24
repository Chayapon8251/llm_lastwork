# Proposal

GearMate เป็นผู้ช่วยสำหรับนักศึกษาที่ต้องการยืมอุปกรณ์ชมรม โดยตอบกฎการยืมจากคู่มือและจำนวนอุปกรณ์ว่างจาก SQLite snapshot ในแชตเดียว ใช้ class proxy โมเดล gemma-4-E4B-it ผ่าน OpenAI SDK, native tool calling ที่มี stop condition, Pydantic validation และ FastAPI UI ข้อมูลเป็น policy corpus และ inventory สมมติที่สร้างใหม่ ไม่ใช่ corpus ของแอปตัวอย่างวิชา ประเมิน retrieval ด้วยคำถามติด label 30 ข้อ เทียบ vector top-1 กับ vector top-3 และ BM25/RRF ที่บริบทเท่ากัน วัด recall, precision, MRR และกรณีที่ต้องใช้หลายแหล่ง พร้อมแยกการทดสอบ LLM จริงออกจาก offline metrics
