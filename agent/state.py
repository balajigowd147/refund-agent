from typing import TypedDict, Annotated, Optional
import operator
from datetime import date

class RefundState(TypedDict):
    request_text: str
    order_id: Optional[str]
    amount: int
    today: Optional[date]
    order: Optional[dict]
    decision: Optional[str]
    reason: Optional[str]
    human_decision: Optional[str]
    audit: Annotated[list[str], operator.add]
