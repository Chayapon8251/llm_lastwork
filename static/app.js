const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const labels = {camera:"กล้อง",audio:"อุปกรณ์เสียง",tripod:"ขาตั้งกล้อง",lighting:"ไฟสตูดิโอ"};
const icons = {camera:"▣",audio:"♩",tripod:"⋀",lighting:"☀"};
const statusLabels = {available:"พร้อมยืม",borrowed:"ถูกยืมอยู่",maintenance:"กำลังซ่อม"};
let history = [], stock = [], busy = false;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
async function api(path, options) {
  const res = await fetch(path, options);
  let data;
  try { data = await res.json(); } catch { throw new Error("server ส่งผลที่อ่านไม่ได้"); }
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "ข้อมูลไม่ผ่านการตรวจสอบ กรุณาลองใหม่");
  return data;
}
function switchPage(page) {
  $$(".page").forEach(p => p.classList.toggle("hidden", p.id !== "page-"+page));
  $$(".nav-item").forEach(p => p.classList.toggle("active", p.dataset.page === page));
  $("#page-title").textContent = {chat:"ผู้ช่วยยืมอุปกรณ์",inventory:"คลังอุปกรณ์",evaluation:"ผลประเมิน"}[page];
  if (page === "evaluation") loadEvaluation();
}
$$('[data-page]').forEach(b => b.addEventListener('click', () => switchPage(b.dataset.page)));

function renderStock() {
  const parent = $("#stock-summary"); parent.replaceChildren();
  Object.entries(labels).forEach(([category,name]) => {
    const row = el("div","stock-row");
    row.append(el("span","stock-icon",icons[category]));
    const title = el("div"); title.append(el("strong","",name),el("small","",category.toUpperCase()));
    const count = el("b","",String(stock.filter(x=>x.category===category && x.status==="available").length));
    count.append(el("small","","ชิ้น"));row.append(title,count);parent.append(row);
  });
}
function renderInventory(filter="all") {
  const parent = $("#inventory-grid"); parent.replaceChildren();
  stock.filter(x=>filter==="all" || x.category===filter).forEach(item=>{
    const card=el("article","equipment-card");
    card.append(el("div","equipment-illustration",icons[item.category]),el("small","",item.id+" / "+item.code),el("h3","",item.name));
    const meta=el("div","equipment-meta");meta.append(el("span","pill "+item.status,statusLabels[item.status]),el("span","","ประกัน "+item.deposit+" ฿"));card.append(meta);parent.append(card);
  });
}
$$("[data-filter]").forEach(b=>b.addEventListener("click",()=>{
  $$("[data-filter]").forEach(x=>x.classList.toggle("selected",x===b));renderInventory(b.dataset.filter);
}));

function renderAnswer(data) {
  const block=el("div","assistant-message");
  block.append(el("div","bubble",data.answer));
  const meta=el("div","answer-meta");
  meta.append(el("span","",data.mode==="live" ? "CLASS PROXY · "+data.model : "DEMO · ไม่ได้เรียก LLM"),el("span","",data.elapsed_ms+" ms"));
  block.append(meta);
  const citations=el("div","source-list"), details=el("div");
  data.sources.forEach(source=>{
    const b=el("button","source-button","↗ "+source.title);
    b.addEventListener("click",()=>{
      const p=el("div","source-text",source.text+"\nที่มา: "+source.source);
      if (details.dataset.source === source.id && details.childNodes.length) { details.replaceChildren(); details.dataset.source=""; }
      else { details.replaceChildren(p);details.dataset.source=source.id; }
    });citations.append(b);
  });
  block.append(citations,details);
  if (data.trace.length) {
    const trace=el("details","trace");
    trace.append(el("summary","","ดูขั้นตอนที่ใช้ · "+data.trace.length+" tool calls · "+data.stop_reason));
    trace.append(el("pre","",JSON.stringify(data.trace,null,2)));block.append(trace);
  }
  $("#conversation").append(block);
}
async function send(question) {
  if (busy || !question.trim()) return;
  busy=true;$("#send-button").disabled=true;
  $("#suggestions")?.remove();
  const conversation=$("#conversation");
  conversation.append(el("div","bubble user-message",question));
  const thinking=el("div","thinking","กำลังตรวจข้อมูลและเตรียมคำตอบ…");conversation.append(thinking);
  $("#message").value="";$("#char-count").textContent="0 / 1,000";conversation.scrollTop=conversation.scrollHeight;
  try {
    const data=await api("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:question,history:history.slice(-12)})});
    thinking.remove();renderAnswer(data);
    history.push({role:"user",content:question},{role:"assistant",content:data.answer.slice(0,3000)});
  } catch(error) { thinking.remove();conversation.append(el("div","error",error.message)); }
  finally {busy=false;$("#send-button").disabled=false;conversation.scrollTop=conversation.scrollHeight;$("#message").focus();}
}
$("#chat-form").addEventListener("submit",e=>{e.preventDefault();send($("#message").value);});
$("#message").addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send(e.currentTarget.value);}});
$("#message").addEventListener("input",e=>{$("#char-count").textContent=e.target.value.length+" / 1,000";});
$$('[data-question]').forEach(b=>b.addEventListener("click",()=>send(b.dataset.question)));
$("#clear-chat").addEventListener("click",()=>{if(!busy) location.reload();});

const pct=x=>(x*100).toFixed(1)+"%";
async function loadEvaluation() {
  try {
    const data=await api("/api/evaluation");
    const base=data.systems.find(x=>x.system==="vector_top1"), chosen=data.systems.find(x=>x.system==="vector_top3");
    const metrics=$("#metric-summary");metrics.replaceChildren();
    [[pct(chosen.recall),"Recall@3 ของวิธีที่เลือก","baseline recall@1 "+pct(base.recall)],[(100*(chosen.recall-base.recall)).toFixed(1)+" pp","เพิ่มจาก baseline top-1","ต่างจำนวน chunk · ไม่ใช่ผล hybrid ล้วน"],[String(data.n),"คำถามที่มี labels","ยังไม่มีผู้ตรวจอิสระ"]].forEach(([number,title,note])=>{
      const box=el("div","metric");box.append(el("strong","",number),el("span","",title),el("small","",note));metrics.append(box);
    });
    const table=$("#evaluation-table");table.replaceChildren();
    const names={vector_top1:"Vector top-1 · baseline",vector_top3:"Vector top-3 · ใช้จริง",bm25_top3:"BM25 top-3",hybrid_top3:"Hybrid RRF top-3"};
    data.systems.forEach(row=>{const tr=el("tr",row.system==="vector_top3"?"selected-row":"");[names[row.system],String(row.cutoff),pct(row.recall),pct(row.precision),row.mrr.toFixed(3),pct(row.complete)].forEach(v=>tr.append(el("td","",v)));table.append(tr);});
    const failures=$("#failure-cases");failures.replaceChildren();
    chosen.details.filter(x=>x.complete<1).forEach(item=>{const card=el("div","failure-item");card.append(el("strong","",item.id+" · "+item.query),el("p","","ต้องการ: "+item.relevant.join(", ")),el("p","","ค้นได้: "+item.ranked.join(", ")));failures.append(card);});
    if(!failures.childNodes.length) failures.append(el("p","","ไม่มีกรณีตกหล่นในชุดนี้ แต่ยังต้องทดสอบคำถามนอกชุดและการตอบของ LLM"));
  } catch(error) {$("#failure-cases").textContent=error.message;}
}

async function init() {
  try {
    const [status,inventory]=await Promise.all([api("/api/status"),api("/api/inventory")]);
    stock=inventory.items;renderStock();renderInventory();
    $("#mode-status").textContent=status.mode==="live"?"Class proxy":"โหมดสาธิต";
    $("#status-button").classList.toggle("live",status.mode==="live");
    $("#demo-banner").classList.toggle("hidden",status.mode==="live");
    const details=$("#status-details");
    ["โหมด: "+status.mode,"โมเดล: "+status.model,"ตั้งค่า proxy: "+(status.configured?"แล้ว":"ยังไม่ได้ตั้ง"),"ขีดจำกัด: "+status.max_steps+" agent turns","ข้อมูลทั้งหมด: จำลอง"].forEach(t=>details.append(el("p","",t)));
  } catch(error) {$("#mode-status").textContent="เชื่อมต่อไม่ได้";$("#stock-summary").textContent=error.message;}
}
$("#status-button").addEventListener("click",()=>$("#status-dialog").showModal());
$$(".dialog-close").forEach(b=>b.addEventListener("click",()=>$("#status-dialog").close()));
init();
