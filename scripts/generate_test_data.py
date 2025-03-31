import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import argparse
from pathlib import Path

def generate_customer_profiles(num_customers):
    """Generate synthetic customer profiles."""
    customers = []
    for i in range(num_customers):
        customer = {
            'id': f'CUST_{i:06d}',
            'name': f'Customer_{i}',
            'email': f'customer_{i}@example.com',
            'risk_score': random.uniform(0.0, 1.0),
            'created_at': datetime.now() - timedelta(days=random.randint(0, 365))
        }
        customers.append(customer)
    return pd.DataFrame(customers)

def generate_merchant_profiles(num_merchants):
    """Generate synthetic merchant profiles."""
    categories = ['retail', 'food', 'travel', 'entertainment', 'utilities', 'healthcare']
    merchants = []
    for i in range(num_merchants):
        merchant = {
            'id': f'MERCH_{i:06d}',
            'name': f'Merchant_{i}',
            'category': random.choice(categories),
            'risk_score': random.uniform(0.0, 1.0),
            'created_at': datetime.now() - timedelta(days=random.randint(0, 365))
        }
        merchants.append(merchant)
    return pd.DataFrame(merchants)

def generate_transactions(num_transactions, customers_df, merchants_df, fraud_ratio):
    """Generate synthetic transaction data with fraud patterns."""
    transactions = []
    num_fraudulent = int(num_transactions * fraud_ratio)
    
    # Generate normal transactions
    for i in range(num_transactions - num_fraudulent):
        customer = customers_df.iloc[random.randint(0, len(customers_df)-1)]
        merchant = merchants_df.iloc[random.randint(0, len(merchants_df)-1)]
        
        transaction = {
            'id': f'TXN_{i:08d}',
            'customer_id': customer['id'],
            'merchant_id': merchant['id'],
            'amount': random.uniform(10.0, 10000.0),
            'timestamp': datetime.now() - timedelta(hours=random.randint(0, 24*30)),
            'status': 'completed',
            'fraud_score': 0.0,
            'is_fraudulent': False
        }
        transactions.append(transaction)
    
    # Generate fraudulent transactions with patterns
    for i in range(num_fraudulent):
        customer = customers_df.iloc[random.randint(0, len(customers_df)-1)]
        merchant = merchants_df.iloc[random.randint(0, len(merchants_df)-1)]
        
        # Generate fraud patterns
        amount = random.uniform(1000.0, 50000.0)  # Higher amounts for fraud
        fraud_score = random.uniform(0.7, 1.0)  # High fraud scores
        
        transaction = {
            'id': f'TXN_{i+num_transactions-num_fraudulent:08d}',
            'customer_id': customer['id'],
            'merchant_id': merchant['id'],
            'amount': amount,
            'timestamp': datetime.now() - timedelta(hours=random.randint(0, 24*30)),
            'status': 'flagged',
            'fraud_score': fraud_score,
            'is_fraudulent': True
        }
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)

def generate_device_profiles(transactions_df):
    """Generate synthetic device profiles for transactions."""
    devices = []
    device_ids = set()
    
    for _, transaction in transactions_df.iterrows():
        if random.random() < 0.3:  # 30% chance of new device
            device_id = f'DEV_{len(device_ids):06d}'
            device_ids.add(device_id)
            
            device = {
                'id': device_id,
                'fingerprint': f'FP_{random.randint(1000000, 9999999)}',
                'type': random.choice(['mobile', 'desktop', 'tablet']),
                'risk_score': random.uniform(0.0, 1.0),
                'created_at': transaction['timestamp']
            }
            devices.append(device)
    
    return pd.DataFrame(devices)

def generate_ip_addresses(transactions_df):
    """Generate synthetic IP addresses for transactions."""
    ip_addresses = []
    ip_set = set()
    
    for _, transaction in transactions_df.iterrows():
        if random.random() < 0.2:  # 20% chance of new IP
            while True:
                ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
                if ip not in ip_set:
                    ip_set.add(ip)
                    break
            
            ip_address = {
                'id': f'IP_{len(ip_set):06d}',
                'address': ip,
                'location': f"Location_{random.randint(1, 100)}",
                'risk_score': random.uniform(0.0, 1.0),
                'created_at': transaction['timestamp']
            }
            ip_addresses.append(ip_address)
    
    return pd.DataFrame(ip_addresses)

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic test data for credit fraud detection')
    parser.add_argument('--num-transactions', type=int, default=10000, help='Number of transactions to generate')
    parser.add_argument('--num-customers', type=int, default=1000, help='Number of customers to generate')
    parser.add_argument('--num-merchants', type=int, default=500, help='Number of merchants to generate')
    parser.add_argument('--fraud-ratio', type=float, default=0.05, help='Ratio of fraudulent transactions')
    parser.add_argument('--output-dir', type=str, default='./test_data', help='Output directory for generated data')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    customers_df = generate_customer_profiles(args.num_customers)
    merchants_df = generate_merchant_profiles(args.num_merchants)
    transactions_df = generate_transactions(args.num_transactions, customers_df, merchants_df, args.fraud_ratio)
    devices_df = generate_device_profiles(transactions_df)
    ip_addresses_df = generate_ip_addresses(transactions_df)
    
    # Save data to CSV files
    customers_df.to_csv(output_dir / 'customers.csv', index=False)
    merchants_df.to_csv(output_dir / 'merchants.csv', index=False)
    transactions_df.to_csv(output_dir / 'transactions.csv', index=False)
    devices_df.to_csv(output_dir / 'devices.csv', index=False)
    ip_addresses_df.to_csv(output_dir / 'ip_addresses.csv', index=False)
    
    # Save configuration
    config = {
        'num_transactions': args.num_transactions,
        'num_customers': args.num_customers,
        'num_merchants': args.num_merchants,
        'fraud_ratio': args.fraud_ratio,
        'generated_at': datetime.now().isoformat()
    }
    with open(output_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Generated test data in {output_dir}")
    print(f"Number of transactions: {len(transactions_df)}")
    print(f"Number of fraudulent transactions: {len(transactions_df[transactions_df['is_fraudulent']])}")
    print(f"Number of customers: {len(customers_df)}")
    print(f"Number of merchants: {len(merchants_df)}")
    print(f"Number of devices: {len(devices_df)}")
    print(f"Number of IP addresses: {len(ip_addresses_df)}")

if __name__ == '__main__':
    main() 