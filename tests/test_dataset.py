import sys
import types

import pytest

from evaluation.build_dataset import records


@pytest.mark.parametrize('case',records(),ids=lambda row:row['id'])
def test_trusted_reference_satisfies_independent_contract(case,monkeypatch):
    # Executes ONLY repository-authored reference fixtures, never cloud-generated code.
    solution = types.ModuleType('solution')
    exec(compile(case['reference'],case['id']+'.py','exec'),solution.__dict__)
    monkeypatch.setitem(sys.modules,'solution',solution)
    tests = {}
    exec(compile(case['tests'],'test_'+case['id']+'.py','exec'),tests)
    tests['test_contract']()


@pytest.mark.parametrize('case',[r for r in records() if r['kind']=='fix'],ids=lambda r:r['id'])
def test_bug_fixtures_really_fail(case,monkeypatch):
    solution = types.ModuleType('solution')
    try:
        exec(compile(case['buggy'],case['id']+'.py','exec'),solution.__dict__)
        monkeypatch.setitem(sys.modules,'solution',solution)
        tests = {}
        exec(compile(case['tests'],'test_'+case['id']+'.py','exec'),tests)
        with pytest.raises(Exception): tests['test_contract']()
    except SyntaxError:
        pass
