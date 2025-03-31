import pandas as pd
import argparse
from sqlalchemy import create_engine
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(data_dir):
    """Load configuration from config.json."""
    with open(Path(data_dir) / 'config.json', 'r') as f:
        return json.load(f)

def create_tables(engine):
    """Create necessary tables in PostgreSQL."""
    create_customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        risk_score FLOAT,
        created_at TIMESTAMP
    );
    """
    
    create_merchants_table = """
    CREATE TABLE IF NOT EXISTS merchants (
        id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100),
        category VARCHAR(50),
        risk_score FLOAT,
        created_at TIMESTAMP
    );
    """
    
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id VARCHAR(20) PRIMARY KEY,
        customer_id VARCHAR(20) REFERENCES customers(id),
        merchant_id VARCHAR(20) REFERENCES merchants(id),
        amount FLOAT,
        timestamp TIMESTAMP,
        status VARCHAR(20),
        fraud_score FLOAT,
        is_fraudulent BOOLEAN
    );
    """
    
    create_devices_table = """
    CREATE TABLE IF NOT EXISTS devices (
        id VARCHAR(20) PRIMARY KEY,
        fingerprint VARCHAR(50),
        type VARCHAR(20),
        risk_score FLOAT,
        created_at TIMESTAMP
    );
    """
    
    create_ip_addresses_table = """
    CREATE TABLE IF NOT EXISTS ip_addresses (
        id VARCHAR(20) PRIMARY KEY,
        address VARCHAR(50),
        location VARCHAR(100),
        risk_score FLOAT,
        created_at TIMESTAMP
    );
    """
    
    with engine.connect() as conn:
        conn.execute(create_customers_table)
        conn.execute(create_merchants_table)
        conn.execute(create_transactions_table)
        conn.execute(create_devices_table)
        conn.execute(create_ip_addresses_table)
        conn.commit()

def ingest_data(engine, data_dir):
    """Ingest data from CSV files into PostgreSQL."""
    data_dir = Path(data_dir)
    
    # Load data from CSV files
    customers_df = pd.read_csv(data_dir / 'customers.csv')
    merchants_df = pd.read_csv(data_dir / 'merchants.csv')
    transactions_df = pd.read_csv(data_dir / 'transactions.csv')
    devices_df = pd.read_csv(data_dir / 'devices.csv')
    ip_addresses_df = pd.read_csv(data_dir / 'ip_addresses.csv')
    
    # Ingest data into PostgreSQL
    customers_df.to_sql('customers', engine, if_exists='replace', index=False)
    merchants_df.to_sql('merchants', engine, if_exists='replace', index=False)
    transactions_df.to_sql('transactions', engine, if_exists='replace', index=False)
    devices_df.to_sql('devices', engine, if_exists='replace', index=False)
    ip_addresses_df.to_sql('ip_addresses', engine, if_exists='replace', index=False)
    
    logger.info(f"Ingested {len(customers_df)} customers")
    logger.info(f"Ingested {len(merchants_df)} merchants")
    logger.info(f"Ingested {len(transactions_df)} transactions")
    logger.info(f"Ingested {len(devices_df)} devices")
    logger.info(f"Ingested {len(ip_addresses_df)} IP addresses")

def main():
    parser = argparse.ArgumentParser(description='Ingest test data into PostgreSQL')
    parser.add_argument('--data-path', type=str, required=True, help='Path to test data directory')
    parser.add_argument('--db-url', type=str, required=True, help='PostgreSQL database URL')
    
    args = parser.parse_args()
    
    # Create database engine
    engine = create_engine(args.db_url)
    
    try:
        # Create tables
        logger.info("Creating database tables...")
        create_tables(engine)
        
        # Load configuration
        config = load_config(args.data_path)
        logger.info(f"Loaded configuration: {config}")
        
        # Ingest data
        logger.info("Ingesting data into PostgreSQL...")
        ingest_data(engine, args.data_path)
        
        logger.info("Data ingestion completed successfully")
        
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        raise

if __name__ == '__main__':
    main() 