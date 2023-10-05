from django.contrib import admin

from .models import Logfile

# Добавление модели на главную страницу интерфейса администратора
admin.site.register(Logfile)
