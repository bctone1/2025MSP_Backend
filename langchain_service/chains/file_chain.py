from langchain.chains import SequentialChain
from langchain_service.document_loaders.file_loader import load_document
from langchain_service.document_loaders.indexer import split_documents, index_documents


def get_qa_chain(file_path):

    file_chain = SequentialChain(

    )

    return file_chain

