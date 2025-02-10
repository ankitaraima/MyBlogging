
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
     path('admin/', admin.site.urls),
     path('', include('myBlog.urls')),
     path('api/token/', 
         jwt_views.TokenObtainPairView.as_view(), 
         name ='token_obtain_pair'), 
     path('api/token/refresh/', 
         jwt_views.TokenRefreshView.as_view(), 
         name ='token_refresh'), 
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),#
     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')#

]
