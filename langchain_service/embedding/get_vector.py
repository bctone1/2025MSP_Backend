import requests
from langchain_core.embeddings import Embeddings
from .setup import get_embeddings
import numpy as np
from typing import List

def text_to_vector(text):
    embeddings = get_embeddings()
    try:
        vector = embeddings.embed_query(text)
        vector = np.array(vector)
        return vector
    except Exception as e:
        print(f"Error during embedding: {e}")
        return None


class ExaoneEmbeddings(Embeddings):
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        response = requests.post(
            self.api_url,
            headers=headers,
            json={"texts": texts}
        )
        # Exaone이 반환하는 벡터 포맷에 맞게 수정 필요
        return response.json()['embeddings']

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]