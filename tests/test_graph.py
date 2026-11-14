import pytest
from datetime import date
from langgraph.types import Command
from agent.graph import create_refund_graph

def test_auto_approval_graph():
    graph = create_refund_graph()
    config = {"configurable": {"thread_id": "test-thread-1"}}
    
    result = graph.invoke(
        {"request_text": "Refund 200 for order ORD-123", "today": date(2026, 6, 1)},
        config
    )
    assert result["decision"] == "approved"
    assert len(result["audit"]) > 0

def test_rejection_graph():
    graph = create_refund_graph()
    config = {"configurable": {"thread_id": "test-thread-2"}}
    
    result = graph.invoke(
        {"request_text": "Refund 9999 for order ORD-123", "today": date(2026, 6, 1)},
        config
    )
    assert result["decision"] == "rejected"

def test_human_approval_pause_and_approve():
    graph = create_refund_graph()
    config = {"configurable": {"thread_id": "test-thread-3"}}
    
    # First invoke: should pause at human_approval (> 500)
    paused = graph.invoke(
        {"request_text": "Refund 600 for order ORD-123", "today": date(2026, 6, 1)},
        config
    )
    assert "__interrupt__" in paused
    interrupts = paused["__interrupt__"]
    assert len(interrupts) > 0
    assert interrupts[0].value["amount"] == 600
    
    # Second invoke: resume with "approve"
    resumed = graph.invoke(Command(resume="approve"), config)
    assert resumed["decision"] == "approved"
    assert resumed["human_decision"] == "approve"

def test_human_approval_pause_and_reject():
    graph = create_refund_graph()
    config = {"configurable": {"thread_id": "test-thread-4"}}
    
    paused = graph.invoke(
        {"request_text": "Refund 800 for order ORD-123", "today": date(2026, 6, 1)},
        config
    )
    assert "__interrupt__" in paused
    
    # Resume with "reject"
    resumed = graph.invoke(Command(resume="reject"), config)
    assert resumed["decision"] == "rejected"
    assert resumed["human_decision"] == "reject"

@pytest.mark.parametrize("resume_val, expected_decision", [
    ("approve", "approved"),
    ("APPROVE", "rejected"),
    (" approve ", "rejected"),
    ("NONE", "rejected"),
    (True, "rejected"),
    ({}, "rejected"),
])
def test_human_approval_strict_matching(resume_val, expected_decision):
    graph = create_refund_graph()
    config = {"configurable": {"thread_id": f"test-thread-strict-{str(resume_val)}"}}
    
    paused = graph.invoke(
        {"request_text": "Refund 600 for order ORD-123", "today": date(2026, 6, 1)},
        config
    )
    assert "__interrupt__" in paused
    
    if resume_val == "NONE":
        resumed = graph.invoke(None, config)
    else:
        resumed = graph.invoke(Command(resume=resume_val), config)
    assert resumed["decision"] == expected_decision

def test_audit_log_full_human_approved_and_policy_rejected():
    graph = create_refund_graph()
    
    # 1. Full human-approved run: 5 nodes (parse_request, lookup_order, check_policy_node, human_approval, finalize_node)
    config1 = {"configurable": {"thread_id": "test-thread-audit-1"}}
    paused = graph.invoke(
        {"request_text": "Refund 600 for order ORD-123", "today": date(2026, 6, 1)},
        config1
    )
    resumed = graph.invoke(Command(resume="approve"), config1)
    audit = resumed["audit"]
    assert len(audit) == 5
    assert any("Parsed request" in entry for entry in audit)
    assert any("Looked up order" in entry for entry in audit)
    assert any("Policy check" in entry for entry in audit)
    assert any("Human approval" in entry for entry in audit)
    assert any("Finalized refund process" in entry for entry in audit)

    # 2. Rejected-by-policy run: no human_approval entry (4 nodes)
    config2 = {"configurable": {"thread_id": "test-thread-audit-2"}}
    result2 = graph.invoke(
        {"request_text": "Refund 9999 for order ORD-123", "today": date(2026, 6, 1)},
        config2
    )
    audit2 = result2["audit"]
    assert len(audit2) == 4
    assert not any("Human approval" in entry for entry in audit2)

def test_graph_today_from_initial_state():
    graph = create_refund_graph()
    config = {"configurable": {"thread_id": "test-thread-today"}}
    result = graph.invoke(
        {
            "request_text": "Refund 100 for order ORD-OLD on 2026-04-05",
            "today": date(2026, 6, 1)
        },
        config
    )
    assert result["decision"] == "rejected"
