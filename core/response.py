from django.http import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST


def response_incorrect_id():
    return JsonResponse({'Error': 'Not correct id'}, status=HTTP_400_BAD_REQUEST)


def response_incorrect_date(e):
    return JsonResponse({'Error': 'Please, use right date format: ' + str(e)}, status=HTTP_400_BAD_REQUEST)
