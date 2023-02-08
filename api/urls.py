from django.urls import path 
from rest_framework.urlpatterns import format_suffix_patterns

from knox import views as knox_views

from . import views

urlpatterns = [
    path('products/create', views.ProductCreate.as_view(), name='product-list'),
    path('products/delete', views.ProductDelete.as_view(), name='product-delete'),
    path('user', views.UserDetailView.as_view()),
    path('logout', knox_views.LogoutView.as_view()),
    path('login', views.LoginView.as_view()),
    path('register', views.RegisterView.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns)
