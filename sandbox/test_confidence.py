#

from app.agent.nodes.confidence import assess_confidence

test_state = {
    "extraction_confidence_score": 0.9,
    "extracted_indicators": {},
}

result = assess_confidence(test_state)

print("\nReturned State Updates:")

for key, value in result.items():
    print(f"{key}: {value}")