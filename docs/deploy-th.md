# ��� deploy GearMate �� Render

## ʶҹ�

Deploy �� Render Free ���������: [�Դ GearMate](https://gearmate.onrender.com) ��Ǩ����� 27 ���Ҥ� 2569 ��� `/healthz` �ͺʶҹ� ok ����� live ���˹��������¡ class proxy ��ԧ����� SQL ��Ф鹤������� �ŵ�Ǩ����� `results/deployment-smoke.json` ��ǹ smoke test ������ͧ 3 ʶҹ��ó��������� `results/live-smoke.json`

## �˵ؼŷ�����͡ Render

��ʵ� Python/FastAPI ������µç �֧�� `from openai import OpenAI` ��� SQLite tool ��� �������¹ backend �� JavaScript �����觢�� static hosting ��Ǣ������� read-only snapshot ������ҧ�ҡ JSON ������ �֧����ͧ�հҹ������ cloud ����

## �ԸշӨҡ GitHub

1. ��ѭ�� Render �ͧ������������� repo Chayapon8251/llm_lastwork
2. ���ҧ Blueprint �ҡ render.yaml ��������� Deploy to Render � README
3. ��Ǩ��� service �� Web, runtime Python, plan Free ��� region Singapore
4. Build command: `pip install -r requirements.lock.txt && python -m scripts.evaluate`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers`
6. ��� OPENAI_API_KEY � environment �ͧ Render ��ҹ�� �����蹡�˹�� Blueprint �� ���� commit .env ������� key � frontend
7. �� deployment �� Live ��� `/healthz` �ͺ 200

����� integration � Codex ��ͧ�Դ����������� Render ��͹�֧�����ҧ service 㹹���ѭ�բͧ������� ����ʹ� integration ���������ҵԴ����������������

## ��Ǩ��纡�͹���觧ҹ

- �Դ URL �ͧ service ��� Render ����ԧ ������ `.onrender.com` ����� URL �ͧ dashboard
- ��Ǩ���� Class proxy ���Ƕ�� ����ͧ��ҧ����� ��е�ͧ�ҧ�Թ��Сѹ����Ô ��ͧ��� SQL ��Ф����� ��Шӹǹ�ç snapshot
- �ѡ������ʹ١ó������ tool
- ����ù���͸Ժ���������Ǵ��� schema ����ͧ�Ѻ �������ѡ�ҹ��Ҥ� inventory ����������ٹ��
- �Դ˹�ҼŻ����Թ��д� failure t27
- ��Ǩ����Ͷ����Ш��˭� �����駷��ͧ�Դ�ҡ����ͧ���������ѹ server ����
- �֧�� URL ����׹�ѹ�������� README ��� Q3 �¤��š�÷��ͧ������ͧ�¡�ҡ�ź���ʵ�

## ��ͨӡѴ�ͧ�����ʵ����

Free instance �ѡ���������� inbound traffic ����ҳ 15 �ҷ� ����Ҩ�����һ���ҳ˹�觹ҷ�������Դ���� �����Դ�������ͧ�����к��ԧ request �ѵ��ѵ���������§��ͨӡѴ�ͧ�������ԡ��

GEARMATE_PUBLIC_DEMO=true �Դ request budgets 6/�ҷյ�� client, 40/���������� ��� 120/�ѹ��� ����� body limit 64 KiB ��� concurrency 2 ���� worker ���� ��ùѺ�����˹��¤�������� reset ����� restart ����� durable quota �����к���ͧ�ѹ�����ҹ�Դ�ѵ�ػ��ʧ���дѺ production ���� request �ѧ�բմ�ӡѴ agent turns ��� tool calls �ͧ����ͧ

��� health check ����ҹ���е�� live ������� credentials ����� environment ���� deploy ���� ��� 401 ����Ǩ key ������� key ŧ log �ҡ proxy ������� �ͻ�Ф׹ error �����Ѻ�� demo ���ͷ���������͹���¡���������

## �ԧ��ҧ���

- https://render.com/docs/deploy-fastapi
- https://render.com/docs/blueprint-spec
- https://render.com/docs/free
