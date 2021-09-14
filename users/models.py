from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def get_income(self):
        income = self.orders.exclude(delivered=None).aggregate(
            Sum('items__cost')
        )['items__cost__sum']

        return income if income else 0

    def get_orders_pending(self):
        return self.orders.exclude(placed=None).filter(
            dispatched=None,
            rejected=None
        ).count()

    def get_deliveries_pending(self):
        return self.orders.exclude(dispatched=None).filter(
            delivered=None,
            rejected=None
        ).count()