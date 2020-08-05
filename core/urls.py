from .views import register, statistic
from django.urls import path

app_name = "core"
# app_name will help us do a reverse look-up latter.

urlpatterns = [
    path('company_name/', register),
    path('statistic/', statistic)

    #    path('reservation_info/<int:workplace_id>/', reservation_info)

]
