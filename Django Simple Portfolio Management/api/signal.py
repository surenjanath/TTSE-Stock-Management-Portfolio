# your_app_name/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from uuid import uuid4
from .models import Webscraping_Header

@receiver(post_save, sender=Webscraping_Header)
def handle_webscraping_header_save(sender, instance, **kwargs):
    if not instance.status:
        new_code = instance.generate_new_code()['Auth']
        instance.cookie_code = new_code
        instance.status = True
        instance.save()