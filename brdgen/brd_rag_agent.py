from langchain_community.vectorstores import Cassandra
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import cassio

from dotenv import load_dotenv
import os

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("TAVILY_API_KEY")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN,database_id=ASTRA_DB_ID)
print("Cassio initialized. Session: %s", cassio.get_session())

class BRDRAG:
    def __init__(self):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.astra_vector_store=Cassandra(
            embedding=embeddings,
            table_name="brd_gen", 
            session=None,
            keyspace=None
        )
        self.retriever=astra_vector_store.as_retriever()

    def load_documents(document_paths: List[str]) -> List[Dict]:
        documents = []
        for path in document_paths:
            if path.lower().endswith('.pdf'):
                loader = PyPDFLoader(path)
            elif path.lower().endswith(('.docx', '.doc')):
                loader = Docx2txtLoader(path)
            else:
                print(f"Unsupported file type: {path}")
                continue

            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            documents.extend(text_splitter.split_documents(docs))

        return documents
    
    def splitDoc(documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 512,
            chunk_overlap = 128
            )

        splits = text_splitter.split_documents(documents)
        return splits
    
    def loadVector(assessment_document_paths: List[str]):
        documents = load_documents(assessment_document_paths)
        doc_splits = splitDoc(documents)
        self.astra_vector_store.add_documents(doc_splits)
        print("Inserted %i headlines." % len(doc_splits))
    
    def retrieveResult(query: str):
        results = self.retriever.invoke(query, ConsistencyLevel="LOCAL_ONE")
        return results

if __name__ == "__main__":
    brd_rag = BRDRAG()
    assessment_document_paths = [
       'new_assessment.pdf'
    ]
    brd_rag.loadVector(assessment_document_paths)
    print(brd_rag.retrieveResult("What is the purpose of the assessment?"))


