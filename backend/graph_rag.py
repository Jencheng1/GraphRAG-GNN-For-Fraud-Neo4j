from neo4j import GraphDatabase
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
import os
from dotenv import load_dotenv

load_dotenv()

class GraphRAG:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = Chroma(
            persist_directory="./data/vector_store",
            embedding_function=self.embeddings
        )

    async def analyze_transaction(self, transaction):
        # Create transaction graph representation
        with self.neo4j_driver.session() as session:
            # Query for related transactions and entities
            query = """
            MATCH (t:Transaction {id: $transaction_id})
            MATCH (c:Customer)-[:MADE]->(t)
            MATCH (m:Merchant)-[:RECEIVED]->(t)
            MATCH (c)-[:MADE]->(related:Transaction)
            WHERE related.id <> t.id
            RETURN t, c, m, related
            """
            result = session.run(query, transaction_id=transaction.id)
            
            # Process the graph data
            graph_data = self._process_graph_data(result)
            
            # Generate embeddings for the transaction context
            context = self._generate_context(graph_data)
            
            # Query the vector store for similar fraudulent patterns
            similar_patterns = self.vector_store.similarity_search(context, k=3)
            
            # Calculate fraud score based on graph patterns and similar cases
            fraud_score = self._calculate_fraud_score(graph_data, similar_patterns)
            
            return fraud_score

    def _process_graph_data(self, result):
        # Process Neo4j query results into a structured format
        graph_data = {
            "transaction": {},
            "customer": {},
            "merchant": {},
            "related_transactions": []
        }
        
        for record in result:
            graph_data["transaction"] = dict(record["t"])
            graph_data["customer"] = dict(record["c"])
            graph_data["merchant"] = dict(record["m"])
            graph_data["related_transactions"].append(dict(record["related"]))
            
        return graph_data

    def _generate_context(self, graph_data):
        # Generate a text context from the graph data
        context = f"""
        Transaction: {graph_data['transaction']}
        Customer: {graph_data['customer']}
        Merchant: {graph_data['merchant']}
        Related Transactions: {graph_data['related_transactions']}
        """
        return context

    def _calculate_fraud_score(self, graph_data, similar_patterns):
        # Implement fraud scoring logic based on graph patterns and similar cases
        # This is a simplified example
        base_score = 0.0
        
        # Check transaction amount
        amount = graph_data["transaction"].get("amount", 0)
        if amount > 10000:  # High-value transaction
            base_score += 0.3
            
        # Check related transactions
        related_transactions = graph_data["related_transactions"]
        if len(related_transactions) > 10:  # High number of related transactions
            base_score += 0.2
            
        # Check similar patterns
        for pattern in similar_patterns:
            if "fraud" in pattern.page_content.lower():
                base_score += 0.1
                
        return min(base_score, 1.0)  # Normalize score between 0 and 1 