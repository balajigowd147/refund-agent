import pytest
from datetime import date
from agent.nodes import parse_request, lookup_order, check_policy_node, finalize_node
from agent.state import RefundState

def test_parse_request():
    state: RefundState = {
        "request_text": "Please refund 350 for order ORD-999",
        "order_id": None,
        "amount": 0,
        "today": None,
        "order": None,
        "decision": None,
        "reason": None,
        "human_decision": None,
        "audit": []
    }
    result = parse_request(state)
    assert result["order_id"] == "ORD-999"
    assert result["amount"] == 350
    assert "today" not in result
    assert len(result["audit"]) > 0

def test_parse_request_leaves_today_unchanged():
    state: RefundState = {
        "request_text": "Refund 100 for order ORD-123 on 2026-04-05",
        "order_id": None,
        "amount": 0,
        "today": date(2026, 6, 1),
        "order": None,
        "decision": None,
        "reason": None,
        "human_decision": None,
        "audit": []
    }
    result = parse_request(state)
    assert result["order_id"] == "ORD-123"
    assert result["amount"] == 100
    assert "today" not in result

def test_parse_request_amount_not_order_id_digits():
    state: RefundState = {
        "request_text": "Refund for order ORD-123, amount 200",
        "order_id": None,
        "amount": 0,
        "today": None,
        "order": None,
        "decision": None,
        "reason": None,
        "human_decision": None,
        "audit": []
    }
    result = parse_request(state)
    assert result["order_id"] == "ORD-123"
    assert result["amount"] == 200

def test_lookup_order():
    state: RefundState = {
        "request_text": "",
        "order_id": "ORD-123",
        "amount": 100,
        "today": date(2026, 6, 1),
        "order": None,
        "decision": None,
        "reason": None,
        "human_decision": None,
        "audit": []
    }
    result = lookup_order(state)
    assert result["order"] is not None
    assert "total" in result["order"]

def test_lookup_order_unknown():
    state: RefundState = {
        "request_text": "",
        "order_id": "UNKNOWN",
        "amount": 100,
        "today": date(2026, 6, 1),
        "order": None,
        "decision": None,
        "reason": None,
        "human_decision": None,
        "audit": []
    }
    result = lookup_order(state)
    assert result["order"] is None

def test_check_policy_node():
    state: RefundState = {
        "request_text": "",
        "order_id": "ORD-123",
        "amount": 100,
        "today": date(2026, 6, 1),
        "order": {"total": 1000, "date": date(2026, 6, 1)},
        "decision": None,
        "reason": None,
        "human_decision": None,
        "audit": []
    }
    result = check_policy_node(state)
    assert result["decision"] == "approved"
    assert len(result["audit"]) > 0

def test_finalize_node():
    state: RefundState = {
        "request_text": "",
        "order_id": "ORD-123",
        "amount": 100,
        "today": date(2026, 6, 1),
        "order": {"total": 1000, "date": date(2026, 6, 1)},
        "decision": "approved",
        "reason": "Auto approved",
        "human_decision": None,
        "audit": []
    }
    result = finalize_node(state)
    assert result["decision"] == "approved"
    assert len(result["audit"]) > 0
