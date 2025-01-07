from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_chroma import Chroma
from langchain.schema import Document
import torch
import re, unicodedata, os
from dotenv import load_dotenv

load_dotenv()

class BRDRAG:
    def load_documents(self, document_paths: List[str]) -> List[Dict]:
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
    
    def load_documents_content(self, content: str) -> List[Document]:
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(content)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents

    def splitDoc(self, documents):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=128
        )

        splits = text_splitter.split_documents(documents)
        return splits

    def getEmbedding(
        self,
    ):
        """
        modelPath = "mixedbread-ai/mxbai-embed-large-v1"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_kwargs = {"device": device}  # cuda/cpu
        encode_kwargs = {"normalize_embeddings": False}

        embedding = HuggingFaceEmbeddings(
            model_name=modelPath, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )
        """
        
        embeddings = FastEmbedEmbeddings()
        return embeddings


    def is_chroma_db_present(self, directory: str):
        # Check if the directory exists and contains any files.
        return os.path.exists(directory) and len(os.listdir(directory)) > 0

    def getResponse(self, assessment_document_content: str, query: str) -> str:
        documents = self.load_documents_content(assessment_document_content)
        splits = self.splitDoc(documents)
        embeddings = self.getEmbedding()
        persist_directory = "docs/chroma/"

        if self.is_chroma_db_present(persist_directory):
            print(
                f"Chroma vector DB found in '{persist_directory}' and will be loaded."
            )
            # Load vector store from the local directory
            vectordb = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.getEmbedding(),
            )
        else:
            vectordb = Chroma.from_documents(
                documents=splits,  # splits we created earlier
                embedding=embeddings,
                persist_directory=persist_directory,  # save the directory
            )

        question = query
        docs = vectordb.search(question, search_type="mmr", k=5)
        response = ""
        for i in range(len(docs)):
            response = response + docs[i].page_content

        return response
