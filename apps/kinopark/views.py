from django.shortcuts import render, get_object_or_404
from rest_framework import status
from apps.kinopark.models import *
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from apps.kinopark.serializers import *
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.core.mail import send_mail
from django.shortcuts import redirect
import jwt, datetime
import pickle
import re
import logging
import pytz
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from .models import ContactForm

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST', 'DELETE'])
def movies_list(request):
    if request.method == 'GET':
        movies = Movie.objects.all()

        title = request.GET.get('title', None)
        if title is not None:
            movies = movies.filter(movie__icontains=title)

        movies_serializer = MovieSerializer(movies, many=True)
        return JsonResponse(movies_serializer.data, safe=False)
        # return render(request, 'index.html', {'movies': movies_serializer.data, 'name': 'test'})
    elif request.method == 'POST':
        movie_data = JSONParser().parse(request)
        movie_serializer = MovieSerializer(data=movie_data)
        if movie_serializer.is_valid():
            movie_serializer.save()
            return JsonResponse(movie_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(movie_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        counter = Movie.objects.all().delete()
        return JsonResponse({'message': 'deleted'.format(counter[0])})


@api_view(['GET'])
def seans_list(request):
    if request.method == 'GET':
        seansy = Seans.objects.all()
        seans_serializer = SeansSerializer(seansy, many=True)
        return JsonResponse(seans_serializer.data, safe=False)


@api_view(['GET'])
def kinozal_by_id(request, id):
    try:
        kinozal = Kinozal.objects.get(id=id)
    except Kinozal.DoesNotExist:
        return JsonResponse({'message: Kinozal does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        kinozal_serializer = KinozalSerializer(kinozal)
        return JsonResponse(kinozal_serializer.data)


@api_view(['GET'])
def seans_by_id(request, id):
    try:
        seans = Seans.objects.get(id=id)
    except Seans.DoesNotExist:
        return JsonResponse({'message: Seans does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        seans_serializer = SeansSerializer(seans)
        return JsonResponse(seans_serializer.data)


@api_view(['POST'])
def create_order(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed("???? ?????????????????????????? ????????????????????????")

    payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    user = get_object_or_404(User, pk=payload['id'])

    order_data = JSONParser().parse(request)
    order_data.update(
        {'user': user.id}
    )

    order_serializer = CreateOrderSerializer(data=order_data)
    if order_serializer.is_valid(raise_exception=True):
        order_serializer.save()
        return JsonResponse(order_serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse("ERROR")


@api_view(['GET'])
def order_by_id(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return JsonResponse({"message": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
    order_serializer = OrderSerializer(order)
    return JsonResponse(order_serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def movie_by_id(request, pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        return JsonResponse({'message: Movie does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        movie_serializer = MovieSerializer(movie)
        return JsonResponse(movie_serializer.data)

    elif request.method == "PUT":
        new_data = JSONParser().parse(request)
        movie_serializer = MovieSerializer(movie, data=new_data)
        if movie_serializer.is_valid():
            movie_serializer.save()
            return JsonResponse(movie_serializer.data)
        return JsonResponse(movie_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        movie.delete()
        return JsonResponse({'message: the movie was deleted'})


@api_view(['GET'])
def unpublished_movies(request):
    movies = Movie.objects.filter(published=False)
    if request.method == 'GET':
        movies_serializer = MovieSerializer(movies, many=True)
        return JsonResponse(movies_serializer.data, safe=False)


class RegisterView(APIView):

    def post(self, request):
        email = request.data['email']
        serializer = UserSerializer(data=request.data)
        pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        if re.search(pattern, email):
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("OK")
            return Response(serializer.data)
        else:
            raise AuthenticationFailed("Error email")


class TicketView(APIView):
    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=self.kwargs.get('id'))
        ticket_serializer = TicketSerializer(ticket)
        return JsonResponse(ticket_serializer.data)

    def post(self, request):
        ticket_data = JSONParser().parse(request)
        ticket_serializer = CreateTicketSerialize(data=ticket_data)
        if ticket_serializer.is_valid(raise_exception=True):
            ticket_serializer.save()
            return JsonResponse(ticket_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse("ERROR")


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.get(email=email)

        if user is None:
            raise AuthenticationFailed("???????????????????????? ???? ????????????")

        if not user.check_password(password):
            raise AuthenticationFailed("???? ???????????????????? ????????????")

        user.is_active = True
        user.last_login = timezone.now()
        user.save()
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


def get_login(request):
    logger.warning('TEST')
    # logging.basicConfig(filename='info.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logging.warning('This will get logged to a file')
    return render(request, 'index.html')


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('???????????????????????? ???? ??????????????????????')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('???????????????????????? ???? ??????????????????????')

        user = User.objects.filter(id=payload['id']).first()

        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()
        user.is_active = False
        user.save()
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': '?????????? ??????????????'
        }
        return response


@api_view(['GET'])
def ticket_by_id(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket_serializer = TicketSerializer(ticket)
    return Response(ticket_serializer.data)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']

            html = render_to_string('emails/contactform.html', {
                'name': name,
                'email': email,
                'content': content
            })

            send_mail('The contact form subject', 'This is the message', 'd.ganiuly@bk.ru',
                      ['daniyal.ganiuly@gmail.com'], html_message=html)

            return JsonResponse({"message": "success"})
    else:
        form = ContactForm()

    return render(request, 'index.html', {
        'form': form
    })
