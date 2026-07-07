# text_quality_pipeline.py
# Run with: python text_quality_pipeline.py

import os
from typing import TypedDict, Literal, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from anthropic import Anthropic

# ── 1. INSTALL DEPENDENCIES ─
# pip install langgraph anthropic
# Set ANTHROPIC_API_KEY in your environment before running.

load_dotenv()

key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic()

# ── 2. STATE DEFINITION ─
# This is the shared state object. Every node reads from and writes to this.
# TypedDict gives you type hints — LangGraph works with plain dicts too,
# but TypedDict makes your code readable and debuggable.

class TextPipelineState(TypedDict):
    # Input
    input_text: str

    # Written by check_length node
    word_count: int
    is_adequate: bool                              # True if >= 50 words

    # Written by summarise or too_short node
    result: Optional[str]
    error: Optional[str]                            #Extending TypeDict, adding error to state


# ── 3. NODE FUNCTIONS ──────────────────────────────────────────────────────
# Each node is a plain Python function.
# It receives the current state dict.
# It returns a dict of ONLY the fields it wants to update.
# LangGraph merges this returned dict into the existing state automatically.
# You never return the full state — only your changes.

def check_length(state: TextPipelineState) -> dict:
    """
    Node 1: Count words and decide if the text is long enough to summarise.
    No LLM call — pure Python logic.
    """
    text = state["input_text"]
    word_count = len(text.split())
    is_adequate = word_count >= 50

    print(f"[check_length] Word count: {word_count}. Adequate: {is_adequate}")

    # Return ONLY the fields this node writes
    return {
        "word_count": word_count,
        "is_adequate": is_adequate 
    }


def summarise(state: TextPipelineState) -> dict:
    """
    Node 2a: Text is long enough — summarise it using Claude.
    """
    text = state["input_text"]
    print(f"[summarise] Calling Claude to summarise {state['word_count']} words...")

    try: 
        response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Summarise the following text in exactly one sentence:\n\n{text}"
        }]
        )

        summary = response.content[0].text.strip()
        print(f"[summarise] Result: {summary}")

        return {"result": f"SUMMARY: {summary}"}
    except Exception as e:
        print(f"[summarise] Error: {e}")
        return {
            "result": None, 
            "error": str(e)
        }


def too_short(state: TextPipelineState) -> dict:
    """
    Node 2b: Text is too short — return a message without calling Claude.
    """
    print(f"[too_short] Text has only {state['word_count']} words. Minimum is 50.")
    return {"result": f"TEXT TOO SHORT ({state['word_count']} words). Minimum is 50 words."}


# ── 4. ROUTING FUNCTION ────────────────────────────────────────────────────
# This function is called by LangGraph after check_length completes.
# It reads the current state and returns the name of the next node.

def route_by_length(state: TextPipelineState) -> str:
    """
    Conditional routing: decide which node to go to next.
    Return the node NAME as a string — must match a registered node name.
    """
    if state["is_adequate"]:
        return "summarise"
    else:
        return "too_short"


# ── 5. GRAPH ASSEMBLY ──────────────────────────────────────────────────────

def build_pipeline():
    """Build, compile, and return the LangGraph pipeline."""

    # Create a graph that uses TextPipelineState as its state type
    workflow = StateGraph(TextPipelineState)

    # Register nodes: (node_name, node_function)
    # node_name is the string used in routing and edge definitions
    workflow.add_node("check_length", check_length)
    workflow.add_node("summarise", summarise)
    workflow.add_node("too_short", too_short)

    # Set the first node that runs when graph.invoke() is called
    workflow.set_entry_point("check_length")

    # Conditional edge: after check_length, call route_by_length to decide what's next
    # The dict maps each possible return value of route_by_length to a node name
    workflow.add_conditional_edges(
        "check_length",              # Source node
        route_by_length,             # Routing function
        {
            "summarise": "summarise",    # If route_by_length returns "summarise" → go to "summarise"
            "too_short": "too_short"     # If route_by_length returns "too_short" → go to "too_short"
        }
    )

    # Both terminal nodes go straight to END
    workflow.add_edge("summarise", END)
    workflow.add_edge("too_short", END)

    # Compile the graph — this validates the structure and returns a runnable object
    return workflow.compile()


# ── 6. RUN THE PIPELINE ────────────────────────────────────────────────────

if __name__ == "__main__":
    pipeline = build_pipeline()

    # Test 1: Short text (should route to too_short)
    print("\n" + "=" * 60)
    print("TEST 1: Short text")
    print("=" * 60)
    short_result = pipeline.invoke({
        "input_text": "This is a very short piece of text.",
        "word_count": 0,        # LangGraph needs all TypedDict keys at invocation
        "is_adequate": False,   # These will be overwritten by check_length
        "result": None
    })
    print(f"Final result: {short_result['result']}")

    # Test 2: Long text (should route to summarise and call Claude)
    print("\n" + "=" * 60)
    print("TEST 2: Long text")
    print("=" * 60)
    long_text = """
    Business Responsibility and Sustainability Reporting represents a significant
    evolution in corporate disclosure requirements in India. Mandated by SEBI for
    the top 1000 listed companies by market capitalisation, BRSR requires companies
    to disclose their performance across nine principles of the National Guidelines on
    Responsible Business Conduct. These principles cover ethics, sustainable products,
    employee wellbeing, stakeholder responsiveness, human rights, environmental
    protection, public policy, inclusive growth, and consumer responsibility.
    The framework is designed to create a standardised basis for ESG assessment
    and improve transparency in the Indian capital markets.
    """
    long_result = pipeline.invoke({
        "input_text": long_text,
        "word_count": 0,
        "is_adequate": False,
        "result": None
    })
    print(f"Final result: {long_result['result']}")

    # Inspect the full final state
    print("\n" + "=" * 60)
    print("FULL FINAL STATE (Test 2):")
    print("=" * 60)
    for key, value in long_result.items():
        print(f"  {key}: {value}")

