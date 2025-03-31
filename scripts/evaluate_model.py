import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import json
import argparse
from pathlib import Path
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, postgres_url, neo4j_uri, neo4j_user, neo4j_password):
        self.postgres_engine = create_engine(postgres_url)
        self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def close(self):
        self.neo4j_driver.close()
    
    def load_test_data(self, test_set_path):
        """Load test data from CSV file."""
        return pd.read_csv(test_set_path)
    
    def get_postgres_predictions(self):
        """Get predictions from PostgreSQL database."""
        query = """
        SELECT t.id, t.fraud_score, t.is_fraudulent
        FROM transactions t
        WHERE t.timestamp >= NOW() - INTERVAL '30 days'
        """
        return pd.read_sql(query, self.postgres_engine)
    
    def get_neo4j_predictions(self):
        """Get predictions from Neo4j graph database."""
        query = """
        MATCH (t:Transaction)
        WHERE t.timestamp >= datetime() - duration('P30D')
        RETURN t.id as id, t.fraud_score as fraud_score, t.is_fraudulent as is_fraudulent
        """
        with self.neo4j_driver.session() as session:
            result = session.run(query)
            return pd.DataFrame([dict(record) for record in result])
    
    def calculate_metrics(self, y_true, y_pred, y_pred_proba):
        """Calculate evaluation metrics."""
        metrics = {
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_pred_proba)
        }
        return metrics
    
    def plot_confusion_matrix(self, y_true, y_pred, output_path):
        """Plot and save confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(output_path)
        plt.close()
    
    def evaluate_graph_metrics(self):
        """Evaluate graph-specific metrics."""
        query = """
        MATCH (t:Transaction)-[:MADE]->(c:Customer)
        WITH c, count(t) as transaction_count
        RETURN avg(transaction_count) as avg_transactions_per_customer
        """
        with self.neo4j_driver.session() as session:
            result = session.run(query)
            metrics = {}
            for record in result:
                metrics['avg_transactions_per_customer'] = record['avg_transactions_per_customer']
            return metrics
    
    def evaluate_system_performance(self):
        """Evaluate system performance metrics."""
        # Query execution time
        query = """
        MATCH (t:Transaction)
        WHERE t.timestamp >= datetime() - duration('P1D')
        RETURN count(t) as transaction_count
        """
        start_time = datetime.now()
        with self.neo4j_driver.session() as session:
            session.run(query)
        neo4j_query_time = (datetime.now() - start_time).total_seconds()
        
        # PostgreSQL query time
        start_time = datetime.now()
        pd.read_sql("SELECT COUNT(*) FROM transactions", self.postgres_engine)
        postgres_query_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'neo4j_query_time': neo4j_query_time,
            'postgres_query_time': postgres_query_time
        }

def main():
    parser = argparse.ArgumentParser(description='Evaluate model performance')
    parser.add_argument('--test-set', type=str, required=True, help='Path to test data CSV')
    parser.add_argument('--postgres-url', type=str, required=True, help='PostgreSQL database URL')
    parser.add_argument('--neo4j-uri', type=str, required=True, help='Neo4j database URI')
    parser.add_argument('--neo4j-user', type=str, required=True, help='Neo4j username')
    parser.add_argument('--neo4j-password', type=str, required=True, help='Neo4j password')
    parser.add_argument('--output-dir', type=str, default='./reports', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize evaluator
    evaluator = ModelEvaluator(
        args.postgres_url,
        args.neo4j_uri,
        args.neo4j_user,
        args.neo4j_password
    )
    
    try:
        # Load test data
        logger.info("Loading test data...")
        test_data = evaluator.load_test_data(args.test_set)
        
        # Get predictions
        logger.info("Getting predictions from databases...")
        postgres_preds = evaluator.get_postgres_predictions()
        neo4j_preds = evaluator.get_neo4j_predictions()
        
        # Calculate metrics
        logger.info("Calculating metrics...")
        metrics = evaluator.calculate_metrics(
            test_data['is_fraudulent'],
            postgres_preds['fraud_score'] > 0.5,
            postgres_preds['fraud_score']
        )
        
        # Plot confusion matrix
        logger.info("Generating confusion matrix...")
        evaluator.plot_confusion_matrix(
            test_data['is_fraudulent'],
            postgres_preds['fraud_score'] > 0.5,
            output_dir / 'confusion_matrix.png'
        )
        
        # Evaluate graph metrics
        logger.info("Evaluating graph metrics...")
        graph_metrics = evaluator.evaluate_graph_metrics()
        
        # Evaluate system performance
        logger.info("Evaluating system performance...")
        system_metrics = evaluator.evaluate_system_performance()
        
        # Combine all metrics
        evaluation_report = {
            'model_performance': metrics,
            'graph_metrics': graph_metrics,
            'system_metrics': system_metrics,
            'evaluation_time': datetime.now().isoformat()
        }
        
        # Save report
        with open(output_dir / 'evaluation_report.json', 'w') as f:
            json.dump(evaluation_report, f, indent=2)
        
        logger.info(f"Evaluation report saved to {output_dir}")
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise
    finally:
        evaluator.close()

if __name__ == '__main__':
    main() 