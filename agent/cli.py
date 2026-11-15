import sys
import argparse
import uuid
from datetime import date
from agent.graph import create_refund_graph, resume_refund

def run_once(request_text, today=None, input_fn=input, output_fn=print):
    graph = create_refund_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    today_val = today if today is not None else date.today()
    
    result = graph.invoke(
        {
            "request_text": request_text,
            "today": today_val
        },
        config
    )
    
    if "__interrupt__" in result:
        interrupts = result["__interrupt__"]
        if interrupts:
            val = interrupts[0].value
            question = val.get("question") if isinstance(val, dict) else str(val)
            output_fn(question)
        try:
            answer = input_fn("approve or reject: ")
        except (EOFError, KeyboardInterrupt):
            answer = "reject"
        result = resume_refund(graph, thread_id, answer)
        
    decision = result.get("decision")
    reason = result.get("reason")
    audit = result.get("audit", [])
    
    output_fn(decision)
    output_fn(f"Decision: {decision}")
    if reason:
        output_fn(reason)
        output_fn(f"Reason: {reason}")
    for entry in audit:
        output_fn(entry)
        
    return result

def main(argv=None, input_fn=input, output_fn=print):
    parser = argparse.ArgumentParser(description="Refund Approval Agent")
    parser.add_argument("request", nargs="?", help="Refund request text")
    parser.add_argument(
        "--today",
        help="demo only; never use in production",
        type=lambda s: date.fromisoformat(s)
    )
    
    args = parser.parse_args(argv)
    
    request_text = args.request
    if not request_text:
        try:
            request_text = input_fn("Enter refund request: ")
        except TypeError:
            request_text = input_fn()
            
    if args.today is not None:
        output_fn("DEMO: date override in use")
        run_once(request_text, today=args.today, input_fn=input_fn, output_fn=output_fn)
    else:
        run_once(request_text, today=None, input_fn=input_fn, output_fn=output_fn)

if __name__ == "__main__":
    main()
