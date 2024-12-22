from typing import TypedDict


class BRDState(TypedDict):
    assessment_text: str
    brd_content: str | None
    iteration_count: int
    rag_result: str | None
