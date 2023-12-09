
from django.contrib import admin
from api.models import *


@admin.register(Webscraping_Header)
class WebscrapingHeaderAdmin(admin.ModelAdmin):
    # Customize the admin options if needed
    list_display = ['header', 'cookie_code', 'time_remaining', 'status', 'uniqueId', 'slug', 'date_created', 'last_updated']
    # ... (other options)