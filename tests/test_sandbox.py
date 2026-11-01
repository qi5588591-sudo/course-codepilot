import asyncio
import os
import shutil

import pytest

from backend.sandbox import DockerSandbox, limited_output


def test_sandbox_command_has_limits_and_no_host_mount(settings):
    command = DockerSandbox(settings).command('test-container')
    for required in ['--network=none','--read-only','--memory=256m','--cpus=1','--pids-limit=64','--cap-drop=ALL','--user=65534:65534','--pull=never']:
        assert required in command
    assert '--privileged' not in command
    assert '-v' not in command and '--volume' not in command


async def test_output_is_bounded_but_stream_is_drained():
    stream = asyncio.StreamReader()
    stream.feed_data(b'x'*100000)
    stream.feed_eof()
    text = await limited_output(stream,1024)
    assert len(text)==1024 and stream.at_eof()


@pytest.mark.skipif(os.environ.get('CODEPILOT_DOCKER_TESTS') != '1', reason='requires explicitly enabled Docker sandbox integration')
@pytest.mark.parametrize('code,tests,status',[
    ('def add(a,b): return a+b','from solution import add\ndef test_add(): assert add(1,2)==3','passed'),
    ('def add(a,b): return a-b','from solution import add\ndef test_add(): assert add(1,2)==3','failed'),
    ('while True: pass','def test_x(): import solution','timeout'),
])
async def test_actual_container(settings,code,tests,status):
    assert shutil.which('docker'), 'Docker must be installed for integration tests'
    result = await DockerSandbox(settings).verify(code,tests)
    assert result.status == status
