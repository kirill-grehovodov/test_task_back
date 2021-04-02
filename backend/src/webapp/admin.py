from django.contrib import admin
from src.webapp.models import Post, Comment, Tag, PostRate, PostImage


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(PostRate)
admin.site.register(PostImage)
