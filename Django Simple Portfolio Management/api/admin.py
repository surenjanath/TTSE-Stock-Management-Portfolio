
from django.contrib import admin
from api.models import *

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock_information', 'transaction_type', 'number_of_stocks', 'transaction_date_display')
    list_filter = ('transaction_type', 'stock_information__TTSE_Symbol')
    search_fields = ('stock_information__TTSE_Symbol', 'transaction_type')
    ordering = ('-transaction_date',)

    def transaction_date_display(self, obj):
        return obj.transaction_date.strftime("%d %b, %Y %H:%M:%S")

    transaction_date_display.short_description = 'Transaction Date'


@admin.register(Webscraping_Header)
class WebscrapingHeaderAdmin(admin.ModelAdmin):
    # Customize the admin options if needed
    list_display = ['header', 'cookie_code', 'time_remaining', 'status', 'uniqueId', 'slug', 'date_created', 'last_updated']
    # ... (other options)



@admin.register(Stock_Information)
class Stock_InformationAdmin(admin.ModelAdmin):
    list_display = ['TTSE_Name', 'TTSE_Symbol', 'TTSE_Sector', 'TTSE_Website', 'TTSE_IssuedShareCap', 'TTSE_MarketCap', 'Type', 'Note', 'Date_Started', 'Site']
    search_fields = ['TTSE_Name', 'TTSE_Symbol', 'TTSE_Sector']

@admin.register(Stock_Data)
class Stock_DataAdmin(admin.ModelAdmin):
    list_display = ['get_ttse_name', 'get_ttse_symbol', 'get_ttse_sector', 'OPEN', 'CLOSE', 'VOLUME_TRADED', 'stock_date']
    list_select_related = ['stock_information']

    def get_ttse_name(self, obj):
        return obj.stock_information.TTSE_Name

    get_ttse_name.short_description = 'TTSE Name'
    get_ttse_name.admin_order_field = 'stock_information__TTSE_Name'

    def get_ttse_symbol(self, obj):
        return obj.stock_information.TTSE_Symbol

    get_ttse_symbol.short_description = 'TTSE Symbol'
    get_ttse_symbol.admin_order_field = 'stock_information__TTSE_Symbol'

    def get_ttse_sector(self, obj):
        return obj.stock_information.TTSE_Sector

    get_ttse_sector.short_description = 'TTSE Sector'
    get_ttse_sector.admin_order_field = 'stock_information__TTSE_Sector'