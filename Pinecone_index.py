from typing import List, Dict
from tqdm.auto import tqdm  # for progress bar

import pinecone


class PineconeIndex:
    def __init__(self, index_name: str):
        self.index = self.connect_to_index(index_name)

    def connect_to_index(self, index_name):
        """Connects to pinecone index matching the user-provided index_name. If the index doesn't exist, create it with name index_name"""
        pinecone.init(api_key="7a96d287-9c61-4335-adf7-636892d6e2a5",
                      environment='us-west1-gcp')
        # check if index already exists, if not we create it
        if index_name not in pinecone.list_indexes():
            print(
                f'Index with name "{index_name}" not found. Creating index with name "{index_name}"...')
            # TODO: Don't hardcode dim 384. Get the length of the embedding
            pinecone.create_index(name=index_name, dimension=384)
            print("Created index with name ", index_name)
        # connect to index
        index = pinecone.Index(index_name)
        print(f"Connected to index '{index_name}'")
        return index

    def upsert(self, data: List[Dict], namespace: str = None):
        """
        data is a list of dictionaries containing a single context and its associated metadata
        data requires at least the following keys (can also contain metadata):
          'id' -> string
         'context' -> string
         'encoding' -> List[Float]

        media vectors (ie youtube videos and podcasts) can also have a 'start (ms)' field, representing the timestamp of the paragraph/sentence
        """

        # upserts = [(v['id'], v['encoding'], {'context': v['context'], 'start (ms)': v['start (ms)']}) for v in data]
        # upserts = [(v['encoding'], {'context': v['context']}) for v in data]

        # now upsert in chunks
        for i in tqdm(range(0, len(data), 50)):
            i_end = i + 50
            if i_end > len(data):
                i_end = len(data)
            self.index.upsert(vectors=data[i:i_end], namespace=namespace)
        print("Done upserting!")

    def delete_namespace(self, namespace):
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            print("Deleted the namespace ", namespace)
        except:
            raise NameError(f"Namespace {namespace} not found")

    def query(self, query_emb: List[float], top_k=5, namespace=None) -> Dict:
        # the Pinecone .query() method expects an array of query vectors, which is why we wrap our query embedding (which is itself a list) in a list
        # we want the metadata to be included in the returned JSON because the context text is in the metadata dictionary
        return self.index.query([query_emb], top_k=top_k, namespace=namespace, include_metadata=True)
