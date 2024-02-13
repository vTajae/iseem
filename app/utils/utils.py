from datetime import datetime
from json import JSONEncoder
import json
import math
import os
from fastapi import HTTPException
from sqlalchemy import select, func, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
# Adjust the import path as needed
from app.api.schemas.Pagination import PageResponse


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Format datetime object as a string
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)


def paginate_data(data, page: int, limit: int):
    
    print(data, "data")
    
    # Default response for unexpected data structure
    default_response = {
        'data': [],
        'page': page,
        'total_pages': 0,
        'total_items': 0
    }

    # Check for 'NoReportData' option
    no_report_data_option = next(
        (option for option in data.get('Header', {}).get('Option', [])
         if option.get('Name') == 'NoReportData'), None)

    # If 'NoReportData' is true, return empty data array
    if no_report_data_option and no_report_data_option.get('Value') == 'true':
        return default_response

    # Handle invoice data
    if 'QueryResponse' in data and 'Invoice' in data['QueryResponse']:
        invoices = data['QueryResponse']['Invoice']
        total_items = data['QueryResponse'].get('totalCount', len(invoices))
        start_index, end_index = (page - 1) * limit, page * limit
        paginated_invoices = invoices[start_index:end_index]

        # Construct invoice data response
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

    # Handle reports data
    elif 'Header' in data and 'ReportName' in data['Header']:
        rows = data.get('Rows', {}).get('Row', [])
        if not rows:
            return default_response  # Return default if no rows

        start_index, end_index = (page - 1) * limit, page * limit
        paginated_rows = rows[start_index:end_index]

        # Construct report data response
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

    return default_response


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if default is None and value is None:
        raise HTTPException(
            status_code=500, detail=f"Environment variable {var_name} not set")
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
