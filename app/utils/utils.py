from datetime import datetime
from json import JSONEncoder
import json
import math
import os
from fastapi import HTTPException
from sqlalchemy import select, func, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.Pagination import PageResponse  # Adjust the import path as needed



class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Format datetime object as a string
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)
    

def paginate_data(data, page: int, limit: int):
    # Ensure data['rows'] is a list
    if not isinstance(data.get('rows', []), list):
        raise TypeError("Expected a list for pagination, but got a different type")

    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_rows = data['rows'][start_index:end_index]

    return {
        'data': [
            {   'Header': data.get('header', {}),  # Include the header if it exists
                'Columns': data.get('columns', []),
                'Rows': paginated_rows
            }
        ],  # Include a list of dictionaries, each containing 'Columns' and 'Rows'
        'page': page,
        'total_pages': (len(data['rows']) + limit - 1) // limit,
        'total_items': len(data['rows'])
    }



def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if default is None and value is None:
        raise HTTPException(status_code=500, detail=f"Environment variable {var_name} not set")
    return value

def empty_to_none(field):
    value = os.getenv(field)
    return None if value is None or len(value) == 0 else value

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True, default=str))

def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}
