from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import numpy as np
import faiss

load_dotenv(override=True)


def pdfRAG(file_path: str, question: str | None = None) -> str:
    """Load a PDF file and answer a question about its content."""
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

    _ = vectorstore.index.reconstruct(0)
    n_vectors = vectorstore.index.ntotal
    _ = np.array([vectorstore.index.reconstruct(i) for i in range(n_vectors)])

    retriever = vectorstore.as_retriever()

    prompt = PromptTemplate.from_template(
        """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Answer in Korean.

#Question:
{question}
#Context:
{context}

#Answer:"""
    )

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    chain = (
        {"context": retriever | docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(question)
    return response
