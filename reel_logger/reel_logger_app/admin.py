from django.contrib import admin

from reel_logger_app.models import Footage, Comment, Scene, Shot, Take

admin.site.register(Footage)
admin.site.register(Comment)
admin.site.register(Scene)
#admin.site.register(Shot)
#admin.site.register(Take)