"""Protocol tests use stubbed SDK messages: never reported as a real LLM eval."""
import json
from types import SimpleNamespace
import openai
import pytest
from app.agent import live_answer


def response(content=None,calls=None):
    class Message:
        tool_calls=calls
        def __init__(self):
            self.content=content
        def model_dump(self,**kwargs):
            result={"role":"assistant","content":self.content}
            if calls:
                result["tool_calls"]=[{"id":c.id,"type":"function","function":{"name":c.function.name,"arguments":c.function.arguments}} for c in calls]
            return result
    return SimpleNamespace(choices=[SimpleNamespace(message=Message())])


def call(name,args,identifier="c1"):
    return SimpleNamespace(id=identifier,function=SimpleNamespace(name=name,arguments=json.dumps(args)))


def setup(monkeypatch,script):
    monkeypatch.setenv("OPENAI_API_KEY","test-not-a-real-key")
    monkeypatch.setenv("OPENAI_BASE_URL","https://invalid.example/v1")
    seen=[]
    def create(**kwargs):
        seen.append({**kwargs,"messages":list(kwargs["messages"])})
        return script.pop(0)
    monkeypatch.setattr(openai,"OpenAI",lambda **kwargs:SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    return seen


def test_native_round_trip_then_separate_json_validation(monkeypatch):
    seen=setup(monkeypatch,[response(calls=[call("search_docs",{"query":"ระยะเวลายืมปกติ"})]),response("ยืมได้สามวัน"),response('{"answer":"ยืมได้สามวัน","source_ids":["duration"],"supported":true}')])
    answer,trace,sources,stop=live_answer("ยืมได้กี่วัน",[])
    assert answer.supported and stop=="final_answer"
    assert "duration" in sources and len(trace)==1
    assert any(m.get("role")=="tool" and m.get("tool_call_id")=="c1" for m in seen[1]["messages"])
    assert "tools" not in seen[-1]


def test_repeat_block_and_max_steps(monkeypatch):
    monkeypatch.setenv("GEARMATE_MAX_STEPS","2")
    setup(monkeypatch,[response(calls=[call("query_inventory",{})]),response(calls=[call("query_inventory",{})])])
    answer,trace,sources,stop=live_answer("มีอุปกรณ์อะไร",[])
    assert stop=="max_steps" and not answer.supported
    assert "repeated call" in trace[1]["error"]


def test_parallel_calls_all_receive_results(monkeypatch):
    seen=setup(monkeypatch,[response(calls=[call("search_docs",{"query":"กล้อง เงินประกัน"},"a"),call("query_inventory",{"category":"camera","status":"available"},"b")]),response("สองกล้อง"),response('{"answer":"มีกล้องว่างสองตัว","source_ids":["inventory"],"supported":true}')])
    answer,trace,sources,stop=live_answer("กล้องว่างไหมและประกันเท่าไร",[])
    assert len(trace)==2
    assert {m["tool_call_id"] for m in seen[1]["messages"] if m["role"]=="tool"}=={"a","b"}


def test_invalid_json_can_be_repaired_once(monkeypatch):
    setup(monkeypatch,[response("hello"),response("bad json"),response('{"answer":"สวัสดี","source_ids":[],"supported":false}')])
    answer,trace,sources,stop=live_answer("hello",[])
    assert answer.answer=="สวัสดี"
