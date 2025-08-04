from fastapi import FastAPI
from pydantic import BaseModel
from predict import predict, load_model
import uvicorn


class Transaction(BaseModel):
    type: str
    amount: float
    oldbalanceOrg: float
    oldbalanceDest: float
    time: int

app = FastAPI()

try: 
    model = load_model()  # Load the model at startup
except Exception as e: 
    print(f"Error loading model: {e}")


@app.post("/predict")
async def prediction(transaction: Transaction):
    """
    Endpoint to make predictions on a transaction.
    """
    # Prepare the data for prediction
    data = {
        "type": transaction.type,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "oldbalanceDest": transaction.oldbalanceDest,
        "time": transaction.time
    }

    # Make predictions
    result =  predict(data, model)
    
    return {"prediction": result}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)