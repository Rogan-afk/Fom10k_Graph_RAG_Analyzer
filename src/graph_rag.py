import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class GraphRAG:
    """Simulates a Retrieval-Augmented Generation system over a knowledge graph."""
    def __init__(self, model_name="gpt-4o"):
        self.graphs = {}
        self.llm = ChatOpenAI(temperature=0.1, model_name=model_name)
        print("GraphRAG chain initialized.")

    def is_graph_loaded(self, filename):
        """Checks if a graph for the given filename is ready for querying."""
        graph_name = os.path.splitext(filename)[0]
        return self.graphs.get(graph_name, {}).get("status") == "loaded"

    def load_graph(self, filename):
        """Marks a graph as 'loaded' and ready for querying."""
        graph_name = os.path.splitext(filename)[0]
        self.graphs[graph_name] = {"status": "loaded"}
        print(f"Graph for '{graph_name}' is now available for queries.")

    def query(self, filename, question):
        """Answers a user's question by simulating a query to the knowledge graph."""
        graph_name = os.path.splitext(filename)[0]
        if not self.is_graph_loaded(filename):
            return "The knowledge graph for this document must be generated first."
        system_prompt = f"""
        You are a financial analysis system. Your knowledge is from a knowledge graph of the 10-K filing for '{graph_name}'.
        The user has asked: '{question}'.
        Provide a direct, professional answer as if retrieving data from the graph. Do not mention the simulation or the graph itself.
        """
        try:
            response = self.llm.invoke(system_prompt)
            return response.content
        except Exception as e:
            print(f"Error during LLM invocation: {e}")
            return "An error occurred while communicating with the language model."