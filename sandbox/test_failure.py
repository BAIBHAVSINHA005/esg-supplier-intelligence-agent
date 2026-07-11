from app.agent.nodes.failure import handle_failure

test_state = {
    "supplier_name": "ABC Manufacturing Ltd",
    "source_filename": "corrupt_file.pdf",
    "assessment_id": "TEST001",

    "document_failure_reason":
        "PDF contains no machine-readable text."
}

result = handle_failure(test_state)

print("\nReturned State Updates:")

for key, value in result.items():
    print(f"{key}: {value}")