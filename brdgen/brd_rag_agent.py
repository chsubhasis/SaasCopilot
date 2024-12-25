import os
from typing import Dict, List

import cassio
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain.schema import Document

# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Cassandra

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)


class BRDRAG:
    def __init__(self):
        # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        embeddings = FastEmbedEmbeddings()

        self.astra_vector_store = Cassandra(
            embedding=embeddings, table_name="brd_gen", session=None, keyspace=None
        )
        self.retriever = self.astra_vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 1, "score_threshold": 0.5},
        )

    def load_documents_from_content(self, document_contents: List[str]) -> List[Dict]:
        print("Loading documents from file contents...")
        documents = []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        for content in document_contents:
            doc = Document(page_content=content, metadata={})
            split_docs = text_splitter.split_documents([doc])
            documents.extend(split_docs)

        return documents

    def load_documents_from_path(self, document_paths: List[str]) -> List[Dict]:
        print("Loading documents from file paths...")
        documents = []
        for path in document_paths:
            if path.lower().endswith(".pdf"):
                loader = PyPDFLoader(path)
            elif path.lower().endswith((".docx", ".doc")):
                loader = Docx2txtLoader(path)
            else:
                print(f"Unsupported file type: {path}")
                continue

            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=50
            )
            documents.extend(text_splitter.split_documents(docs))

        return documents

    def splitDoc(self, documents):
        print("Splitting documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=128
        )

        splits = text_splitter.split_documents(documents)
        return splits

    def loadVector(self, assessment_document_paths: List[str]):
        print("Loading vectors...")
        documents = self.load_documents(assessment_document_paths)
        doc_splits = self.splitDoc(documents)
        self.astra_vector_store.add_documents(doc_splits)
        print("Inserted %i splits." % len(doc_splits))

    def retrieveResult(self, query: str):
        print("Retrieving results...")
        results = self.retriever.invoke(query)
        return results
