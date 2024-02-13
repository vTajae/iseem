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
    print(data, "data")
    # Check if it's invoice data based on the presence of 'QueryResponse' and 'Invoice' keys
    if 'QueryResponse' in data and 'Invoice' in data['QueryResponse']:
        invoices = data['QueryResponse']['Invoice']
        total_items = data['QueryResponse'].get('totalCount', len(invoices))

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_invoices = invoices[start_index:end_index]

        # Construct the response for invoice data
        return {
            'data': {
                'QueryResponse': {
                    'Invoices': paginated_invoices,
                    'startPosition': start_index + 1,
                    'maxResults': len(paginated_invoices),
                    'totalCount': total_items
                },
                "time": data['QueryResponse'].get('Time', '')
            },
            'page': page,
            'total_pages': (total_items + limit - 1) // limit,
            'total_items': total_items
        }

    # Assuming 'Rows' key for other types of data
    elif 'Header' in data and 'ReportName' in data['Header']:
        
        print(data, "data")
        rows = data['Rows']['Row']
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_rows = rows[start_index:end_index]

        # Construct the response for other data types
        return {
            'data': [
                {
                    'Header': data.get('Header', {}),
                    'Columns': data.get('Columns', []),
                    'Rows': {'Row': paginated_rows}
                }
            ],
            'page': page,
            'total_pages': (len(rows) + limit - 1) // limit,
            'total_items': len(rows)
        }
    else:
        # Handle unexpected data structure
        return {
            'data': [],
            'page': page,
            'total_pages': 0,
            'total_items': 0
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
