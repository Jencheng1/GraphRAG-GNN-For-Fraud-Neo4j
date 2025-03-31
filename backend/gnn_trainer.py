import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data
import numpy as np
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class FraudGNN(nn.Module):
    def __init__(self, num_features, hidden_channels, num_classes):
        super(FraudGNN, self).__init__()
        self.conv1 = GCNConv(num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.classifier = nn.Linear(hidden_channels, num_classes)
        
    def forward(self, x, edge_index, batch):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv2(x, edge_index)
        x = global_mean_pool(x, batch)
        x = self.classifier(x)
        return x

class GNNTrainer:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
        )
        self.model = None
        
    async def train(self):
        # Fetch data from Neo4j
        data = await self._fetch_training_data()
        
        # Prepare PyTorch Geometric data
        graph_data = self._prepare_graph_data(data)
        
        # Initialize model
        self.model = FraudGNN(
            num_features=graph_data.num_features,
            hidden_channels=64,
            num_classes=2  # Binary classification (fraudulent or not)
        ).to(self.device)
        
        # Training loop
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()
        
        self.model.train()
        for epoch in range(100):
            optimizer.zero_grad()
            out = self.model(
                graph_data.x,
                graph_data.edge_index,
                graph_data.batch
            )
            loss = criterion(out, graph_data.y)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch {epoch+1:03d}, Loss: {loss.item():.4f}')
        
        return {"status": "success", "epochs": 100, "final_loss": loss.item()}
    
    async def _fetch_training_data(self):
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (t:Transaction)
            MATCH (c:Customer)-[:MADE]->(t)
            MATCH (m:Merchant)-[:RECEIVED]->(t)
            RETURN t, c, m
            """
            result = session.run(query)
            return [dict(record) for record in result]
    
    def _prepare_graph_data(self, data):
        # Convert Neo4j data to PyTorch Geometric format
        # This is a simplified example - you'll need to implement the actual conversion
        # based on your graph structure and features
        
        # Example feature vectors (you should create meaningful features)
        x = torch.randn(len(data), 10)  # 10 features per node
        edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)  # Example edges
        y = torch.tensor([0, 1], dtype=torch.long)  # Example labels
        
        return Data(x=x, edge_index=edge_index, y=y) 