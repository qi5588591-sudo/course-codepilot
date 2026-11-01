import asyncio

import pytest

from backend.config import Settings
from backend.llm import ModelError
from backend.main import create_app
from backend.schemas import ModelOutput, ValidationResult
from fastapi.testclient import TestClient


def fake_model(service):
    async def generate(req):
        return ModelOutput(code="def add(a, b):\n    return a + b\n", explanation="生成结果"), {"total_tokens": 42}
    service.llm.generate = generate


def test_health_and_unconfigured_model(client):
    assert client.get('/health').json()['model_configured'] is False
    response = client.post('/api/tasks', json={'task': 'generate', 'requirement': '加法'})
    assert response.status_code == 503
    assert '配置' in response.json()['detail']


@pytest.mark.parametrize('language', ['python', 'java', 'javascript', 'cpp'])
@pytest.mark.parametrize('task', ['generate','complete','explain','review','tests','docs','fix','naming','suggest'])
def test_tasks_and_history(client, language, task):
    fake_model(client.app.state.service)
    response = client.post('/api/tasks', json={'task':task,'language':language,'requirement':'任务'})
    assert response.status_code == 200
    row = response.json()
    assert row['usage']['total_tokens'] == 42
    assert row['verification'] == '未验证'
    history = client.get('/api/history').json()
    assert history[0]['id'] == row['id']
    assert client.get('/api/history/' + row['id']).json() == row


@pytest.mark.parametrize('payload', [
    {'task':'generate'}, {'task':'unknown','requirement':'x'},
    {'task':'generate','language':'ruby','requirement':'x'},
    {'task':'generate','requirement':'x','code':'x'*60001},
])
def test_invalid_tasks(client,payload):
    assert client.post('/api/tasks',json=payload).status_code == 422


def test_history_missing_and_pagination(client):
    assert client.get('/api/history/missing').status_code == 404
    assert client.get('/api/history?limit=0').status_code == 422
    assert client.get('/api/history?offset=-1').status_code == 422


def test_origin_rejected_and_token_protected(tmp_path):
    with TestClient(create_app(Settings(_env_file=None,database=str(tmp_path/'auth.db'),backend_token='local-secret'))) as client:
        assert client.get('/api/history').status_code == 401
        assert client.get('/api/history',headers={'Authorization':'Bearer local-secret'}).status_code == 200
        assert client.get('/api/history',headers={'Authorization':'Bearer local-secret','Origin':'http://testserver'}).status_code == 200
        assert client.post('/api/tasks',json={'task':'generate','requirement':'x'},headers={'Origin':'https://example.com','Authorization':'Bearer local-secret'}).status_code == 403


def test_verification_syntax_no_tests_unavailable(client,monkeypatch):
    monkeypatch.setattr('backend.sandbox.shutil.which',lambda _:None)
    assert client.post('/api/verify',json={'code':'def broken(','tests':''}).json()['status'] == 'syntax_error'
    assert client.post('/api/verify',json={'code':'x=1','tests':''}).json()['status'] == 'no_tests'
    result = client.post('/api/verify',json={'code':'x=1','tests':'def test_x():\n assert True'}).json()
    assert result['status'] == 'unavailable'
    assert len(result['tests_sha256']) == 64


def test_repair_preserves_tests_and_records_rounds(client):
    service = client.app.state.service
    observed_tests, observed_codes = [], []
    async def verify(code,tests):
        observed_tests.append(tests); observed_codes.append(code)
        return ValidationResult(status='passed' if 'a + b' in code else 'failed',output='assertion failed',tests_sha256='same')
    service.sandbox.verify = verify
    fake_model(service)
    tests = 'from solution import add\ndef test_add():\n assert add(1,2)==3'
    response = client.post('/api/repair',json={'code':'def add(a,b): return a-b','tests':tests,'max_repairs':2}).json()
    assert response['status'] == 'passed'
    assert len(response['rounds']) == 2
    assert observed_tests == [tests,tests]
    assert response['usage']['total_tokens'] == 42
    assert client.get('/api/history/' + response['id']).json() == response


def test_repair_stops_after_two_and_handles_model_failure(client):
    service = client.app.state.service
    async def verify(code,tests): return ValidationResult(status='failed',output='failed')
    service.sandbox.verify = verify
    fake_model(service)
    payload = {'code':'x=0','tests':'def test_x(): pass','max_repairs':2}
    result = client.post('/api/repair',json=payload).json()
    assert len(result['rounds']) == 3
    assert result['status'] == 'failed'
    assert result['usage']['total_tokens'] == 84
    async def broken(req): raise ModelError('额度不足',429)
    service.llm.generate = broken
    result = client.post('/api/repair',json=payload).json()
    assert result['repair_error'] == '额度不足'
    assert len(result['rounds']) == 1


def test_invalid_test_syntax_does_not_trigger_model_repair(client):
    result = client.post('/api/repair',json={'code':'x=1','tests':'def test_x('}).json()
    assert len(result['rounds']) == 1
    assert result['status'] == 'syntax_error'


def test_out_of_range_repair_count(client):
    assert client.post('/api/repair',json={'code':'x=1','tests':'','max_repairs':3}).status_code == 422
