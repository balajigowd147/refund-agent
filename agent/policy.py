from datetime import date
from typing import Optional, Dict, Any

def check_policy_rules(
    order_id: Optional[str],
    amount: int,
    today: Optional[date],
    order: Optional[dict]
) -> Dict[str, Any]:
    if not order_id or order is None:
        return {"decision": "rejected", "reason": "Unknown order"}
    
    if amount <= 0:
        return {"decision": "rejected", "reason": "Amount must be greater than 0"}
    
    if amount > order.get("total", 0):
        return {"decision": "rejected", "reason": "Amount exceeds order total"}
    
    order_date = order.get("date")
    if order_date:
        if today is None:
            return {"decision": "rejected", "reason": "Cannot verify order age"}
        age_days = (today - order_date).days
        if age_days > 30:
            return {"decision": "rejected", "reason": f"Order is {age_days} days old, exceeding 30-day limit"}
            
    if amount <= 500:
        return {"decision": "approved", "reason": f"Amount {amount} is within auto-approval threshold (<= 500)"}
    else:
        return {"decision": "pending_human", "reason": f"Amount {amount} exceeds 500, requires human approval"}

def normalize_human_answer(answer: Any) -> str:
    if answer == "approve":
        return "approve"
    return "reject"
