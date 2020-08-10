from .views import register, statistic, yandex_metric, yandex_metric_counter
from django.urls import path

app_name = "core"
# app_name will help us do a reverse look-up latter.

urlpatterns = [
    path('company_name/', register),
    path('statistic/', statistic),
    path('yandex_metric/', yandex_metric),
    path('yandex_metric_counter/', yandex_metric_counter)
    #    path('reservation_info/<int:workplace_id>/', reservation_info)

]
