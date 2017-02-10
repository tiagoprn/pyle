from django.contrib import admin
from .models import Tag, Link, LinkTag

admin.site.register(Tag)
admin.site.register(Link)
admin.site.register(LinkTag)
