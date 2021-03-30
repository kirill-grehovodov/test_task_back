import requests
from django.core.exceptions import ValidationError


def is_existing_country(string):
    print("validator")
    country = requests.get("https://restcountries.eu/rest/v2/alpha/" + string)
    if not country:
        raise ValidationError('Несуществующее название страны')