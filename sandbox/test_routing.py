from app.agent.edges.routing import route_after_quality_check

print("SUCCESS CASE")

state = {
    "document_failure": False
}

print(route_after_quality_check(state))

print("\nFAILURE CASE")

state = {
    "document_failure": True
}

print(route_after_quality_check(state))