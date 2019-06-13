from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(LinkedQuestion)
admin.site.register(RelatedQuestion)
