from fastapi.testclient import TestClient
from app.limits import DemoLimiter
from app.main import app


def test_client_window_expires():
    timer = [0.0]
    limiter = DemoLimiter(clock=lambda: timer[0])
    assert all(limiter.allow('a')[0] for _ in range(6))
    allowed, retry = limiter.allow('a')
    assert not allowed and retry > 0
    timer[0] = 61.0
    assert limiter.allow('a')[0]


def test_global_hour_budget_is_shared_across_clients():
    timer = [0.0]
    limiter = DemoLimiter(clock=lambda: timer[0])
    assert all(limiter.allow(str(i))[0] for i in range(40))
    assert not limiter.allow('another')[0]
    timer[0] = 3601.0
    assert limiter.allow('another')[0]


def test_daily_budget_and_cleanup():
    timer = [0.0]
    limiter = DemoLimiter(clock=lambda: timer[0])
    for hour in range(3):
        timer[0] = hour * 3601.0
        assert all(limiter.allow(f'{hour}-{i}')[0] for i in range(40))
    timer[0] = 4 * 3601.0
    assert not limiter.allow('extra')[0]
    timer[0] = 86401.0
    assert limiter.allow('extra')[0]


def test_health_does_not_call_llm(monkeypatch):
    monkeypatch.setenv('GEARMATE_MODE', 'auto')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('OPENAI_BASE_URL', raising=False)
    response = TestClient(app).get('/healthz')
    assert response.status_code == 200
    assert response.json()['mode'] == 'demo'


def test_live_health_requires_configuration(monkeypatch):
    monkeypatch.setenv('GEARMATE_MODE', 'live')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    assert TestClient(app).get('/healthz').status_code == 503


def test_public_chat_limit_before_proxy_call(monkeypatch):
    monkeypatch.setenv('GEARMATE_PUBLIC_DEMO', 'true')
    from app import main
    monkeypatch.setattr(main, 'limiter', DemoLimiter())
    client = TestClient(app)
    for _ in range(6):
        assert client.post('/api/chat', json={'message': 'สวัสดีครับ', 'mode': 'demo'}).status_code == 200
    response = client.post('/api/chat', json={'message': 'สวัสดีครับ', 'mode': 'demo'})
    assert response.status_code == 429
    assert int(response.headers['retry-after']) > 0


def test_public_payload_limit(monkeypatch):
    monkeypatch.setenv('GEARMATE_PUBLIC_DEMO', 'true')
    response = TestClient(app).post('/api/chat', content='x' * 65537, headers={'content-type': 'application/json'})
    assert response.status_code == 413
