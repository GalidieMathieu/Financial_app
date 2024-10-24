 # stocks/models.py
from django.db import models
from django.utils import timezone

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField(default=0.0)
    high_price = models.FloatField(default=0.0)
    low_price = models.FloatField(default=0.0)
    close_price = models.FloatField(default=0.0)
    volume = models.BigIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp on creation

    class Meta:
        unique_together = ('symbol', 'date')
