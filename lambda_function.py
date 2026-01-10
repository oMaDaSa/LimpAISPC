import json
import traceback
from mangum import Mangum
from src.app import app

_handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    try:
        print(f"Event received: {json.dumps(event)}")
        response = _handler(event, context)
        print(f"Response status: {response.get('statusCode', 'N/A')}")
        return response
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
