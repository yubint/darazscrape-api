import re
import requests

from django.contrib.auth import login

from rest_framework.views import APIView
from rest_framework import status, generics, permissions
from rest_framework.response import Response

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from .models import Product, Price
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
        if 'https://daraz.com.np/products/' not in url:
            return Response({"error":"incorrect url"}, status=status.HTTP_400_BAD_REQUEST)
        
        new_url = re.match(r'.*html', url).group() 

        # If the product is already in the database then associating the user with the product else adding that product in database:
        try:
            product = Product.objects.get(url=new_url)
            product.users.add(self.request.user)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist: 
            try:
                data = scrape_data(new_url)
            except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
                return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = ProductSerializer(data = data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            product = serializer.save()

            product.users.add(self.request.user)
            Price.objects.create(price = data.get('price'), product=product)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductDelete(APIView):
    '''
    Delete the products for the user given the product id
    '''
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        product_id = request.data.get('productId')
        if product_id is None:
            return Response({"error":"product id not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(pk=product_id)
            product.users.remove(self.request.user)
            return Response(status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error":"Product does not exist"}, status=status.HTTP_400_BAD_REQUEST)

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
    Login the User with keys user and password
    '''

    permission_classes = [permissions.AllowAny]

    def post(self , request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user =serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None) 
