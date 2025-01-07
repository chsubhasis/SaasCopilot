import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pytest
from brdgen.brd_utility import Utility
from brdgen.brd_tool_executor import BRDExternalTool
from brdgen.brd_rag_agent_chroma import BRDRAG
from brdgen.brd_gen_agent import BRDGenerator

"""
def test_text_extract():
    test_file = os.path.join(project_root, "tests/test_files", "test_pdf.pdf")
    result = Utility.extract_text(test_file)
    assert isinstance(result, str)
    assert len(result) > 0


def test_tool_search():
    brdtool = BRDExternalTool()
    result = brdtool.search()
    assert isinstance(result, str)
    assert len(result) > 0
"""

def test_rag_agent():
    brd_rag = BRDRAG()

    assessment_document_paths = ["brdgen/new_assessment.pdf"]
    # brd_rag.loadVector(assessment_document_paths)

    result = brd_rag.getResponse(
        assessment_document_paths, "What is the purpose of the assessment?"
    )
    # pagecontent = result[0].page_content
    # for res in result:
    #    print(res.page_content)
    print(result)
    assert isinstance(result, str)
    assert len(result) > 0, f"Result value: {result}, length: {len(result)}"

"""
def test_gen_agent():
    brd_generator = BRDGenerator(
        api_key=os.getenv("MISTRAL_API"), model="mistral-large-latest"
    )
    rag_results = [
        "Additional context from similar projects...",
        "More additional context...",
    ]
    brd_initial_content = brd_generator.generate_brd(
        assessment_text="Input assessment text...",  # TODO - replace with actual assessment text
        rag_results="\n".join(rag_results),
        save_prompt=True,
    )
    assert isinstance(brd_initial_content.selected_brd, str)
    assert len(brd_initial_content.selected_brd) > 0
"""