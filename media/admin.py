from django.contrib import admin
from .models import Series, MediaItem, PlayerTime

# Register your models here.
admin.site.register(Series)
admin.site.register(MediaItem)
admin.site.register(PlayerTime)
