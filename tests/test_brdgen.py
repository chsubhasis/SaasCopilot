from SaasCoplit.brdgen.brd_utility import Utility
from SaasCoplit.brdgen.brd_tool_executor import BRDExternalTool
from SaasCoplit.brdgen.brd_rag_agent import BRDRAG
from SaasCoplit.brdgen.brd_gen_agent import BRDGenerator
import os
import pytest

"""
def test_text_extract():
    test_file = os.path.join("tests/test_files", "test_pdf.pdf")
    result = Utility.extract_text(test_file)
    assert isinstance(result, str)
    assert len(result) > 0


def test_tool_search():
    brdtool = BRDExternalTool()
    result = brdtool.search()
    assert isinstance(result, str)
    assert len(result) > 0


def test_rag_agent():
    brd_rag = BRDRAG()
    
    #assessment_document_paths = [
    #   'new_assessment.pdf'
    #]
    brd_rag.loadVector(assessment_document_paths)
    
    result = brd_rag.retrieveResult("What is the purpose of the assessment?")
    pagecontent = result[0].page_content
    # for res in result:
    #    print(res.page_content)
    assert isinstance(pagecontent, str)
    assert len(pagecontent) > 0

"""

def test_gen_agent():
    brd_generator = BRDGenerator(api_key=os.getenv("MISTRAL_API"), model="mistral-large-latest")
    brd_initial_content = brd_generator.generate_brd("This is a test assessment")
    assert isinstance(brd_initial_content, str)
    assert len(brd_initial_content) > 0

"""
def test_reflexion_agent():
    pass

def test_workflow():
    pass
"""
