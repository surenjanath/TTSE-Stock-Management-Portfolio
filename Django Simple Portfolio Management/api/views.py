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
def add_stock_data(request):
    if request.method == 'POST':
        # var stockType = $("#stockType").val();
        # var stockSite = $("#stockSite").val();
        # var ttseSymbol = $("#ttseSymbol").val();
        sym = request.POST.get('ttseSymbol', '')  # Get the query from the frontend
        stock_type = request.POST.get('stockType', '')
        if sym != '':
            pass
            # Record the search query and increment its count
            # query_obj, created = Search_Query.objects.get_or_create(query=query.upper())
            # query_obj.count += 1
            # query_obj.save()

        session = requests.Session()


        scraping_result = fetchTTSE_DATA(session=session,TTSE_SYMBOL=sym, TYPE=stock_type)

        return JsonResponse({
            'status': 'success',
            'message': scraping_result,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})