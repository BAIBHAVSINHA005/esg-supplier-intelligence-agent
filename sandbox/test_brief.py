from app.agent.nodes.brief import compile_brief

test_state = {
    "supplier_name": "ABC Manufacturing Ltd",
    "source_filename": "test_brsr.pdf",
    "assessment_id": "TEST001",

    "confidence_level": "high",
    "confidence_directive": "Placeholder directive",
    "hitl_flag": False,

    "completeness_results": [],
    "scope3_verdict": {
        "level": "not_found"
    },
    "gaps": [],
    "followup_questions": [],
    "uncertain_fields": [],
}

result = compile_brief(test_state)

print("\nReturned State Updates:")

for key, value in result.items():
    print(f"{key}: {value}")