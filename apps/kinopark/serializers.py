from rest_framework import serializers
from apps.kinopark.models import *


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Order
        fields = "__all__"
        depth = 1


class CreateOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "total_price",
            "time",
            "ticket",
            "user"
        )


class CreateTicketSerialize(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "movie",
            "seans"
        )
class TicketSerializer(serializers.ModelSerializer):
    ticket_order = OrderSerializer(many=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "movie",
            "seans",
            "ticket_order"
        )

    def create(self, validated_data):
        ticket_order = validated_data.pop('ticket_order')
        ticket = Ticket.objects.create(**validated_data)
        for ticket in ticket_order:
            Order.objects.create(**ticket, ticket_order=ticket_order)
        return ticket


class KinozalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KinozalDetails
        fields = "__all__"
        depth = 1


class SeansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seans
        fields = "__all__"
        depth = 1


class KinozalSerializer(serializers.ModelSerializer):
    kinozal_details = KinozalDetailsSerializer(many=True)

    class Meta:
        model = Kinozal
        fields = (
            "id",
            "seat_quantity",
            "kinozal_details"
        )


class MovieSerializer(serializers.ModelSerializer):
    movie_seansy = SeansSerializer(many=True)

    class Meta:
        model = Movie
        fields = (
            'id',
            'title',
            'description',
            'producer',
            'rating',
            'published',
            'image',
            'movie_seansy'
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password"
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
