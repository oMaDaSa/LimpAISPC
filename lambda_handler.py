import json
from mangum import Mangum
from src.app import app

# Adapter Mangum para Flask
_handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    Handler principal para AWS Lambda
    Recebe eventos do API Gateway e processa via Flask
    """
    return _handler(event, context)
