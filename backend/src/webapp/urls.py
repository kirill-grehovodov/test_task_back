from django.urls import path

from src.webapp.views import IndexView, CountryView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('country/<str:code>/', CountryView.as_view(), name='country_view')
]