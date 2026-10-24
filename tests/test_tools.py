import json
import sqlite3
import pytest
from pydantic import ValidationError
from app.agent import dispatch, validate_answer
from app.inventory import connect, query_inventory
from app.retrieval import Retriever, rrf
from app.schemas import SearchArgs, InventoryArgs
from scripts.evaluate import metrics


@pytest.mark.parametrize("args", [{"query":""},{"query":"  "},{"query":1},{"query":"x","top_k":True},{"query":"x","top_k":0},{"query":"x","top_k":6},{"query":"x","extra":1}])
def test_invalid_search_args(args):
    with pytest.raises(ValidationError):
        SearchArgs.model_validate(args)


@pytest.mark.parametrize("args", [{"category":"secret"},{"status":"deleted"},{"code":"x'; DROP TABLE equipment;--"},{"sql":"SELECT * FROM secrets"}])
def test_invalid_inventory_args(args):
    with pytest.raises(ValidationError):
        InventoryArgs.model_validate(args)


def test_inventory_bound_query_and_count():
    result=query_inventory(category="camera",status="available")
    assert result["count"]==2
    assert result["parameters"]==["camera","available"]
    assert "category = ?" in result["sql"]
    assert query_inventory(code="CAM-A6400",status="available")["count"]==1


def test_database_really_read_only():
    db=connect()
    try:
        with pytest.raises(sqlite3.OperationalError,match="readonly"):
            db.execute("DELETE FROM equipment")
    finally:
        db.close()


def test_sql_injection_value_cannot_broaden_query():
    assert query_inventory(code="CAM-A6400' OR 1=1 --")["items"]==[]


def test_unknown_tool_refused():
    with pytest.raises(ValueError,match="allow-list"):
        dispatch("delete_database",{})


def test_known_code_retrieval_and_citation():
    results=Retriever().search("CAM-A6400 เงินประกัน")
    assert results[0]["id"]=="camera_deposit"
    assert results[0]["source"]=="data/policies.json#camera_deposit"


def test_unknown_tokens_no_results():
    assert Retriever().search("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")==[]


def test_rrf_ties_keep_first_seen():
    assert rrf([["a","b"],["b","a"]])==["a","b"]
    assert rrf([[],[]])==[]


def test_metric_multiple_required_sources():
    assert metrics(["a"], ["a","b"],1)=={"recall":.5,"precision":1.0,"mrr":1.0,"complete":0.0}


@pytest.mark.parametrize("raw", [
    '{"answer":"ok","source_ids":["invented"],"supported":true}',
    '{"answer":"ok","source_ids":[],"supported":true}',
    '{"answer":"ok","source_ids":[],"supported":"true"}',
    '{"answer":"ok","source_ids":[],"supported":false,"extra":1}',
    'not json',
])
def test_invalid_final_output_refused(raw):
    with pytest.raises((ValueError,ValidationError)):
        validate_answer(raw,{"duration":{}})


def test_valid_final_output():
    answer=validate_answer('{"answer":"ยืมได้สามวัน","source_ids":["duration"],"supported":true}', {"duration":{}})
    assert answer.source_ids==["duration"]
