from typing import List, Dict, Union

from pinecone_index import PineconeIndex


class Controller:
    def __init__(self, retriever_model, index: PineconeIndex):
        self.retriever_model = retriever_model
        self.index = index
        # self.embedding_dims = self.get_pinecone_embedding_dims()

    # TRANSFORMING DATA
    def get_embedding(self, x: str):
        """
        Computes and returns the vector embedding of the string x
        """
        return self.retriever_model.encode(x).tolist()

    def transform_data(self, data):
        """
        Adds the encoding of the context to each dictionary in data and adds the encoding as a value to each dict item (each item representing a specific context) in the data list of dicts.
        Returns this new modified list of dictionaries. Modifies in-place
        Example input data:
          [
            {'context': 'Hello World!', 'id': '123'},
           {'context': 'My name is Chris', 'id': '988767'}
          ]
        Output:
          [
            {'context': 'Hello World!', 'id': '123', 'encoding': [.42, -.23, .25]},
           {'context': 'My name is Chris', 'id': '988767', 'encoding': [.86, -.99, .12]}
          ]
        """

        def encode_context(d):
            """
            Encodes the context for a particular dictionary of data and adds the vector embedding as an item in the dictionary
            """
            d["encoding"] = self.get_embedding(d["context"])
            return d

        return list(map(encode_context, data))

    # INTERFACING WITH INDEX
    def upsert(self, data: List[Dict], namespace: str, metadata_fields=[]):
        """
        Transforms the un-encoded, raw data and upserts them to the Pinecone Index under the provided namespace.
        data is a list of dictionaries, each dictionary containing a single context and its associated metadata.
        data requires at least the following keys (can also contain metadata):
          Required keys in data:
            'id' -> string
            'context' -> string
          Optional key(s):
            'start (ms)' -> int
        """
        encoded_data = self.transform_data(
            data
        )  # add encoded context as a value for each dictionary in data
        # the original context is added as a metadata field by default. Additional metadata fields can be specified by the argument 'metadata_fields'
        metadata_fields = ["context", *metadata_fields]
        # once we have the encoded data, pull the relevant fields from each context dictionary
        upserts = [
            (v["id"], v["encoding"], {field: v[field] for field in metadata_fields})
            for v in encoded_data
        ]
        self.index.upsert(upserts, namespace)

    def delete_namespace(self, namespace):
        self.index.delete_namespace(namespace)

    def list_namespaces(self):
        """
        Lists all the namespaces in the current index
        """
        return self.index.index.describe_index_stats()["namespaces"]

    def get_pinecone_embedding_dims(self):
        """
        Queries the Pinecone index for the embedding dimensions
        """
        return self.index.index.describe_index_stats()["dimension"]

    def query(
        self, query: str, top_k=5, namespace=None, verbose=False
    ) -> Union[List[Dict], List[str]]:
        """
        Returns the the top k most similar contexts to the query in the Pinecone index, ranked in decreasing order of similarity.
        If verbose is false, will only return the contexts.
        If verbose is true, will return the scores, id, and other metadata (such as start timestamp for media documents) as well.

        Example return object when verbose =  True:
          [
            {
              'id': '4mkh709',
              'metadata': {'context': 'The father of the modern '
                                      'synthesizer is undoubtedly '
                                      'Dr. Bob Mogue.',
                          'start (ms)': 250.0},
              'score': 0.406163871,
              'values': []
              },
            {
              'id': '3rzq85k',
              'metadata': {'context': 'The Mogue modular '
                                      'synthesizer first became '
                                      'widely heard in 1968 on a '
                                      'record called Switched On '
                                      'Bark by Walter Now, Wendy '
                                      'Carlos. It was Big Brother '
                                      'to the best known '
                                      'synthesizer of all time, '
                                      'the mini mode.',
                          'start (ms)': 7650.0},
              'score': 0.196624324,
              'values': []
              },
            ]
        Example return object when verbose = False:
          [
            'The father of the modern synthesizer is undoubtedly Dr. Bob Mogue.',
            'The Mogue modular synthesizer first became widely heard in 1968 on a record called Switched On Bark by Walter Now, Wendy Carlos. It was Big Brother to the best known synthesizer of all time, the mini mode.',
          ]

        """
        query_emb = self.get_embedding(query)
        # results =  self.retriever.query(self.index, query_emb, top_k, namespace)
        results = self.index.query(query_emb, top_k, namespace)
        if verbose:
            return results["results"][0]["matches"]
        elif verbose == False:
            # return self.retriever.grab_contexts(results)
            # return only the context for each result
            return [x["metadata"]["context"] for x in results["results"][0]["matches"]]
