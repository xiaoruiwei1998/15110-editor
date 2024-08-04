import openai
from django.http import JsonResponse
from django.http import Http404
from rest_framework import status
from utils.exceptions import BadRequestError
from django.http import HttpResponse
import uuid

import functools

def uuid4():
    return str(uuid.uuid4())

def flatten(lst):
    new_list = []
    for element in lst:
        new_list.extend(element)
    return new_list

def HandleExceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequestError as e:
            return ErrorResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:            
            return ErrorResponse(str(e), status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return ErrorResponse(str(e), status=status.HTTP_404_NOT_FOUND)
        # except openai.error.InvalidRequestError as e:
        #     return ErrorResponse({"msg": "Invalid request. The maximum content length is 4000."}, status.HTTP_400_BAD_REQUEST)
        # except openai.error.RateLimitError as e:
        #     return ErrorResponse({"msg": "Rate limit e3xceeded. Please wait for a while and try again later."}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ErrorResponse(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

def Controller(func):
    # future use of multiple decorators:
    # method3(method2(handle_exceptions(func)))
    return HandleExceptions(func)

# def compose(*decorators):
#     def decorator(func):
#         for dec in reversed(decorators):
#             func = dec(func)
#         return func
#     return decorator

# # Usage
# Controller = compose(alert_report, handle_exceptions)

def ErrorResponse(error, status):

    def parse_error(error):
        """
        Rules to parse the error message
        """
        error_message = error.replace('\"', "'")
        return error_message

    if not isinstance(error, dict):
        return JsonResponse({"error": error}, status=status)

    errors = {"error": {}}
    for key, value in error.items():
        if isinstance(value, str):
            error_message = parse_error(value)
        elif isinstance(value, list):
            error_message = [parse_error(item) for item in value]
        else:
            error_message = value

        errors["error"][key] = error_message

    return JsonResponse(errors, status=status)

def CsvResponse(filename) -> HttpResponse:
    response = HttpResponse(
                    content_type='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="{filename}"'}
                )
    response["Access-Control-Expose-Headers"] = "Content-Type, Content-Disposition"
    return response

def isFalse(value):
    return value == False or value == "false" or value == "False"