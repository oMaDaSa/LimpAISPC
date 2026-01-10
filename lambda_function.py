import json
from mangum import Mangum
from src.app import app

_handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    return _handler(event, context)
