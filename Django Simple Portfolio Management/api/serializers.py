from rest_framework import  serializers
from api.models import *

class Stock_InformationSerializer(serializers.ModelSerializer):

    latest_open = serializers.SerializerMethodField()
    latest_close = serializers.SerializerMethodField()

    class Meta:
        model = Stock_Information
        fields = ('id','No_days_since_start','TTSE_Name','TTSE_Symbol','TTSE_Sector','TTSE_Website','TTSE_IssuedShareCap','TTSE_MarketCap','Type','Note','Date_Started','Site', 'latest_open', 'latest_close')

    def get_latest_open(self, obj):
        return obj.get_latest_prices()['latest_open']

    def get_latest_close(self, obj):
        return obj.get_latest_prices()['latest_close']