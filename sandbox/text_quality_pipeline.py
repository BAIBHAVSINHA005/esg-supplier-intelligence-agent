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
    sentence_count: int


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
# first state accumulation exercise
def count_sentences(state: TextPipelineState) -> dict:

    text = state["result"]

    if text:
        sentence_count = text.count(".")            #Runs only if text exists
    else:
        sentence_count = 0

    print(f"[count_sentences] Sentences: {sentence_count}")

    return {
        "sentence_count": sentence_count
    }

def too_short(state: TextPipelineState) -> dict:
    """
    Node 2b: Text is too short — return a message without calling Claude.
    """
    print(f"[too_short] Text has only {state['word_count']} words. Minimum is 50.")
    return {"result": f"TEXT TOO SHORT ({state['word_count']} words). Minimum is 50 words."}


def needs_context(state: TextPipelineState) -> dict:
    """
    Node 2c: Text is in the 50-100 word range.
    Mock implementation — no Claude call required.
    Replace the return value with a real API call once credits are available.
    """
    word_count = state["word_count"]
    print(f"[needs_context] {word_count} words. Moderate length — generating contextual summary (mock).")

    mock_result = (
        f"[MOCK — no API call made] Text contains {word_count} words. "
        f"In production this node calls Claude for a 3-sentence contextual summary. "
        f"Single-sentence summarisation is reserved for texts over 100 words."
    )

    return {"result": mock_result}


# ── 4. ROUTING FUNCTION ────────────────────────────────────────────────────
# This function is called by LangGraph after check_length completes.
# It reads the current state and returns the name of the next node.

def route_by_length(state: TextPipelineState) -> str:
    """
    Three-way routing based on word count.
    Return value must match a key in the add_conditional_edges mapping dict.
    """
    word_count = state["word_count"]

    if word_count < 50:
        return "too_short"
    elif word_count <= 100:
        return "needs_context"
    else:
        return "summarise"


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
    workflow.add_node("needs_context", needs_context)
    workflow.add_node("count_sentences", count_sentences)

    # Set the first node that runs when graph.invoke() is called
    workflow.set_entry_point("check_length")

    # Conditional edge: after check_length, call route_by_length to decide what's next
    # The dict maps each possible return value of route_by_length to a node name
    workflow.add_conditional_edges(
        "check_length",
        route_by_length,
        {
        "too_short":     "too_short",
        "needs_context": "needs_context",
        "summarise":     "summarise"
        }
    )
    

    # too_short and needs_context terminate directly.
    # summarise continues to count_sentences.
    
    workflow.add_edge("too_short", END)
    workflow.add_edge("needs_context", END)

    workflow.add_edge("summarise", "count_sentences")
    workflow.add_edge("count_sentences", END)

   

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
        "result": None,
        "error": None,
        "sentence_count": 0
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
        "result": None,

        "error": None,
        
        "sentence_count": 0
    })
    print(f"Final result: {long_result['result']}")


    # Test 3: Medium text — should route to needs_context
    print("\n" + "=" * 60)
    print("TEST 3: Medium text (50–100 words → needs_context)")
    print("=" * 60)
    medium_text = (
    "BRSR stands for Business Responsibility and Sustainability Report. "
    "It is mandated by SEBI for the top 1000 listed companies in India. "
    "The framework covers nine principles drawn from the National Guidelines "
    "on Responsible Business Conduct. These principles address ethics, "
    "employee wellbeing, environmental protection, and human rights. "
    "Companies must disclose both essential and leadership indicators annually."
)
    medium_result = pipeline.invoke({
    "input_text": medium_text,
    "word_count": 0,
    "is_adequate": False,
    "result": None,
    "sentence_count": 0
    })
    print(f"Final result: {medium_result['result']}")

print("\nFULL FINAL STATE (Test 3):")
for key, value in medium_result.items():
    print(f"  {key}: {value}")

    # Inspect the full final state
    print("\n" + "=" * 60)
    print("FULL FINAL STATE (Test 2):")
    print("=" * 60)
    for key, value in long_result.items():
        print(f"  {key}: {value}")

