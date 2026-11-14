import uuid
from datetime import date
from agent.graph import create_refund_graph, resume_refund

def main():
    print("=== Refund Agent ===")
    request_text = input("Enter refund request: ")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    graph = create_refund_graph()
    
    result = graph.invoke(
        {
            "request_text": request_text,
            "today": date.today()
        },
        config
    )
    
    # Check if paused for human approval
    if "__interrupt__" in result:
        interrupts = result["__interrupt__"]
        if interrupts:
            val = interrupts[0].value
            order_id = val.get("order_id")
            amount = val.get("amount")
            print(f"Refund of {amount} for order {order_id} requires human approval.")
            print(f"Order ID: {order_id}")
            print(f"Amount: {amount}")
            
        answer = input("Type 'approve' or 'reject': ")
        result = resume_refund(graph, thread_id, answer)
        
    decision = result.get("decision")
    print(f"Decision: {decision}")
    
    print("Audit Log:")
    for entry in result.get("audit", []):
        print(f" - {entry}")

if __name__ == "__main__":
    main()
