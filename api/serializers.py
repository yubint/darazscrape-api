from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import User, Product, Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['price', 'date']
    
class ProductSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(read_only= True, many=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'url', 'image_url', 'prices']
    

class UserSerializer(serializers.ModelSerializer):
    products = ProductSerializer(Product.objects.all(), many=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'products']
    
class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password']
        extra_kwargs = {'password' : {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'])
        return user

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        write_only=True
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace = False,
        write_only=True
    )
    token = serializers.CharField(
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = ('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = ('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs