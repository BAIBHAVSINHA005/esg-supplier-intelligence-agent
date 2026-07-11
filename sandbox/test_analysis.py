from app.agent.nodes.analysis import analysis_layer


test_state = {
    "supplier_name": "ABC Manufacturing Ltd",

    "brsr_section_text": (
        "Placeholder BRSR disclosure text."
    ),

    "extracted_indicators": {
        "principle_6": {
            "scope_3_emissions": {
                "state": "not_found",
                "value": "",
                "citation": (
                    "PLACEHOLDER: real citation will appear here"
                )
            }
        }
    }
}


result = analysis_layer(test_state)

print("\nReturned State Updates:")

for key, value in result.items():
    print(f"{key}: {value}")