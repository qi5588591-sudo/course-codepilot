import json

import httpx
import pytest

from backend.config import Settings
from backend.llm import LLMClient, ModelError, parse_output
from backend.prompts import build_messages, summarize_python
from backend.schemas import TaskRequest


def test_parsing_and_rejection():
    assert parse_output('```json\n{"code":"x=1"}\n```').code == 'x=1'
    for bad in ['hello','{"issues":[{"line":0,"message":"x"}]}','{"suggestions":[{}]}']:
        with pytest.raises(ModelError): parse_output(bad)


def test_context_ablation_keeps_task_code_and_excludes_auxiliary_files():
    req = TaskRequest(task='review',code='def f(x): return x',requirement='review',
        prefix='import math',context_files=[{'path':'helper.py','content':'secret helper'}])
    with_context = build_messages(req)[1]['content']
    assert 'helper.py' in with_context and 'function f' in with_context
    req.use_context = False
    data = json.loads(build_messages(req)[1]['content'])
    assert data['code'] == req.code
    assert 'context_files' not in data and 'prefix' not in data
    assert '语法错误' in summarize_python('def f(')


@pytest.mark.parametrize('status,expected',[(401,502),(403,502),(429,429),(500,502)])
async def test_provider_http_errors_are_sanitized(monkeypatch,status,expected):
    original = httpx.AsyncClient
    def transport(request): return httpx.Response(status,text='private-provider-error')
    monkeypatch.setattr('backend.llm.httpx.AsyncClient',lambda **kw: original(transport=httpx.MockTransport(transport),**kw))
    llm = LLMClient(Settings(_env_file=None,api_base='https://model.example/v1',api_key='private-key',model='test'))
    with pytest.raises(ModelError) as caught:
        await llm.generate(TaskRequest(task='generate',requirement='x'))
    assert caught.value.status == expected
    assert 'private' not in str(caught.value)


async def test_real_adapter_success_with_mock_transport(monkeypatch):
    original = httpx.AsyncClient
    def transport(request):
        assert str(request.url) == 'https://model.example/v1/chat/completions'
        assert json.loads(request.content)['messages'][0]['role'] == 'system'
        return httpx.Response(200,json={'choices':[{'message':{'content':'{"code":"x=1"}'}}],'usage':{'total_tokens':7}})
    monkeypatch.setattr('backend.llm.httpx.AsyncClient',lambda **kw: original(transport=httpx.MockTransport(transport),**kw))
    output,usage = await LLMClient(Settings(_env_file=None,api_base='https://model.example/v1',api_key='x',model='test')).generate(TaskRequest(task='generate',requirement='x'))
    assert output.code == 'x=1' and usage['total_tokens'] == 7


@pytest.mark.parametrize('kind', ['timeout','network','badbody','empty'])
async def test_provider_timeout_network_and_invalid_body(monkeypatch,kind):
    original = httpx.AsyncClient
    def transport(request):
        if kind == 'timeout': raise httpx.ReadTimeout('private',request=request)
        if kind == 'network': raise httpx.ConnectError('private',request=request)
        return httpx.Response(200,json={} if kind=='badbody' else {'choices':[{'message':{'content':'{}'}}]})
    monkeypatch.setattr('backend.llm.httpx.AsyncClient',lambda **kw: original(transport=httpx.MockTransport(transport),**kw))
    with pytest.raises(ModelError) as caught:
        await LLMClient(Settings(_env_file=None,api_base='https://model.example/v1',api_key='x',model='test')).generate(TaskRequest(task='generate',requirement='x'))
    assert 'private' not in str(caught.value)
