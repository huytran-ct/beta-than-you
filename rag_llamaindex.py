from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, load_index_from_storage, StorageContext
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

class RAGLlamaIndex:
    def __init__(self, data_dir, index_dir):
        """
        Initialize the RAGLlamaIndex class.
        """
        self.data_dir = data_dir
        self.index_dir = index_dir

    def load_documents(self):
        """
        Custom method to load text files from the data directory.
        """
        reader = SimpleDirectoryReader(self.data_dir)
        documents = reader.load_data()
        return documents

    def build_index(self):
        """
        Build an index from documents in the specified directory.
        """
        # Load documents manually
        documents = self.load_documents()

        # Build the index
        index = VectorStoreIndex.from_documents(documents, embedding=OpenAIEmbedding(name="text-embedding-3-small"))

        # Save the index to disk
        index.storage_context.persist(persist_dir=self.index_dir)
        print(f"Index saved to {self.index_dir}")

    def query_index(self, query):
        """
        Query the index and return the response.
        """
        # Load the index from disk
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=self.index_dir))
        
        index_query = index.as_query_engine(llm=OpenAI(model="gpt-4o-mini"))

        # Query the index
        response = index_query.query(query)
        return response

if __name__ == "__main__":
    # Paths
    data_directory = "./data"  # Directory containing documents
    index_directory = "./index"  # Directory to save the index

    # Initialize the RAGLlamaIndex class
    rag = RAGLlamaIndex(data_directory, index_directory)

    # Build the index
    rag.build_index()

    # Query the index
    user_query = "What is the best way to find a job in Vietnam?"
    response = rag.query_index(user_query)
    print(f"Response: {response}")