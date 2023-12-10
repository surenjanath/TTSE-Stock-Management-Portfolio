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




# import pandas as pd
# import json
# from .models import StockData, StockInformation

# @receiver(post_save, sender=YourModel)  # Replace YourModel with the actual model used in your_view
# def your_view_success_handler(sender, instance, created, **kwargs):
#     if instance.status == 'success':  # Adjust this condition based on your actual success response
#         # Assuming your response is stored in 'message' field, and it's a JSON string
#         response_data = json.loads(instance.message)

#         # Process the response_data using pandas
#         df = pd.DataFrame(response_data)  # Adjust this based on your actual response structure

#         # Iterate through the DataFrame and save data to StockData model
#         for index, row in df.iterrows():
#             stock_information = StockInformation.objects.get(stock_Name=row['stock_Name'])  # Assuming stock_Name is the key
#             stock_data = StockData.objects.create(
#                 stock_information=stock_information,
#                 OPEN=row['OPEN'],
#                 CLOSE=row['CLOSE'],
#                 VOLUME_TRADED=row['VOLUME_TRADED'],
#                 stock_date=row['stock_date'],
#             )
#             stock_data.save()