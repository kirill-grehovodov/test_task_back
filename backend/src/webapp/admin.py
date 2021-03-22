from django.contrib import admin
from src.webapp.models import Post, Comment, Tag, PostRate, PostImage


class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
    readonly_fields = ('rating',)


admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(PostRate)
admin.site.register(PostImage)