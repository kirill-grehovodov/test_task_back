from django.contrib import admin
from src.followers.models import FollowerUser, FollowerTag, FollowerCountry


admin.site.register(FollowerUser)
admin.site.register(FollowerTag)
admin.site.register(FollowerCountry)
