import pandas as pd
import argparse
from neo4j import GraphDatabase
from pathlib import Path
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jIngester:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_constraints(self, session):
        """Create necessary constraints in Neo4j."""
        constraints = [
            "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) ON (c.id) IS UNIQUE",
            "CREATE CONSTRAINT merchant_id IF NOT EXISTS FOR (m:Merchant) ON (m.id) IS UNIQUE",
            "CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) ON (t.id) IS UNIQUE",
            "CREATE CONSTRAINT device_id IF NOT EXISTS FOR (d:Device) ON (d.id) IS UNIQUE",
            "CREATE CONSTRAINT ip_id IF NOT EXISTS FOR (i:IPAddress) ON (i.id) IS UNIQUE"
        ]
        
        for constraint in constraints:
            session.run(constraint)
    
    def create_customers(self, session, customers_df):
        """Create Customer nodes in Neo4j."""
        query = """
        UNWIND $customers AS customer
        CREATE (c:Customer {
            id: customer.id,
            name: customer.name,
            email: customer.email,
            risk_score: customer.risk_score,
            created_at: datetime(customer.created_at)
        })
        """
        session.run(query, customers=customers_df.to_dict('records'))
    
    def create_merchants(self, session, merchants_df):
        """Create Merchant nodes in Neo4j."""
        query = """
        UNWIND $merchants AS merchant
        CREATE (m:Merchant {
            id: merchant.id,
            name: merchant.name,
            category: merchant.category,
            risk_score: merchant.risk_score,
            created_at: datetime(merchant.created_at)
        })
        """
        session.run(query, merchants=merchants_df.to_dict('records'))
    
    def create_devices(self, session, devices_df):
        """Create Device nodes in Neo4j."""
        query = """
        UNWIND $devices AS device
        CREATE (d:Device {
            id: device.id,
            fingerprint: device.fingerprint,
            type: device.type,
            risk_score: device.risk_score,
            created_at: datetime(device.created_at)
        })
        """
        session.run(query, devices=devices_df.to_dict('records'))
    
    def create_ip_addresses(self, session, ip_addresses_df):
        """Create IPAddress nodes in Neo4j."""
        query = """
        UNWIND $ip_addresses AS ip
        CREATE (i:IPAddress {
            id: ip.id,
            address: ip.address,
            location: ip.location,
            risk_score: ip.risk_score,
            created_at: datetime(ip.created_at)
        })
        """
        session.run(query, ip_addresses=ip_addresses_df.to_dict('records'))
    
    def create_transactions(self, session, transactions_df):
        """Create Transaction nodes and relationships in Neo4j."""
        query = """
        UNWIND $transactions AS tx
        MATCH (c:Customer {id: tx.customer_id})
        MATCH (m:Merchant {id: tx.merchant_id})
        CREATE (t:Transaction {
            id: tx.id,
            amount: tx.amount,
            timestamp: datetime(tx.timestamp),
            status: tx.status,
            fraud_score: tx.fraud_score,
            is_fraudulent: tx.is_fraudulent
        })
        CREATE (c)-[:MADE]->(t)
        CREATE (t)-[:WITH]->(m)
        """
        session.run(query, transactions=transactions_df.to_dict('records'))
    
    def create_device_relationships(self, session, transactions_df, devices_df):
        """Create relationships between transactions and devices."""
        query = """
        UNWIND $transactions AS tx
        MATCH (t:Transaction {id: tx.id})
        MATCH (d:Device {id: tx.device_id})
        CREATE (t)-[:USED_DEVICE]->(d)
        """
        session.run(query, transactions=transactions_df.to_dict('records'))
    
    def create_ip_relationships(self, session, transactions_df, ip_addresses_df):
        """Create relationships between transactions and IP addresses."""
        query = """
        UNWIND $transactions AS tx
        MATCH (t:Transaction {id: tx.id})
        MATCH (i:IPAddress {id: tx.ip_id})
        CREATE (t)-[:FROM_IP]->(i)
        """
        session.run(query, transactions=transactions_df.to_dict('records'))

def main():
    parser = argparse.ArgumentParser(description='Ingest test data into Neo4j')
    parser.add_argument('--data-path', type=str, required=True, help='Path to test data directory')
    parser.add_argument('--uri', type=str, required=True, help='Neo4j database URI')
    parser.add_argument('--user', type=str, required=True, help='Neo4j username')
    parser.add_argument('--password', type=str, required=True, help='Neo4j password')
    
    args = parser.parse_args()
    
    # Load data from CSV files
    data_dir = Path(args.data_path)
    customers_df = pd.read_csv(data_dir / 'customers.csv')
    merchants_df = pd.read_csv(data_dir / 'merchants.csv')
    transactions_df = pd.read_csv(data_dir / 'transactions.csv')
    devices_df = pd.read_csv(data_dir / 'devices.csv')
    ip_addresses_df = pd.read_csv(data_dir / 'ip_addresses.csv')
    
    # Initialize Neo4j ingester
    ingester = Neo4jIngester(args.uri, args.user, args.password)
    
    try:
        with ingester.driver.session() as session:
            # Create constraints
            logger.info("Creating Neo4j constraints...")
            ingester.create_constraints(session)
            
            # Create nodes
            logger.info("Creating Customer nodes...")
            ingester.create_customers(session, customers_df)
            
            logger.info("Creating Merchant nodes...")
            ingester.create_merchants(session, merchants_df)
            
            logger.info("Creating Device nodes...")
            ingester.create_devices(session, devices_df)
            
            logger.info("Creating IPAddress nodes...")
            ingester.create_ip_addresses(session, ip_addresses_df)
            
            # Create relationships
            logger.info("Creating Transaction nodes and relationships...")
            ingester.create_transactions(session, transactions_df)
            
            logger.info("Creating device relationships...")
            ingester.create_device_relationships(session, transactions_df, devices_df)
            
            logger.info("Creating IP address relationships...")
            ingester.create_ip_relationships(session, transactions_df, ip_addresses_df)
            
            logger.info("Data ingestion completed successfully")
            
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        raise
    finally:
        ingester.close()

if __name__ == '__main__':
    main() 