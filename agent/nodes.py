import re
from datetime import date
from typing import Dict, Any
from langgraph.types import interrupt
from agent.state import RefundState
from agent.policy import check_policy_rules, normalize_human_answer

MOCK_ORDERS = {
    "ORD-123": {"total": 1000, "date": date(2026, 6, 1)},
    "ORD-999": {"total": 500, "date": date(2026, 5, 15)},
    "ORD-OLD": {"total": 2000, "date": date(2026, 4, 1)},
}

def parse_request(state: RefundState) -> Dict[str, Any]:
    text = state["request_text"]
    
    order_id_match = re.search(r"(ORD-[A-Za-z0-9_-]+)", text, re.IGNORECASE)
    order_id = order_id_match.group(1) if order_id_match else None
    
    clean_text = re.sub(r"\d{4}-\d{2}-\d{2}", "", text)
    clean_text = re.sub(r"ORD-[A-Za-z0-9_-]+", "", clean_text, flags=re.IGNORECASE)
    
    amounts = re.findall(r"\b(\d+)\b", clean_text)
    amount = int(amounts[0]) if amounts else 0
    
    return {
        "order_id": order_id,
        "amount": amount,
        "audit": [f"Parsed request: order_id={order_id}, amount={amount}"]
    }

def lookup_order(state: RefundState) -> Dict[str, Any]:
    order_id = state.get("order_id")
    order = MOCK_ORDERS.get(order_id) if order_id else None
    return {
        "order": order,
        "audit": [f"Looked up order {order_id}: found={order is not None}"]
    }

def check_policy_node(state: RefundState) -> Dict[str, Any]:
    result = check_policy_rules(
        order_id=state.get("order_id"),
        amount=state.get("amount", 0),
        today=state.get("today"),
        order=state.get("order")
    )
    decision = result["decision"]
    reason = result["reason"]
    return {
        "decision": decision,
        "reason": reason,
        "audit": [f"Policy check: decision={decision}, reason={reason}"]
    }

def human_approval(state: RefundState) -> Dict[str, Any]:
    answer = interrupt({
        "question": f"Refund of {state.get('amount')} for order {state.get('order_id')} requires human approval.",
        "order_id": state.get("order_id"),
        "amount": state.get("amount")
    })
    
    human_decision = normalize_human_answer(answer)
    decision = "approved" if human_decision == "approve" else "rejected"
    reason = f"Human reviewer decided: {human_decision}"
    
    return {
        "human_decision": human_decision,
        "decision": decision,
        "reason": reason,
        "audit": [f"Human approval processed: answer={human_decision}, decision={decision}"]
    }

def finalize_node(state: RefundState) -> Dict[str, Any]:
    decision = state.get("decision")
    reason = state.get("reason")
    return {
        "decision": decision,
        "reason": reason,
        "audit": [f"Finalized refund process: decision={decision}, reason={reason}"]
    }
