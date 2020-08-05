from django.db.models import Q
import datetime

from core.models import Reservation
from dateutil.parser import parse


def get_reservation(datetime_from, datetime_to):
    return Reservation.objects.filter(
        Q(date_from__range=[datetime_from, datetime_to]) |
        (Q(date_from__lte=datetime_from) & Q(date_to__gte=datetime_from)))


def get_date(request, is_params=False):
    if is_params:
        datetime_from = request.query_params.get('datetime_from', None)
    else:
        datetime_from = request.data.get('datetime_from', None)
    date_time_now = datetime.datetime.now()
    if datetime_from is not None:
        datetime_from = parse(datetime_from)
    else:
        datetime_from = date_time_now
    if datetime_from < date_time_now:
        raise ValueError('datetime_from < date_time_now')
    if is_params:
        datetime_to = request.query_params.get('datetime_to', None)
    else:
        datetime_to = request.data.get('datetime_to', None)
    if datetime_to is not None:
        datetime_to = parse(datetime_to)
    else:
        datetime_to = datetime_from + datetime.timedelta(hours=8)
    if datetime_from > datetime_to:
        raise ValueError('datetime_from < datetime_to')
    return datetime_from, datetime_to
