import chromadb
from chromadb.utils import embedding_functions
import os
import hashlib

class LongTermMemory:
    def __init__(self, persist_directory="./chroma_db", collection_name="jarvis_stark_archives"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def add_document(self, text, metadata=None):
        """Adds a document to the Stark Archives."""
        # Use stable ID based on content
        doc_id = hashlib.md5(text.encode()).hexdigest()
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{}],
            ids=[doc_id]
        )

    def query(self, query_text, n_results=3):
        """Queries the archives for relevant data."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

    def load_from_directory(self, directory_path):
        """Ingests all protocols and documents from a directory."""
        if not os.path.exists(directory_path):
            return
            
        count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt") or filename.endswith(".md"):
                file_path = os.path.join(directory_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            self.add_document(content, metadata={"filename": filename, "source": "local_ingest"})
                            count += 1
                except Exception as e:
                    print(f"Error ingesting {filename}: {e}")
        
        if count > 0:
            print(f"[JARVIS]: Stark Archives updated. {count} protocols ingested from {directory_path}.")
