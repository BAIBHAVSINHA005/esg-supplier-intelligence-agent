from app.extraction.llm_extractor import LLMExtractor

extractor = LLMExtractor()

result = extractor.extract_indicator(
    indicator_id="ENV-1",
    indicator_name="Total Water Consumption",
    indicator_description="Total water consumed during the reporting period.",
    context="""
The company consumed 1,250 KL of water during FY2025.
""",
)

print(result)