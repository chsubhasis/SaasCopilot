from SaasCoplit.brdgen.brd_utility import Utility
from SaasCoplit.brdgen.brd_tool_executor import BRDExternalTool
from SaasCoplit.brdgen.brd_rag_agent import BRDRAG
import os
import pytest


def test_extract_text():
    test_file = os.path.join("tests/test_files", "test_pdf.pdf")
    result = Utility.extract_text(test_file)
    assert isinstance(result, str)
    assert len(result) > 0


def test_tool_search():
    brdtool = BRDExternalTool()
    result = brdtool.search()
    assert isinstance(result, str)
    assert len(result) > 0


def test_retrieve_rag():
    brd_rag = BRDRAG()
    result = brd_rag.retrieveResult("What is the purpose of the assessment?")
    pagecontent = result[0].page_content
    # for res in result:
    #    print(res.page_content)
    assert isinstance(pagecontent, str)
    assert len(pagecontent) > 0
