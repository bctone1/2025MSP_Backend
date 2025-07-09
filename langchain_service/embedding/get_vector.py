from .setup import get_embeddings
import numpy as np

def text_to_vector(text):
    embeddings = get_embeddings()
    try:
        vector = embeddings.embed_query(text)
        vector = np.array(vector)
        return vector
    except Exception as e:
        print(f"Error during embedding: {e}")
        return None



