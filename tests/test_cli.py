import pytest
from unittest.mock import patch
from datetime import date

@pytest.fixture(autouse=True)
def mock_today():
    with patch("agent.cli.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 1)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        yield

def test_cli_auto_approval(monkeypatch, capsys):
    from agent import cli
    
    # Mock user entering a refund request that is auto-approved (e.g. amount <= 500)
    monkeypatch.setattr("builtins.input", lambda _: "Refund 200 for order ORD-123")
    
    cli.main()
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Refund Agent" in output
    assert "approved" in output.lower()
    assert "audit" in output.lower() or "Parsed request" in output

def test_cli_human_approval(monkeypatch, capsys):
    from agent import cli
    
    # First input: refund request requiring human approval (> 500)
    # Second input: "approve" when prompted
    inputs = iter(["Refund 600 for order ORD-123", "approve"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    
    cli.main()
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Refund Agent" in output
    assert "ORD-123" in output
    assert "600" in output
    assert "approved" in output.lower()
    assert "audit" in output.lower() or "Human approval" in output

def test_cli_human_rejection(monkeypatch, capsys):
    from agent import cli
    
    # First input: refund request requiring human approval (> 500)
    # Second input: "reject" when prompted
    inputs = iter(["Refund 600 for order ORD-123", "reject"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    
    cli.main()
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Refund Agent" in output
    assert "ORD-123" in output
    assert "600" in output
    assert "rejected" in output.lower()
    assert "audit" in output.lower()

def test_cli_displays_audit_log_and_decision(monkeypatch, capsys):
    from agent import cli
    
    monkeypatch.setattr("builtins.input", lambda _: "Refund 150 for order ORD-123")
    
    cli.main()
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Decision" in output or "decision" in output.lower()
    assert "Audit" in output or "audit" in output.lower()
    assert "Parsed request" in output
