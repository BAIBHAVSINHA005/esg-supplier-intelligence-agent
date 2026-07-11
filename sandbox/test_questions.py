from app.agent.nodes.questions import generate_questions

test_state = {
    "supplier_name": "ABC Manufacturing Ltd",
    "gaps": [
        {
            "gap_id": "G-01",
            "severity": "critical"
        }
    ]
}

result = generate_questions(test_state)

print("\nReturned State Updates:")

for key, value in result.items():
    print(f"{key}: {value}")