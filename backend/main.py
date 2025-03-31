from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from .database import SessionLocal, engine
from . import models, schemas, crud
from .graph_rag import GraphRAG
from .gnn_trainer import GNNTrainer

app = FastAPI(title="Credit Fraud Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize GraphRAG and GNN Trainer
graph_rag = GraphRAG()
gnn_trainer = GNNTrainer()

@app.get("/")
def read_root():
    return {"message": "Welcome to Credit Fraud Detection API"}

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)

@app.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    return transactions

@app.post("/analyze-fraud/")
async def analyze_fraud(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Use GraphRAG to analyze the transaction
    fraud_score = await graph_rag.analyze_transaction(transaction)
    return {"fraud_score": fraud_score, "transaction_id": transaction_id}

@app.post("/train-gnn/")
async def train_gnn():
    # Train the GNN model
    training_results = await gnn_trainer.train()
    return {"status": "success", "results": training_results}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 