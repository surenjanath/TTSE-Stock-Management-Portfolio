# -*- encoding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from uuid import uuid4

class Stock_Information(models.Model):
    TTSE_Name = models.CharField(max_length=255)
    TTSE_Symbol = models.CharField(max_length=255)

    Type = models.CharField(max_length=500)
    Note = models.CharField(max_length=500)
    Date_Started = models.DateTimeField(default=timezone.now)
    Site = models.CharField(max_length=500)

    #Utility fields
    uniqueId        = models.CharField(null=True, blank=True, max_length=100)
    slug            = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created    = models.DateTimeField(blank=True, null=True)
    last_updated    = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} | {}'.format(self.NasDaqCode, self.uniqueId)

    class Meta:
        ordering = ['date_created']

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())

        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]
            self.slug = slugify('{} | {}'.format(self.NasDaqCode, self.uniqueId))

        self.slug = slugify('{} | {}'.format(self.NasDaqCode, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(Stock_Information, self).save(*args, **kwargs)










# class Search_Results(models.Model):
#     comment                 = models.CharField(blank=True, null=True,max_length=100 )
#     author                  = models.CharField(blank=True, null=True,max_length=100 )
#     title                   = models.CharField(max_length=255)
#     publisher               = models.CharField(max_length=255)
#     year                    = models.CharField(max_length=255)
#     pages                   = models.CharField(max_length=255)
#     language                = models.CharField(max_length=50)
#     size                    = models.CharField(max_length=20)
#     extension               = models.CharField(max_length=10)
#     link                    = models.URLField()
#     md5_id                  = models.CharField(max_length=32, unique=True)  # Ensure unique MD5 IDs

#     #Foreign Key
#     searchquery = models.ForeignKey(Stock_Information, on_delete=models.CASCADE, related_name='searchFnt')

#     #Utility fields
#     uniqueId        = models.CharField(null=True, blank=True, max_length=100)
#     slug            = models.SlugField(max_length=500, unique=True, blank=True, null=True)
#     date_created    = models.DateTimeField(blank=True, null=True)
#     last_updated    = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return '{} - ({}) | {}'.format(self.title, self.searchquery.query, self.uniqueId)

#     class Meta:
#         ordering = ['date_created']

#     def save(self, *args, **kwargs):
#         if self.date_created is None:
#             self.date_created = timezone.localtime(timezone.now())

#         if self.uniqueId is None:
#             self.uniqueId = str(uuid4()).split('-')[4]
#             self.slug = slugify('{} - ({}) | {}'.format(self.title, self.searchquery.query, self.uniqueId))

#         self.slug = slugify('{} - ({}) | {}'.format(self.title, self.searchquery.query, self.uniqueId))
#         self.last_updated = timezone.localtime(timezone.now())

#         super(Search_Results, self).save(*args, **kwargs)
