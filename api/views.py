import re

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login

from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework import status, generics, permissions
from rest_framework.response import Response

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from .models import User, Product, Price
from .serializers import ProductSerializer, UserSerializer, RegisterUserSerializer, AuthTokenSerializer
from .scrape import scrape_data

# Create your views here.
class ProductCreate(APIView):
    '''
    Associate the user to a products if it's already in the database.
    Else add the products to the database and then associate it to the user.
    '''

    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        url = request.data.get('url') 
        if url is None:
            return Response({"error": "url not provided"},status=status.HTTP_400_BAD_REQUEST)
        
        new_url = re.match(r'.*html', url).group() 

        # If the product is already in the database then associating the user with the product else adding that product in database:
        try:
            product = Product.objects.get(url=new_url)
            product.users.add(self.request.user)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist: 
            data = scrape_data(new_url)
            if data.get('error'):
                return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            request.data['url'] = new_url
            request.data['title'] = data.get('title')
            request.data['image_url'] = data.get('image_url')

            serializer = ProductSerializer(data = request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            product = serializer.save()

            product.users.add(self.request.user)
            Price.objects.create(price = data.get('price'), product=product)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UserDetailView(generics.RetrieveAPIView):
    '''
    Get the detail about a user 
    '''
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user

class RegisterView(APIView):
    '''
    Register the users 
    '''
    def post(self, request, format=None):
        serializer = RegisterUserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })

class LoginView(KnoxLoginView):
    '''
    Login the User 
    '''

    permission_classes = [permissions.AllowAny]

    def post(self , request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user =serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None) 