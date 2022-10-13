from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms


class Movie(models.Model):
    title = models.CharField(max_length=70, blank=False, default='')
    description = models.CharField(max_length=300, blank=False, default='')
    producer = models.CharField(max_length=50, blank=False, default='')
    rating = models.FloatField(blank=False)
    published = models.BooleanField(default=False)
    image = models.CharField(max_length=255, null=True)

    @property
    def movie_seansy(self):
        return self.seans_set.all()


class Ticket(models.Model):
    seans = models.ForeignKey('Seans', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)

    @property
    def ticket_order(self):
        return self.order_set.all()


class Order(models.Model):
    total_price = models.BigIntegerField(blank=False)
    time = models.DateTimeField(auto_now=True)
    ticket = models.ForeignKey('Ticket', on_delete=models.PROTECT)
    user = models.ForeignKey('User', on_delete=models.PROTECT)

    @property
    def ticket_id(self):
        return self.ticket_id

    @property
    def user_id(self):
        return self.user_id


class User(AbstractUser):
    first_name = models.CharField(max_length=80, blank=False)
    last_name = models.CharField(max_length=80, blank=False)
    email = models.CharField(max_length=90, blank=False, unique=True)
    username = models.CharField(max_length=90, blank=True, null=True, unique=True)
    password = models.CharField(max_length=90, blank=False)
    # username = None

    # USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class Seans(models.Model):
    price = models.BigIntegerField(null=False)
    time = models.TimeField()
    kinozal = models.ForeignKey('Kinozal', on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)


class Kinozal(models.Model):
    seat_quantity = models.IntegerField()

    @property
    def kinozal_details(self):
        return self.kinozaldetails_set.all()


class KinozalDetails(models.Model):
    seat_numeration = models.IntegerField()
    available = models.BooleanField()
    kinozal = models.ForeignKey('Kinozal', on_delete=models.CASCADE)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    content = forms.CharField(widget=forms.Textarea)
