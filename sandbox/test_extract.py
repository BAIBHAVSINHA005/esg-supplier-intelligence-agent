# "D:\Portfolio_projects\esg-supplier-intelligence-agent\sandbox\test_extract.py"

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent)
)

from app.agent.nodes.extract import extract_indicators
test_state = {
    "supplier_name": "ABC Manufacturing Ltd",
    "assessment_id": "TEST_001",
    "brsr_section_text": (
        "Business Responsibility and Sustainability Report "
        "placeholder section content."
    ),
}

result = extract_indicators(test_state)

print("\nReturned State Updates:")

for key, value in result.items():
    print(f"{key}: {value}")