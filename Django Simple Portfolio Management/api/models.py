# -*- encoding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from uuid import uuid4

from django.db.models.signals import post_save



from .Functions import get_TTSE_Auth


class Webscraping_Header(models.Model):
    header          = models.CharField(max_length=255, null=True, blank=True,)
    cookie_code     = models.CharField(max_length=500, null=True, blank=True,)
    time_remaining  = models.IntegerField(default=3600*8) # Seconds
    status          = models.BooleanField(default=True)
    message         = models.CharField(max_length=500, null=True, blank=True,)
    #Utility fields
    uniqueId        = models.CharField(null=True, blank=True, max_length=100)
    slug            = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created    = models.DateTimeField(blank=True, null=True)
    last_updated    = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} | {}'.format(self.status, self.uniqueId)

    class Meta:
        ordering = ['date_created']

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())

        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} | {}'.format(self.status, self.uniqueId))

        self.slug = slugify('{} | {}'.format(self.status, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Webscraping_Header, self).save(*args, **kwargs)

    def generate_new_code(self):
        print("[*] Generating New Code. Please Wait...")
        HEADER = self.header
        return get_TTSE_Auth(HEADER)




class Stock_Information(models.Model):
    TTSE_Name = models.CharField(max_length=255)
    TTSE_Symbol = models.CharField(max_length=255)
    TTSE_Sector = models.CharField(max_length=255, null=True, blank=True)
    TTSE_Website = models.CharField(max_length=255, null=True, blank=True)
    TTSE_IssuedShareCap = models.IntegerField(default=0)
    TTSE_MarketCap = models.FloatField(default=0.0)
    Type = models.CharField(max_length=500, null=True, blank=True)
    Note = models.CharField(max_length=500, null=True, blank=True)
    Date_Started = models.DateTimeField(default=timezone.now)
    Site = models.CharField(max_length=500, null=True, blank=True)

    total_stocks_purchased = models.FloatField(default=0)
    total_stocks_sold = models.FloatField(default=0)

    No_days_since_start = models.IntegerField(default=0, editable=False)

    #Utility fields
    uniqueId        = models.CharField(null=True, blank=True, max_length=100)
    slug            = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created    = models.DateTimeField(blank=True, null=True)
    last_updated    = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} | {}'.format(self.TTSE_Symbol, self.uniqueId)

    class Meta:
        ordering = ['date_created']

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())

        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} | {}'.format(self.TTSE_Symbol, self.uniqueId))

        super(Stock_Information, self).save(*args, **kwargs)

        # Calculate the total stocks purchased
        total_purchased = self.transactions.filter(transaction_type='BUY').aggregate(models.Sum('number_of_stocks'))['number_of_stocks__sum']
        self.total_stocks_purchased = total_purchased or 0

        # Calculate the total stocks sold
        total_sold = self.transactions.filter(transaction_type='SELL').aggregate(models.Sum('number_of_stocks'))['number_of_stocks__sum']
        self.total_stocks_sold = total_sold or 0

        self.slug = slugify('{} | {}'.format(self.TTSE_Symbol, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        self.No_days_since_start = (timezone.now() - self.Date_Started).days

        super(Stock_Information, self).save(*args, **kwargs)

    def get_latest_prices(self):
        # Get the latest opening and closing prices
        latest_data = self.stock_data.order_by('-stock_date').first()
        if latest_data:
            return {
                'latest_open': latest_data.OPEN,
                'latest_close': latest_data.CLOSE,
            }
        return {
            'latest_open': None,
            'latest_close': None,
        }

    def update_total_purchased(self):
        # Update the total_purchased field based on the sum of 'BUY' transactions
        total_purchased = self.transactions.filter(transaction_type='BUY').aggregate(models.Sum('number_of_stocks'))['number_of_stocks__sum']
        total_sold = self.transactions.filter(transaction_type='SELL').aggregate(models.Sum('number_of_stocks'))['number_of_stocks__sum']
        self.total_purchased = total_purchased or 0
        self.total_sold = total_sold or 0
        self.save()

class StockTransactionManager(models.Manager):
    def total_stocks_sold(self, stock_info):
        return self.filter(stock_information=stock_info, transaction_type='SELL').aggregate(models.Sum('number_of_stocks'))['number_of_stocks__sum'] or 0

class StockTransaction(models.Model):
    stock_information = models.ForeignKey(Stock_Information, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    number_of_stocks = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    notes           = models.CharField(null=True, blank=True, max_length=500)


    # Utility fields
    unique_id = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    objects = StockTransactionManager()

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = str(uuid4()).split('-')[4]
            self.slug = slugify('{}-{}'.format(self.transaction_type, self.unique_id))

        super(StockTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return '{} | {}'.format(self.stock_information.TTSE_Symbol, self.unique_id)

    class Meta:
        ordering = ['-transaction_date']



class Stock_Data(models.Model):

    stock_information = models.ForeignKey(Stock_Information, on_delete=models.CASCADE, related_name='stock_data')
    OPEN = models.FloatField()
    CLOSE = models.FloatField()
    VOLUME_TRADED = models.FloatField()
    stock_date = models.DateTimeField(blank=True, null=True)

    #Utility fields
    uniqueId        = models.CharField(null=True, blank=True, max_length=100)
    slug            = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created    = models.DateTimeField(blank=True, null=True)
    last_updated    = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} | {}'.format(self.stock_information.TTSE_Symbol, self.uniqueId)

    class Meta:
        ordering = ['stock_date']

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())

        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} | {}'.format(self.stock_information.TTSE_Symbol, self.uniqueId))

        self.slug = slugify('{} | {}'.format(self.stock_information.TTSE_Symbol, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Stock_Data, self).save(*args, **kwargs)
