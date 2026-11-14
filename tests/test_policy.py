import pytest
from datetime import date, timedelta
from agent.policy import check_policy_rules

def test_unknown_order():
    result = check_policy_rules(
        order_id="UNKNOWN",
        amount=100,
        today=date(2026, 6, 1),
        order=None
    )
    assert result["decision"] == "rejected"
    assert "unknown order" in result["reason"].lower()

def test_amount_lte_zero():
    order = {"total": 1000, "date": date(2026, 6, 1)}
    result = check_policy_rules(
        order_id="ORD-1",
        amount=0,
        today=date(2026, 6, 1),
        order=order
    )
    assert result["decision"] == "rejected"
    assert "amount" in result["reason"].lower()

    result_neg = check_policy_rules(
        order_id="ORD-1",
        amount=-50,
        today=date(2026, 6, 1),
        order=order
    )
    assert result_neg["decision"] == "rejected"

def test_amount_exceeds_total():
    order = {"total": 500, "date": date(2026, 6, 1)}
    result = check_policy_rules(
        order_id="ORD-1",
        amount=600,
        today=date(2026, 6, 1),
        order=order
    )
    assert result["decision"] == "rejected"
    assert "exceeds" in result["reason"].lower()

def test_order_age_limit():
    today = date(2026, 6, 1)
    
    # Exactly 30 days old: allowed
    order_30 = {"total": 1000, "date": today - timedelta(days=30)}
    result_30 = check_policy_rules(
        order_id="ORD-1",
        amount=100,
        today=today,
        order=order_30
    )
    assert result_30["decision"] != "rejected"

    # 31 days old: rejected
    order_31 = {"total": 1000, "date": today - timedelta(days=31)}
    result_31 = check_policy_rules(
        order_id="ORD-1",
        amount=100,
        today=today,
        order=order_31
    )
    assert result_31["decision"] == "rejected"

def test_order_age_today_none():
    order = {"total": 1000, "date": date(2026, 6, 1)}
    result = check_policy_rules(
        order_id="ORD-1",
        amount=100,
        today=None,
        order=order
    )
    assert result["decision"] == "rejected"
    assert "cannot verify order age" in result["reason"].lower()

def test_auto_approve_threshold():
    today = date(2026, 6, 1)
    order = {"total": 1000, "date": today}
    
    result_500 = check_policy_rules(
        order_id="ORD-1",
        amount=500,
        today=today,
        order=order
    )
    assert result_500["decision"] == "approved"

def test_human_approval_threshold():
    today = date(2026, 6, 1)
    order = {"total": 1000, "date": today}
    
    result_501 = check_policy_rules(
        order_id="ORD-1",
        amount=501,
        today=today,
        order=order
    )
    assert result_501["decision"] == "pending_human"
