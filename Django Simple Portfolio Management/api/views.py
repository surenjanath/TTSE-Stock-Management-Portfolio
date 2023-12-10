# -*- encoding: utf-8 -*-

from django.http import JsonResponse
from rest_framework import status, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils.datastructures import MultiValueDict
from django.utils.datastructures import MultiValueDictKeyError

from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist


import json
from django.views.decorators.csrf import csrf_exempt
from .Functions import *
import requests

#----------------------------------------------------
# INTERNAL CALLS
#----------------------------------------------------
from rest_framework import generics
from .models import *
from .serializers import *
import pandas as pd
from bs4 import BeautifulSoup as bs
from io import StringIO

from rest_framework.decorators import api_view


@api_view(['GET'])
def get_stock_information(request):
    stock_information = Stock_Information.objects.all()
    serializer = Stock_InformationSerializer(stock_information, many=True)
    return Response(serializer.data)



@csrf_exempt
def add_stock_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            sym = data['symbol'].strip()
            stock_type = data['type']
            site = data['site']
            if sym != '':

                session = requests.Session()


                scraping_result = fetchTTSE_DATA(session=session, TTSE_SYMBOL=sym, TYPE=stock_type, HEADER_MODEL = Webscraping_Header)
                if scraping_result['status'] == 'success':
                    soup = bs(scraping_result['body'], 'lxml')
                    df = pd.read_html(StringIO(str(soup.find("table",{'id':'myTable'}))))[0]

                    # Data Cleaning and Preprocessing
                    df.fillna({'Open': 0, 'CLOSE': 0, 'Volume Traded': 0}, inplace=True)
                    df['Open'] = df['Open'].astype(float)
                    df['Close'] = df['Close'].astype(float)
                    df['Volume Traded'] = df['Volume Traded'].astype(float)
                    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, format='mixed', errors='coerce')

                    Stock_Name = soup.find("div", {'class':'elementor-element-99e4bff'}).text.strip()
                    Stock_Sector = soup.find("div", {'class':'elementor-element-5a9fb12'}).text.strip()
                    Stock_Website = soup.find("div", {'class':'elementor-element-4ec62fe'}).text.strip()


                    index_data = soup.find("table",{"id":"index_information"})
                    # Find the last two <th> elements
                    marCap_th = index_data.find_all('tr')[-1]

                    # Get the corresponding <td> elements
                    issued_share_capital_td = marCap_th.find_all('td')[0]
                    market_cap_td = marCap_th.find_all('td')[1]

                    # Extract the text content
                    issued_share_capital = issued_share_capital_td.get_text(strip=True)
                    market_cap = market_cap_td.get_text(strip=True)

                    print("Name:", Stock_Name)
                    print("Sector:", Stock_Sector)
                    print("Website:", Stock_Website)
                    print("Issued Share Capital:", issued_share_capital)
                    print("Market Capitalization:", market_cap)

                    # Saving data to the Stock_Information model
                    stock_info = Stock_Information(
                        TTSE_Name=Stock_Name,
                        TTSE_Symbol=sym,  # Replace with the actual symbol
                        TTSE_Sector=Stock_Sector,
                        TTSE_Website=Stock_Website,
                        TTSE_IssuedShareCap=int(issued_share_capital.replace(",", "")),
                        TTSE_MarketCap=float(market_cap.replace("$", "").replace(",", "")),
                        Type= stock_type,
                        Note="",
                        Site=site,
                    )
                    stock_info.save()

                    # Create a list to store Stock_Data instances
                    stock_data_instances = []

                    # Populate the list with Stock_Data instances
                    for _, row in df.iterrows():
                        stock_data = Stock_Data(
                            stock_information=stock_info,
                            OPEN=row['Open'],
                            CLOSE=row['Close'],
                            VOLUME_TRADED=row['Volume Traded'],
                            stock_date=row['Date'],  # Assuming 'Date' is a column in your DataFrame
                        )
                        # Set additional fields
                        stock_data.uniqueId = str(uuid4()).split('-')[4]
                        stock_data.slug = slugify('{} | {}'.format(stock_info.TTSE_Symbol, stock_data.uniqueId))
                        stock_data.date_created = timezone.localtime(timezone.now())
                        stock_data.last_updated = timezone.localtime(timezone.now())

                        # Append the instance to the list
                        stock_data_instances.append(stock_data)

                    # Use bulk_create to save all instances in a single query
                    Stock_Data.objects.bulk_create(stock_data_instances)

                return JsonResponse({
                    'status': 'success',
                    'message': str(scraping_result),
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No Symbol was Given',
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON payload',
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method',
    })