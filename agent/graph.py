from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver
from agent.state import RefundState
from agent.policy import normalize_human_answer
from agent.nodes import (
    parse_request,
    lookup_order,
    check_policy_node,
    human_approval,
    finalize_node
)


def route_after_policy(state: RefundState) -> str:
    if state.get("decision") == "pending_human":
        return "human_approval"
    return "finalize"

def create_refund_graph():
    workflow = StateGraph(RefundState)
    
    workflow.add_node("parse_request", parse_request)
    workflow.add_node("lookup_order", lookup_order)
    workflow.add_node("check_policy", check_policy_node)
    workflow.add_node("human_approval", human_approval)
    workflow.add_node("finalize", finalize_node)
    
    workflow.add_edge(START, "parse_request")
    workflow.add_edge("parse_request", "lookup_order")
    workflow.add_edge("lookup_order", "check_policy")
    
    workflow.add_conditional_edges(
        "check_policy",
        route_after_policy,
        {
            "human_approval": "human_approval",
            "finalize": "finalize"
        }
    )
    
    workflow.add_edge("human_approval", "finalize")
    workflow.add_edge("finalize", END)
    
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)

def resume_refund(graph, thread_id: str, answer: Any) -> Dict[str, Any]:
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    if "human_approval" not in snapshot.next:
        raise ValueError("No pending approval for this thread")
    normalized = normalize_human_answer(answer)
    return graph.invoke(
        Command(resume=normalized),
        config
    )

