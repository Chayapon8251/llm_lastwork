"""Build the six-page progress report from measured retrieval results."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT=Path(__file__).resolve().parents[1]
INK=colors.HexColor('#263322')
OLIVE=colors.HexColor('#526b3e')
LIME=colors.HexColor('#e8efdb')
MUTED=colors.HexColor('#75836c')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleGM',fontName='Helvetica-Bold',fontSize=35,leading=40,textColor=INK,spaceAfter=14))
styles.add(ParagraphStyle(name='HeadGM',fontName='Helvetica-Bold',fontSize=20,leading=26,textColor=INK,spaceAfter=16))
styles.add(ParagraphStyle(name='SubGM',fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=OLIVE,spaceBefore=13,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyGM',fontName='Helvetica',fontSize=10,leading=15,textColor=INK,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallGM',fontName='Helvetica',fontSize=8,leading=11,textColor=MUTED,spaceAfter=8))
styles.add(ParagraphStyle(name='TagGM',fontName='Helvetica-Bold',fontSize=8,leading=12,textColor=OLIVE,spaceAfter=12))
styles.add(ParagraphStyle(name='CellGM',fontName='Helvetica',fontSize=8,leading=11,textColor=INK))


def p(text,style='BodyGM'):
    return Paragraph(text,styles[style])


def table(rows,widths):
    data=[[p(escape(str(cell)),'CellGM') for cell in row] for row in rows]
    result=Table(data,colWidths=widths,hAlign='LEFT')
    result.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIME),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#dce4d2'))]))
    return result


def architecture():
    d=Drawing(475,220)
    def box(x,y,w,h,title,subtitle=''):
        d.add(Rect(x,y,w,h,rx=7,fillColor=LIME,strokeColor=colors.HexColor('#ccd8bf')))
        d.add(String(x+w/2,y+h/2+3,title,textAnchor='middle',fontName='Helvetica-Bold',fontSize=9,fillColor=INK))
        if subtitle:d.add(String(x+w/2,y+h/2-10,subtitle,textAnchor='middle',fontSize=7,fillColor=MUTED))
    def arrow(x1,y1,x2,y2):
        d.add(Line(x1,y1,x2,y2,strokeColor=OLIVE,strokeWidth=1))
        if x1==x2:d.add(Polygon([x2,y2,x2-3,y2+6,x2+3,y2+6],fillColor=OLIVE,strokeColor=OLIVE))
        else:d.add(Polygon([x2,y2,x2-6,y2+3,x2-6,y2-3],fillColor=OLIVE,strokeColor=OLIVE))
    box(0,160,104,45,'Thai web UI','FastAPI / REST')
    box(132,160,174,45,'Class proxy / gemma-4-E4B-it','native tool loop, max 5 turns')
    box(335,160,139,45,'Final JSON + validation','schema / citation membership')
    arrow(104,182,132,182);arrow(306,182,335,182)
    box(132,90,174,42,'Allow-list + arguments','Pydantic / repeat detection')
    arrow(220,160,220,132)
    box(35,15,174,45,'search_docs','TF-IDF cosine / original policies')
    box(260,15,174,45,'query_inventory','SQLite query-only / bound values')
    arrow(180,90,122,60);arrow(260,90,347,60)
    d.add(String(238,0,'Tool results return to the model with tool_call_id',textAnchor='middle',fontSize=8,fillColor=MUTED))
    return d


def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#dbe2d1'))
    canvas.line(20*mm,18*mm,190*mm,18*mm)
    canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED)
    canvas.drawString(20*mm,12*mm,'GEARMATE / CAPSTONE PROGRESS REPORT / 25 OCT 2026')
    canvas.drawRightString(190*mm,12*mm,f'{doc.page} / 6')
    canvas.restoreState()


def main():
    result=json.loads((ROOT/'results/retrieval.json').read_text(encoding='utf-8'))
    systems={row['system']:row for row in result['systems']}
    story=[]
    story.extend([p('CAPSTONE / END-TO-END LLM APPLICATION','TagGM'),p('GearMate','TitleGM'),p('An evidence-backed assistant<br/>for student equipment lending','HeadGM'),p('Author: Chayapon8251 | Repository: github.com/Chayapon8251/llm_lastwork','SmallGM')])
    story.append(table([['STATUS','IMPLEMENTATION AND OFFLINE EVALUATION COMPLETE'],['Live class proxy','Not yet verified: credentials unavailable at this report build'],['Data','Synthetic club policies and inventory; no real bookings'],['Purpose','A working, inspectable project foundation, not a final submission claim']],[100,375]))
    story.extend([Spacer(1,18),p('1 / Problem and intended users','SubGM'),p('Students preparing a club production need both policy information and available equipment. A question such as "How many cameras are available, and what deposit is required?" spans prose and structured records. A language model should not invent a stock count or a borrowing rule.'),p('GearMate combines a Thai web interface, document retrieval and a read-only SQLite tool. A live agent chooses which tool to call, sees its results, and returns a validated answer with source IDs. A separately labelled deterministic demo keeps the interface inspectable without credentials.')])
    image=ROOT/'docs/screenshots/home.png'
    if image.exists():
        im=Image(str(image));ratio=min(475/im.imageWidth,220/im.imageHeight);im.drawWidth=im.imageWidth*ratio;im.drawHeight=im.imageHeight*ratio;story.append(im)
    story.append(p('Interface screenshot from offline-demo mode. The banner explicitly states that no LLM was called.','SmallGM'))
    story.append(PageBreak())

    story.extend([p('02 / Design and course coverage','TagGM'),p('Two data sources. One bounded loop.','HeadGM'),architecture(),Spacer(1,15),p('Live execution sequence','SubGM'),p('1. FastAPI validates the user input and bounded history.<br/>2. OpenAI() calls the class proxy with model gemma-4-E4B-it and tool schemas.<br/>3. The model requests a tool; code validates its name and arguments.<br/>4. Tool output returns as role: tool, matched by tool_call_id; the model continues.<br/>5. A normal response with no tool call ends the loop. A separate request renders JSON, which Pydantic and citation-membership checks validate.'),table([['Course family','Concrete implementation'],['Structured output','Validated answer / source_ids / supported JSON; one repair attempt'],['Evaluation (required)','30 labelled retrieval questions; four reproducible comparisons'],['Agent loop (agentic)','Native function calling; no-tool stop, max turns, call budget'],['Advanced SQL (agentic)','Typed filters compile to bound SELECT on a query-only database'],['Served interface','FastAPI endpoints, Thai chat, stock view, metrics view']],[125,350]),Spacer(1,10),p('Retrieval is lexical: character-trigram TF-IDF vectors, not neural semantic embeddings. The SQL tool uses fixed templates rather than unconstrained text-to-SQL. These are deliberate scope choices. No sandbox code execution, web browsing or MCP server is claimed.','SmallGM')])
    story.append(PageBreak())

    story.extend([p('03 / Original data and retrieval','TagGM'),p('A small corpus with explicit provenance.','HeadGM'),p('The repository commits 18 topic-sized policy records in Thai with English translations, and 12 synthetic equipment records. Topics include eligibility, standard duration, deposits, late fees, reservations, training, damage and privacy. Each policy has a stable ID; source links identify the data file and record. This is an original hypothetical domain, not the course reference corpus.'),p('Chunking and indexing','SubGM'),p('One policy record is one chunk, preserving conditions such as the 24-hour extension deadline and staff approval requirement. TF-IDF weights normalized character trigrams and compares vectors by cosine. BM25 uses English tokens and Thai bigrams. Both indexes are built in memory from the committed corpus; there is no external embedding service or persistent vector database.'),p('Candidate systems','SubGM'),table([['System','What changes'],['Vector top-1','Naive named baseline: one cosine-ranked chunk'],['Vector top-3','Budget control: same retriever, three context chunks'],['BM25 top-3','Keyword ranking, same output budget'],['Hybrid top-3','RRF(60) over top ten from each ranking, then three results']],[120,355]),Spacer(1,10),p('Threshold and safety boundaries','SubGM'),p('All candidates use a cosine floor of 0.04. This is a development heuristic, not a calibrated confidence score. A low threshold can admit off-topic text, especially with Thai character overlap. A fresh negative benchmark is needed before relying on automatic abstention. The final model must judge whether evidence answers the question.'),p('Inventory records are loaded into an in-memory SQLite database and the connection is switched to query_only. The only tool accepts category, item code and status. Field names are fixed by code and values use bound parameters. No endpoint accepts arbitrary SQL or writes a reservation.')])
    story.append(PageBreak())

    story.extend([p('04 / Evaluation protocol and results','TagGM'),p('Measure the change, including the trade-off.','HeadGM'),p('The curated test set contains 30 questions: 18 require one source and 12 require two. It includes Thai questions, exact item codes and English multi-source queries. Six development questions and six unsupported/manual scenarios are separate. Labels were authored with AI assistance alongside the corpus and are not independently human-validated. This creates lexical-overlap and selection bias.'),p('Metrics','SubGM'),p('Macro recall@k = relevant IDs in the returned top-k / relevant IDs. Precision@k divides by k. MRR is the mean reciprocal rank of the first relevant hit in the returned list, or zero if absent. Complete coverage is the fraction of questions retrieving every required source. Each result uses its actual cutoff.'),table([['System','k','Recall','Precision','MRR','Complete']]+[[name.replace('_',' '),s['cutoff'],f"{s['recall']:.4f}",f"{s['precision']:.4f}",f"{s['mrr']:.4f}",f"{s['complete']:.4f}"] for name,s in systems.items()],[130,25,80,80,80,80]),Spacer(1,13),p('What the numbers support','SubGM'),p('Increasing the output from one to three vector results raises recall from 0.8000 to 0.9833 (+18.33 percentage points) and complete coverage from 0.6000 to 0.9667. Precision falls from 1.0000 to 0.4556 because more context includes irrelevant chunks. The gain is partly an output-budget change, not proof that a new retrieval algorithm is better.'),p('At the same k=3, hybrid matches the vector results rather than improving them. The shipped default is therefore vector top-3. Hybrid remains an evaluated alternative. MRR=1.0 means the first relevant hit was first on this small set; it does not mean every needed source was retrieved.'),p('Reproduce: python -m scripts.evaluate. results/retrieval.json records rankings, subgroup metrics, failures and newline-normalized SHA-256 hashes. No model calls contribute to this table. These are retrieval metrics, not answer correctness, faithfulness or real-user success rates.','SmallGM')])
    story.append(PageBreak())

    story.extend([p('05 / Failures and verification','TagGM'),p('A high average still misses important context.','HeadGM'),p('Failure A: multi-source retrieval','SubGM'),p('Test t27 asks: "camera deposit and first use training requirements". Gold sources are camera_deposit and training. Vector top-3 instead returns training, lighting_deposit and audio_deposit. Recall for this question is 0.5. MRR remains 1.0 because training is first. Similar vocabulary across deposit policies distracts the lexical retriever.'),p('Failure B: an unseen short question','SubGM'),p('The post-implementation question "How many days can I borrow?" in Thai retrieves extension, membership and weekend_return, missing the standard-duration policy. The more explicit Thai query "standard borrowing duration" succeeds. This is an observed failure, not a removed test. Model-driven query refinement may help, but that has not yet been demonstrated against the real class proxy.'),p('Failure C: unavailable knowledge or action','SubGM'),p('Drone inventory, current weather and next month\'s university holidays are not represented. Booking is a write action and is intentionally unavailable. The damage policy has no flat compensation amount. A correct agent must acknowledge missing data instead of fabricating a fee, date or completed transaction.'),p('What was actually verified','SubGM'),table([['Check','Evidence / scope'],['Automated tests','39 passing tests: validators, query-only DB, injection values, metrics, REST and agent protocol'],['Protocol tests','Stubbed SDK messages verify tool_call_id, parallel calls, repeat blocking, caps and JSON repair; not an LLM benchmark'],['Browser checks','Chat, SQL+policy example, citation expansion, trace, evaluation view and mobile stock filter'],['Real proxy / faithfulness','Not yet run; requires class credentials and manual answer review']],[125,350]),Spacer(1,12),p('Citation membership guarantees only that an ID was observed in a tool result. It does not prove that every sentence follows from that source. Prompt labels discourage injection but the stronger boundary is architectural: no arbitrary execution or write tool exists.','SmallGM')])
    story.append(PageBreak())

    story.extend([p('06 / Limitations and next steps','TagGM'),p('Ready to inspect. Not yet ready to submit.','HeadGM'),p('Remaining completion work','SubGM'),p('1. Configure OPENAI_API_KEY and OPENAI_BASE_URL from the instructor; never commit them.<br/>2. Run python -m scripts.smoke_live using gemma-4-E4B-it. Inspect success and failure answers, tool selection, citations and latency.<br/>3. Have the student verify the corpus and labels, then collect a fresh test set from an independent person.<br/>4. Add a manually reviewed answer-quality evaluation. Separate unsupported claims, wrong answers and reasonable abstentions.<br/>5. Update this report with actual live results and record a narrated 3-6 minute demo showing one success and one honest failure.'),p('Boundaries of the current evidence','SubGM'),p('The corpus is synthetic and small. Test questions were created with the same source material and the benchmark has now been inspected, so it should be considered a development benchmark going forward. The lexical representation is not a neural encoder and cannot reliably match arbitrary paraphrases. The default threshold has not been calibrated on a large negative set. Inventory is a fixed snapshot with no real accounts or operational integration.'),p('What I would improve next','SubGM'),p('Collect independent labels before adding complexity. Then compare multilingual neural embeddings, query construction and a cross-encoder at the same context budget. Keep only changes that improve the relevant metric enough to justify latency and cost. Add authentication, operational logs with privacy controls and real inventory updates only if the prototype becomes a deployed service.'),p('Submission map','SubGM'),table([['Deliverable','Current artifact / remaining gap'],['Q1 repository','github.com/Chayapon8251/llm_lastwork; run instructions, original data, metrics and tests'],['Q2 report','This six-page progress report; regenerate after real-proxy verification'],['Q3 demo URL','Narration outline supplied in docs/demo-script-th.md; recording and upload remain']],[110,365]),Spacer(1,12),p('References and authorship','SubGM'),p('Course Lectures 8-14 supplied the concepts of retrieval metrics, RRF, tool round-trips, bounded loops and SQL guardrails. Native calling follows the official OpenAI guide: https://developers.openai.com/api/docs/guides/function-calling. Code and synthetic corpus were created for this project with AI assistance. The student must inspect, adapt and defend the work; this report does not claim independent human annotation or real LLM performance.','SmallGM')])
    output=ROOT/'docs/report.pdf'
    SimpleDocTemplate(str(output),pagesize=(210*mm,297*mm),leftMargin=20*mm,rightMargin=20*mm,topMargin=20*mm,bottomMargin=24*mm,title='GearMate Capstone Progress Report',author='Chayapon8251').build(story,onFirstPage=footer,onLaterPages=footer)
    print(output)


if __name__=='__main__':
    main()
