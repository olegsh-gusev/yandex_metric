import json
import random
from time import sleep

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from parser import ParserError

from rest_framework.response import Response
from rest_framework.decorators import api_view

import requests, json
from requests.exceptions import ConnectionError

#  Метод для корректной обработки строк в кодировке UTF-8 как в Python 3, так и в Python 2
import sys

from rest_framework.status import HTTP_200_OK


@csrf_exempt
@api_view(["POST"])
def register(request):
    if sys.version_info < (3,):
        def u(x):
            try:
                return x.encode("utf8")
            except UnicodeDecodeError:
                return x
    else:
        def u(x):
            if type(x) == type(b''):
                return x.decode('utf8')
            else:
                return x
    CampaignsURL = 'https://api.direct.yandex.com/json/v5/campaigns'
    token = request.data.get('token')
    if token is None:
        return Response({"success": True, 'message': "add token"},
                        status=HTTP_200_OK)
    clientLogin = '7702d565154f4b0291feb6f6f579b9ee'

    headers = {"Authorization": "Bearer " + token,  # OAuth-токен. Использование слова Bearer обязательно
               # "Client-Login": clientLogin,  # Логин клиента рекламного агентства
               "Accept-Language": "ru",  # Язык ответных сообщений
               }

    # Создание тела запроса
    body = {"method": "get",  # Используемый метод.
            "params": {"SelectionCriteria": {},
                       # Критерий отбора кампаний. Для получения всех кампаний должен быть пустым
                       "FieldNames": ["ClientInfo", "Id", "Status", "Funds",  "State", "Currency", "Name", "StatusPayment", "StatusClarification", "StartDate", "EndDate", "DailyBudget"]
                       # Имена параметров, которые требуется получить.
                       }}
    jsonBody = json.dumps(body, ensure_ascii=False).encode('utf8')

    try:
        result = requests.post(CampaignsURL, jsonBody, headers=headers)
        # Обработка запроса
        if result.status_code != 200 or result.json().get("error", False):
            print("Произошла ошибка при обращении к серверу API Директа.")
            print("Код ошибки: {}".format(result.json()["error"]["error_code"]))
            print("Описание ошибки: {}".format(u(result.json()["error"]["error_detail"])))
            print("RequestId: {}".format(result.headers.get("RequestId", False)))
            return Response({"success": True, 'message': "Произошла ошибка при обращении к серверу API Директа."},
                            status=HTTP_200_OK)

        else:
            print("RequestId: {}".format(result.headers.get("RequestId", False)))
            print("Информация о баллах: {}".format(result.headers.get("Units", False)))
            # Вывод списка кампаний

            return JsonResponse(result.json()["result"]["Campaigns"], safe=False)
            if result.json()['result'].get('LimitedBy', False):
                # Если ответ содержит параметр LimitedBy, значит,  были получены не все доступные объекты.
                # В этом случае следует выполнить дополнительные запросы для получения всех объектов.
                # Подробное описание постраничной выборки - https://tech.yandex.ru/direct/doc/dg/best-practice/get-docpage/#page
                return Response({"success": True, 'message': "Получены не все доступные объекты."},
                            status=HTTP_200_OK)

    # Обработка ошибки, если не удалось соединиться с сервером API Директа
    except ConnectionError:
        # В данном случае мы рекомендуем повторить запрос позднее
        print("Произошла ошибка соединения с сервером API.")
        return Response({"success": True, 'message': "Произошла ошибка соединения с сервером API."},
                        status=HTTP_200_OK)

    # Если возникла какая-либо другая ошибка
    except:
        # В данном случае мы рекомендуем проанализировать действия приложения
        print("Произошла непредвиденная ошибка.")
        return Response({"success": True, 'message': "Произошла непредвиденная ошибка."},
                        status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def statistic(request):
    if sys.version_info < (3,):
        def u(x):
            try:
                return x.encode("utf8")
            except UnicodeDecodeError:
                return x
    else:
        def u(x):
            if type(x) == type(b''):
                return x.decode('utf8')
            else:
                return x

    # --- Входные данные ---
    # Адрес сервиса Reports для отправки JSON-запросов (регистрозависимый)
    ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'

    # OAuth-токен пользователя, от имени которого будут выполняться запросы
    token = request.data.get('token')
    if token is None:
        return Response({"success": True, 'message': "add token"},
                        status=HTTP_200_OK)
    # Логин клиента рекламного агентства
    # Обязательный параметр, если запросы выполняются от имени рекламного агентства
    clientLogin = 'ЛОГИН_КЛИЕНТА'

    # --- Подготовка запроса ---
    # Создание HTTP-заголовков запроса
    headers = {
        # OAuth-токен. Использование слова Bearer обязательно
        "Authorization": "Bearer " + token,
        # Логин клиента рекламного агентства
        # "Client-Login": clientLogin,
        # Язык ответных сообщений
        "Accept-Language": "ru",
        # Режим формирования отчета
        "processingMode": "auto"
        # Формат денежных значений в отчете
        # "returnMoneyInMicros": "false",
        # Не выводить в отчете строку с названием отчета и диапазоном дат
        # "skipReportHeader": "true",
        # Не выводить в отчете строку с названиями полей
        # "skipColumnHeader": "true",
        # Не выводить в отчете строку с количеством строк статистики
        # "skipReportSummary": "true"
    }

    # Создание тела запроса
    body = {
        "params": {
            "SelectionCriteria": {
                "DateFrom": "2020-08-01",
                "DateTo": "2020-08-05"
            },
            "FieldNames": [
                "Date",
                "CampaignName",
                "LocationOfPresenceName",
                "Impressions",
                "Clicks",
                "Cost"
            ],
            "ReportName": "name",
            "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": "NO",
            "IncludeDiscount": "NO"
        }
    }

    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)

    # --- Запуск цикла для выполнения запросов ---
    # Если получен HTTP-код 200, то выводится содержание отчета
    # Если получен HTTP-код 201 или 202, выполняются повторные запросы
    while True:
        try:
            req = requests.post(ReportsURL, body, headers=headers)
            req.encoding = 'utf-8'  # Принудительная обработка ответа в кодировке UTF-8
            if req.status_code == 400:
                print("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                return Response({"success": True,
                                 'message': "Параметры запроса указаны неверно или достигнут лимит отчетов в очереди"},
                                status=HTTP_200_OK)
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("JSON-код запроса: {}".format(u(body)))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break
            elif req.status_code == 200:
                print("Отчет создан успешно")
                return Response({"success": True,
                                 'message': "Содержание отчета: \n{}".format(u(req.text))},
                                status=HTTP_200_OK)
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("Содержание отчета: \n{}".format(u(req.text)))

                break
            elif req.status_code == 201:
                print("Отчет успешно поставлен в очередь в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                print("Повторная отправка запроса через {} секунд".format(retryIn))
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                sleep(retryIn)
            elif req.status_code == 202:
                print("Отчет формируется в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                print("Повторная отправка запроса через {} секунд".format(retryIn))
                print("RequestId:  {}".format(req.headers.get("RequestId", False)))
                sleep(retryIn)
            elif req.status_code == 500:
                return Response({"success": True,
                                 'message': "При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее"},
                                status=HTTP_200_OK)
                print("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее")
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break
            elif req.status_code == 502:
                return Response({"success": True,
                                 'message': "Время формирования отчета превысило серверное ограничение."},
                                status=HTTP_200_OK)
                print("Время формирования отчета превысило серверное ограничение.")
                print(
                    "Пожалуйста, попробуйте изменить параметры запроса - уменьшить период и количество запрашиваемых данных.")
                print("JSON-код запроса: {}".format(body))
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break
            else:
                return Response({"success": True,
                                 'message': "Произошла непредвиденная ошибка"},
                                status=HTTP_200_OK)
                print("Произошла непредвиденная ошибка")
                print("RequestId:  {}".format(req.headers.get("RequestId", False)))
                print("JSON-код запроса: {}".format(body))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break

        # Обработка ошибки, если не удалось соединиться с сервером API Директа
        except ConnectionError:
            return Response({"success": True,
                             'message': "Произошла ошибка соединения с сервером API"},
                            status=HTTP_200_OK)
            # В данном случае мы рекомендуем повторить запрос позднее
            print("Произошла ошибка соединения с сервером API")
            # Принудительный выход из цикла
            break

        # Если возникла какая-либо другая ошибка
        except:
            return Response({"success": True,
                             'message': "Произошла непредвиденная ошибка"},
                            status=HTTP_200_OK)
            # В данном случае мы рекомендуем проанализировать действия приложения
            print("Произошла непредвиденная ошибка")
            # Принудительный выход из цикла
            break