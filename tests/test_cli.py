import pytest
from datetime import date
from agent import cli

def test_run_once_auto_approval():
    outputs = []
    inputs_called = [0]
    def fake_input(prompt=""):
        inputs_called[0] += 1
        return "approve"
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 200 for order ORD-123",
        today=date(2026, 6, 5),
        input_fn=fake_input,
        output_fn=fake_output
    )
    assert state["decision"] == "approved"
    assert inputs_called[0] == 0

def test_run_once_human_approval_approved():
    outputs = []
    inputs_called = [0]
    def fake_input(prompt=""):
        inputs_called[0] += 1
        return "approve"
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 600 for order ORD-123",
        today=date(2026, 6, 5),
        input_fn=fake_input,
        output_fn=fake_output
    )
    assert state["decision"] == "approved"
    assert inputs_called[0] == 1

@pytest.mark.parametrize("answer", ["reject", "banana", "APPROVE"])
def test_run_once_human_approval_rejected_answers(answer):
    outputs = []
    def fake_input(prompt=""):
        return answer
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 600 for order ORD-123",
        today=date(2026, 6, 5),
        input_fn=fake_input,
        output_fn=fake_output
    )
    assert state["decision"] == "rejected"

@pytest.mark.parametrize("exc", [EOFError, KeyboardInterrupt])
def test_run_once_input_exception_rejects(exc):
    outputs = []
    def fake_input(prompt=""):
        raise exc("interrupted")
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 600 for order ORD-123",
        today=date(2026, 6, 5),
        input_fn=fake_input,
        output_fn=fake_output
    )
    assert state["decision"] == "rejected"

def test_run_once_old_order_rejected():
    outputs = []
    inputs_called = [0]
    def fake_input(prompt=""):
        inputs_called[0] += 1
        return "approve"
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 100 for order ORD-OLD",
        today=date(2026, 6, 5),
        input_fn=fake_input,
        output_fn=fake_output
    )
    assert state["decision"] == "rejected"
    assert inputs_called[0] == 0

def test_run_once_output_contains_decision_reason_and_audit():
    outputs = []
    def fake_input(prompt=""):
        return "approve"
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 200 for order ORD-123",
        today=date(2026, 6, 5),
        input_fn=fake_input,
        output_fn=fake_output
    )
    
    combined = "\n".join(outputs)
    assert state["decision"] in combined
    assert state["reason"] in combined
    for entry in state["audit"]:
        assert entry in combined

def test_run_once_order_age_days_in_output():
    outputs = []
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    state = cli.run_once(
        "Refund 100 for order ORD-123 on 2026-06-04",
        today=date(2026, 11, 15),
        output_fn=fake_output
    )
    combined = "\n".join(outputs)
    assert state["decision"] == "rejected"
    assert "167 days" in combined

def test_main_today_override_and_demo_message():
    outputs = []
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    cli.main(["Refund 200 for order ORD-123", "--today", "2026-06-05"], output_fn=fake_output)
    combined = "\n".join(outputs)
    assert "DEMO: date override in use" in combined
    assert "approved" in combined.lower()

def test_main_without_today_never_prints_demo():
    outputs = []
    def fake_input(prompt=""):
        return "Refund 200 for order ORD-123"
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    cli.main([], input_fn=fake_input, output_fn=fake_output)
    combined = "\n".join(outputs)
    assert "DEMO: date override in use" not in combined

def test_main_invalid_today_exits():
    outputs = []
    def fake_output(msg=""):
        outputs.append(str(msg))
        
    with pytest.raises(SystemExit):
        cli.main(["x", "--today", "2026-13-45"], output_fn=fake_output)
