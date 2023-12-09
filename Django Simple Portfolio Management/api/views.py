# -*- encoding: utf-8 -*-

from django.http import JsonResponse
from rest_framework import status, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils.datastructures import MultiValueDict
from django.utils.datastructures import MultiValueDictKeyError

from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist



from django.views.decorators.csrf import csrf_exempt
from .Functions import *
import requests
#----------------------------------------------------
# INTERNAL CALLS
#----------------------------------------------------

from rest_framework import generics
from .models import *
from .serializers import *

@csrf_exempt  # For demonstration purposes; use proper CSRF protection
def scrape_data(request):
    if request.method == 'POST':

        sym = request.POST.get('query', '')  # Get the query from the frontend
        stock_type = request.POST.get('stock_type', '')
        if sym != '':
            pass
            # Record the search query and increment its count
            # query_obj, created = Search_Query.objects.get_or_create(query=query.upper())
            # query_obj.count += 1
            # query_obj.save()

        session = requests.Session()
        headers = {
            'Authority':'www.stockex.co.tt',
            'Method':'GET',
            'Scheme':'https',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.9,de;q=0.8',
            'Cache-Control':'no-cache',

            'Cookie':"""sucuri_cloudproxy_uuid_2bf554b18=d8450e5c0a1eb7b610118d5c1a1f5305""".strip(),
            'Pragma':'no-cache',
            'Sec-Ch-Ua-Mobile':'?0',
            'Sec-Ch-Ua-Platform':'"Windows"',
            'Sec-Fetch-Dest':'document',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-Site':'cross-site',
            'Sec-Fetch-User':'?1',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }

        scraping_result = fetchTTSE_DATA(session=session,TTSE_SYMBOL=sym, TYPE=stock_type, headers=headers)

        return JsonResponse({
            'status': 'success',
            'message': scraping_result,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})