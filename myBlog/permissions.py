# filepath: /D:/Internship/NewBlog/blog/myBlog/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import AccessToken
from .models import Post
import jwt, json
import os
from dotenv import load_dotenv

def decode_jwt(token):
    SECRET_KEY = os.environ.get('SECRET_KEY')
  # This should be the same secret key used to encode the token

    try:
        # Decode the token
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_payload.get('role')  
        

    except jwt.ExpiredSignatureError:
        return None



    except jwt.InvalidTokenError:
        return None

class RolePermission(BasePermission):
    def has_permission(self, request, view):
        # Allow POST for login (as it doesn't require token)
        if request.method == 'POST' and request.path == '/api/login/':
            return True

        # Token handling from Authorization header
        token = request.headers.get('Authorization')

        if not token:
            return False  # No token found in the header, access denied

        try:
            # Extract the token from the Authorization header
            token = token.split(' ')[1]  # Assuming the token is in the format "Bearer <token>"

            # Get the user role from the token
            user_role = decode_jwt(token)
            # If role is extracted successfully, check access based on role
            if user_role:
                if user_role == 'admin':
                    return True
                elif user_role == 'manager' and request.method in ['GET', 'PUT']:
                    return True
                elif user_role == 'user' and request.method in [ 'GET']:
                    return True
                return False  # Deny access if none of the conditions match
            else:
                return False  # If no role found, deny access

        except Exception as e:
            return False  # Handle any other errors (e.g., malformed token)
        

#POST BASED
##POST based permission   
def decode_id_jwt(token, request):
    SECRET_KEY = os.environ.get('SECRET_KEY')


    try:
        # Decode the token
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_role= decoded_payload.get('user_role')
        user_id= decoded_payload.get('user_id')
        user={user_role:user_role, user_id:user_id}
        request.user_id=user_id

        return user  
        

    except jwt.ExpiredSignatureError:
        return None



    except jwt.InvalidTokenError:
        return None

class PostRolePermission(BasePermission):
    def has_permission(self, request, view):
        # Allow POST for login (as it doesn't require token)
        if request.method == 'POST' and request.path == '/api/login/':
            return True

        # Token handling from Authorization header
        token = request.headers.get('Authorization')

        if not token:
            return False  # No token found in the header, access denied
        # return True

        try:
            token = token.split(' ')[1]  # Assuming the token is in the format "Bearer <token>"

            # Get the user role from the token
            # user_role = decode_jwt(token).get('role')
            # user_id=decode_jwt(token).get('user_id')
            print("Hi")

            user_role=decode_jwt(token)
            user_id=decode_id_jwt(token, request)
            print(request.user_id)
            if user_role :
                if user_role == 'admin':
                    
                    return True
                pk=view.kwargs['pk']
                if pk:
                    
                    userid = decode_id_jwt(token, request)
                    user_id=Post.objects.get(id=pk).user_id
                    if user_id==userid:
                        return True
                    else:
                        return False
                else:
                    return True    
            else:
                return False  # If no role found, deny access

        except Exception as e:
            return False  # Handle any other errors (e.g., malformed token)
        
class IsAuthLikeComment(BasePermission):
     def has_permission(self, request, view):
        # Allow POST for login (as it doesn't require token)
        if request.method == 'POST' and request.path == '/api/login/':
            return True

        # Token handling from Authorization header
        token = request.headers.get('Authorization')

        if not token:
            return False  # No token found in the header, access denied
        else:
            return True