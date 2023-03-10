import random

from django.db import models
from simple_history.models import HistoricalRecords
from .services.generate_fieds_for_models import default_datetime


class DiscountPercent(models.Model):
    name = models.CharField(max_length=25)
    percent = models.FloatField()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Discount percent"
        verbose_name_plural = "Discount percents"


class Status(models.TextChoices):
    active = 'Active'
    inactive = 'Inactive'
    frozen = 'Frozen'
    overdue = 'Overdue'


def default_percent():
    percent = DiscountPercent.objects.get(name='default')
    return percent


def sum_digits(x):
  res = 0

  while x:
    res += x % 10
    x //= 10

  return res


def gen_smth(N):
  digit = random.randint(1, 9)
  mid = random.randint(0, 10**N - 1)
  if sum_digits(mid) % 2:
    mid -= 1
  rez = (digit * 10**N + mid) * 10 + digit
  if Card.objects.filter(number=rez).exists() and BagCards.objects.filter(number=rez).exists():
    gen_smth(3)
  return rez


def generate_number():
    return gen_smth(3)


class CardTemplate(models.Model):
    series = models.IntegerField()
    number = models.IntegerField(default=generate_number)
    created_at = models.DateField(auto_now_add=True)
    date_end = models.DateField(default=default_datetime)
    latest_use = models.DateTimeField(auto_now=True)
    summa_purchases = models.IntegerField()
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.active
    )
    percent = models.ForeignKey(DiscountPercent, on_delete=models.CASCADE, default=default_percent)

    class Meta:
        abstract = True


class Card(CardTemplate):
    history = HistoricalRecords()

    def __str__(self):
        return f'Card {self.number}'

    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"


class BagCards(CardTemplate):
    history = HistoricalRecords()

    def __str__(self):
        return f'BagCard {self.number}'

    class Meta:
        verbose_name = "BagCard"
        verbose_name_plural = "BagCards"


class Goods(models.Model):
    name = models.CharField(max_length=50,unique=True)
    cost = models.FloatField()
    discount_cost = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Good"
        verbose_name_plural = "Goods"


class Orders(models.Model):
    goods = models.ManyToManyField(Goods)
    number = models.IntegerField(unique=True)
    date = models.DateTimeField(auto_now_add=True)
    sum = models.FloatField()
    percent = models.IntegerField(null=True, blank=True)
    discount_amount = models.FloatField(null=True, blank=True)
    card = models.ForeignKey(Card, models.SET_NULL, null=True, blank=True, related_name='order')
    bag_id = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f'order: {self.number}| date: {self.date.strftime("%m/%d/%Y, %H:%M:%S")}| sum: {self.sum}| percent:{self.percent}| discount amount: {self.discount_amount}'

    class Meta:
        ordering = ['-date']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
