from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(GameData)
admin.site.register(Event)
admin.site.register(Room)
admin.site.register(SaveData)
admin.site.register(Response)
admin.site.register(Routes)
admin.site.register(ObjectiveState)
admin.site.register(Comment)