import requests
from django.core.exceptions import ValidationError


def is_existing_country(string):
    country = requests.get("https://restcountries.eu/rest/v2/alpha/" + string)
    if not country:
        raise ValidationError('Несуществующее название страны')


def rate_check(number):
    if number not in [1, -1]:
        raise ValidationError('Несуществующая оценка')