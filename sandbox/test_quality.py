from app.agent.nodes.quality import quality_check

test_state = {
    "source_filename": "test_brsr.pdf",
    "document_text": (
        "Business Responsibility and Sustainability Report "
        "placeholder content."
    ),
}

result = quality_check(test_state)

print("\nReturned State Updates:")
for key, value in result.items():
    print(f"{key}: {value}")