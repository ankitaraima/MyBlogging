"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserView, PostView, CommentView, LikeView
from .views import CustomTokenObtainPairView

from django.urls import path
from .views import login, CustomTokenObtainPairView, HelloView
router = DefaultRouter()
router.register(r'users', UserView)
router.register(r'posts', PostView)
router.register(r'comments', CommentView)
router.register(r'likes', LikeView)
urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.UserOverView, name='home'),
    #user
    path('api/create/', views.create_user, name='create'),
    path('api/read/', views.read_user, name='read'),
    path('api/update/<int:pk>/', views.update_user, name='update'),
    path('api/delete/<int:pk>/', views.delete_user, name='deelte'),

    #post
    path('api/create_post/', views.create_post, name='create_post'),
    path('api/read_post/', views.read_post, name='read_post'),
    path('api/update_post/<int:pk>/', views.update_post, name='update_post'),
    path('api/delete_post/<int:pk>/', views.delete_post, name='delete_post'),

    #comment    
    path('api/create_comment/', views.create_comment, name='create_comment'),
    path('api/read_comment/', views.read_comment, name='read_comment'),
    path('api/update_comment/<int:pk>/', views.update_comment, name='update_comment'),
    path('api/delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),


    #like
    path('api/create_like/<int:post_id>/', views.create_like, name='create_like'),
    path('api/read_like/', views.read_like, name='read_like'),

    #share
    path('api/create_share/<int:post_id>/', views.create_share, name='create_share'),
    path('api/read_share/', views.read_share, name='read_share'),

    #JWT
    # path('hello/', views.HelloView.as_view(), name ='hello'),
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),     
    path('api/login/', login, name='login'),
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('hello/', HelloView.as_view(), name='hello'),

    # path('login/', views.login, name='login-MEMBER'),


]
