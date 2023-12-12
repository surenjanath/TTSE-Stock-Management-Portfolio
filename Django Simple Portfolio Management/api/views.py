# -*- encoding: utf-8 -*-

from django.http import JsonResponse
from rest_framework import status, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils.datastructures import MultiValueDict
from django.utils.datastructures import MultiValueDictKeyError

from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

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
from datetime import datetime
from django.db.models.functions import TruncMonth, TruncDate

from django.db.models import Sum, F, FloatField
import pandas_market_calendars as mcal

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
                sym = sym.upper()
                existing_symbol = Stock_Information.objects.filter(TTSE_Symbol=sym).first()

                if existing_symbol:
                    print(existing_symbol.__dict__)
                    data = existing_symbol.__dict__

                    return JsonResponse({
                        'status': 'error',
                        'message': f'Sorry {sym} Exists',
                        'stockName' : data['TTSE_Name'],
                        'issuedShareCapital' : data['TTSE_IssuedShareCap'],
                        'marketCapitalization' : data['TTSE_MarketCap'],
                        'uniqueId': data['uniqueId'],
                        'stockWebsite' :data['TTSE_Website'],
                    })
                else:
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
                        try:
                            Stock_Website = soup.find("div", {'class':'elementor-element-4ec62fe'}).text.strip()
                        except:
                            Stock_Website = None

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

                            'stockName' : Stock_Name,
                            'stockWebsite' :Stock_Website,
                            'issuedShareCapital' : issued_share_capital,
                            'marketCapitalization' : market_cap,
                            'uniqueId': stock_info.uniqueId,
                            'message': str(scraping_result),
                        })
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'No Symbol was Given',
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

@csrf_exempt
def add_stock_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            stock_id = data['stockInfoId']
            number_of_stocks_purchased = data['numberOfStocks']
            transactionType = data['transactionType']
            transactionDate = data['transactionDate']
            note = data['transactionNote']
            transaction_date_str = transactionDate

            # Convert transaction_date string to datetime object
            transaction_date = None
            if transaction_date_str:
                transaction_date = datetime.strptime(transaction_date_str, '%d %b, %Y')

            stock_info = get_object_or_404(Stock_Information, uniqueId=stock_id)

            # Create Stock Transaction instance
            stock_transaction = StockTransaction(
                stock_information=stock_info,
                number_of_stocks=number_of_stocks_purchased,
                transaction_type=transactionType,
                notes=note,
                transaction_date=transaction_date or timezone.localtime(timezone.now()),
            )

            # Save the Stock Transaction
            stock_transaction.save()

            # Update total_purchased in Stock_Information
            stock_info.update_total_purchased()

            return JsonResponse({
                'status': 'success',
                'message': 'Stock transaction added successfully.',
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

class PortfolioAnalysisAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Assuming the user provides the analysis date in the request parameters
        analysis_date = request.query_params.get('analysis_date')

        # Get all stock information records
        all_stock_info = Stock_Information.objects.all()

        # Initialize total cash flow, total investment, total profit/loss, and overall portfolio value
        total_cash_flow = 0
        total_investment = 0
        total_profit_loss = 0
        overall_portfolio_value = 0

        # Lists to store individual stock analysis details
        stock_analysis = []

        # Loop through all stock information records
        for stock_info in all_stock_info:
            # Get the stock data for the analysis date
            stock_data = stock_info.stock_data.filter(stock_date=analysis_date).first()

            if stock_data:
                # Calculate cash flow, investment, profit/loss, and portfolio value at the analysis date for each stock
                cash_flow = stock_info.total_stocks_purchased * stock_data.CLOSE
                investment = stock_info.total_stocks_purchased * stock_info.get_latest_prices()['latest_open']
                profit_loss = cash_flow - investment
                portfolio_value = stock_info.total_stocks_purchased * stock_data.CLOSE + cash_flow

                # Accumulate total cash flow, total investment, total profit/loss, and overall portfolio value
                total_cash_flow += cash_flow
                total_investment += investment
                total_profit_loss += profit_loss
                overall_portfolio_value += portfolio_value

                # Calculate advanced financial metrics
                roi = (profit_loss / investment) * 100 if investment != 0 else 0
                roe = (profit_loss / stock_info.TTSE_IssuedShareCap) * 100 if stock_info.TTSE_IssuedShareCap != 0 else 0
                eps = (profit_loss / stock_info.TTSE_IssuedShareCap) if stock_info.TTSE_IssuedShareCap != 0 else 0

                # Individual stock analysis details
                stock_analysis.append({
                    'stock_symbol': stock_info.TTSE_Symbol,
                    'cash_flow': cash_flow,
                    'investment': investment,
                    'profit_loss': profit_loss,
                    'portfolio_value': portfolio_value,
                    'closing_price': stock_data.CLOSE,
                    'roi': roi,
                    'roe': roe,
                    'eps': eps,
                })

        # Additional overall analysis
        overall_analysis = {
            'analysis_date': analysis_date,
            'total_cash_flow': total_cash_flow,
            'total_investment': total_investment,
            'total_profit_loss': total_profit_loss,
            'overall_portfolio_value': overall_portfolio_value,
            'portfolio_percentage_change': ((overall_portfolio_value - total_investment) / total_investment) * 100 if total_investment != 0 else 0,
        }

        # Return the overall analysis and individual stock analysis as a JSON response
        return Response({'overall_analysis': overall_analysis, 'stock_analysis': stock_analysis}, status=status.HTTP_200_OK)



class PortfolioValueAPIView(APIView):
    def get(self, request, *args, **kwargs):
        analysis_date = request.query_params.get('analysis_date')

        try:
            all_stocks = Stock_Information.objects.all()
            analysis_data = self.calculate_portfolio_value(all_stocks, analysis_date)
            return Response(analysis_data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def calculate_portfolio_value(self, all_stocks, analysis_date):
        portfolio_data = []

        stock_data_entries = Stock_Data.objects.filter(
            stock_information__in=all_stocks,
            stock_date=analysis_date
        ).select_related('stock_information')

        for stock_info in stock_data_entries:
            stock_data = self.get_stock_data(stock_info, analysis_date)

            if stock_data:
                stock_value = stock_info.stock_information.total_stocks_purchased * stock_data.CLOSE
                portfolio_data.append({
                    "stock_symbol": stock_data.stock_information.TTSE_Symbol,
                    "stock_value": stock_value,
                    "closing_price": stock_data.CLOSE,
                })

        total_portfolio_value = sum(item["stock_value"] for item in portfolio_data)

        # unique_dates = Stock_Data.objects.filter(stock_date__gte='2021-12-31').values_list('stock_date', flat=True).distinct()
        unique_dates = Stock_Data.objects.filter( stock_date__gte='2021-12-31' ).annotate(last_day=TruncMonth('stock_date')).values_list('last_day', flat=True).distinct()

        # Assuming sorted_dates is already sorted
        sorted_dates = Stock_Data.objects.filter(
            stock_date__gte='2021-12-31'
        ).annotate(last_day=TruncDate('stock_date')).values_list('last_day', flat=True).distinct()

        result_data = self.calculate_total_portfolio_values(sorted_dates)
        return {
            "portfolio_data": portfolio_data,
            "total_portfolio_value": total_portfolio_value,
            "total_values": result_data
        }

    def calculate_total_portfolio_values(self, sorted_dates):
        result_data = []

        for date in sorted_dates:
            stock_data_entries = Stock_Data.objects.filter(stock_date=date).select_related('stock_information')
            total_portfolio_value = self.calculate_total_portfolio_value(stock_data_entries)
            result_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'total_portfolio_value': total_portfolio_value
            })

        return result_data

    def calculate_total_portfolio_value(self, stock_data_entries):
        total_portfolio_value = stock_data_entries.aggregate(
            total=Sum(F('stock_information__total_stocks_purchased') * F('CLOSE'), output_field=FloatField())
        )['total'] or 0

        return total_portfolio_value

    def get_stock_data(self, stock_info, analysis_date):

        try:
            # Assuming TTSE_Symbol is a unique identifier for Stock_Information
            stock_information = Stock_Information.objects.get(TTSE_Symbol=stock_info.stock_information.TTSE_Symbol)
        except Stock_Information.DoesNotExist:
            # Handle the case where the Stock_Information instance does not exist
            return None

        stock_data = Stock_Data.objects.filter(stock_information=stock_information, stock_date=analysis_date).first()

        if not stock_data:
            last_day_of_month = (pd.to_datetime(analysis_date) + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
            stock_data = Stock_Data.objects.filter(stock_information=stock_information, stock_date=last_day_of_month).first()

        return stock_data