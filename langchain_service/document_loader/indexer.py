from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_service.embedding.get_vector import text_to_vector
from typing import List
from langchain.schema import Document
from sqlalchemy.orm import Session
from crud.llm import save_info
# import kss
# from langchain.text_splitter import TextSplitter

def split_documents(documents: List[Document], chunk_size=1500, chunk_overlap=400):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

def index_documents(db: Session, id : int, documents: List[Document], use_pgvector=True):
    chunks = split_documents(documents)
    if use_pgvector:
        vectors = [text_to_vector(chunk.page_content) for chunk in chunks]
        texts = [chunk.page_content for chunk in chunks]
    for idx, chunk in enumerate(chunks):
        content = chunk.page_content
        vector_memory = vectors[idx]

        save_info(db=db, infobase_id=id, content = content, vector_memory = vector_memory)



# 한국어 전용 Text Splitter
# class KssTextSplitter(TextSplitter):
#     def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
#         super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#
#     def split_text(self, text: str):
#         sentences = kss.split_sentences(text)
#         chunks, current_chunk = [], ""
#
#         for sentence in sentences:
#             if len(current_chunk) + len(sentence) > self._chunk_size:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = current_chunk[-self._chunk_overlap:] + sentence
#             else:
#                 if current_chunk:
#                     current_chunk += " " + sentence
#                 else:
#                     current_chunk = sentence
#
#         if current_chunk:
#             chunks.append(current_chunk.strip())
#
#         return chunks


