#!/bin/bash

# Install Java
apt-get update
apt-get install -y openjdk-11-jdk

# Add Neo4j repository
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | tee /etc/apt/sources.list.d/neo4j.list

# Install Neo4j
apt-get update
apt-get install -y neo4j

# Configure Neo4j
sed -i 's/#dbms.memory.heap.initial_size=512m/dbms.memory.heap.initial_size=2G/' /etc/neo4j/neo4j.conf
sed -i 's/#dbms.memory.heap.max_size=1G/dbms.memory.heap.max_size=2G/' /etc/neo4j/neo4j.conf
sed -i 's/#dbms.memory.pagecache.size=512m/dbms.memory.pagecache.size=2G/' /etc/neo4j/neo4j.conf

# Set Neo4j password
neo4j-admin set-initial-password ${neo4j_password}

# Start Neo4j
systemctl start neo4j
systemctl enable neo4j

# Configure firewall
gcloud compute firewall-rules create neo4j-rule \
  --direction=INGRESS \
  --priority=1000 \
  --network=credit-fraud-vpc \
  --action=ALLOW \
  --rules=tcp:7474,tcp:7687 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=neo4j 