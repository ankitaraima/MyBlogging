from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from django.db.models import Sum
from .models import User, Post, Comment, like_share
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import jwt
import os
import csv
from django.conf import settings
# JWT
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import RolePermission,PostRolePermission,IsAuthLikeComment  # Import RolePermission

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
# Create your views here.
class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
class CommentView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer    
class LikeView(viewsets.ModelViewSet):        
    queryset = like_share.objects.all()
    serializer_class = LikeSerializer  
# Create your views here.

@api_view(['GET','POST','DELETE','PUT'])
def UserOverView(request):
    api_urls    = { 'all_user': '/', 
                   'search by email': '/?email=email',
                   'search by id': '/?id=id',
                     'add': '/create', 
                     'update': '/update/pk', 
                     'delete': '/delete/pk',
                      "search by post category": "/?category=category",
                      "search by post id": "/?id=id",
                      "search by user id": "/?user_id=user_id",
                      "search by post authon": "/?author=author",}
    return Response(api_urls)


#========================================USER=========================================
# Create User
@api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdmin])
@permission_classes([RolePermission])
def create_user(request):
    item=UserSerializer(data=request.data)
    if User.objects.filter(email=request.data['email']).exists():
        return Response({"error": "Email already exists"})
    if item.is_valid():
        item.save()
        return Response({"status": "User created", "data": item.data,"status_code":201,"success":True,"message":"User created successfully"})

    return Response({"error":item.errors,"status_code":400,"success":False,"message":"User not created"})
# Read User

# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @permission_classes([IsAuthenticated, RolePermission]) 
# def read_user(request):
#     x = RolePermission.has_permission( True,request)
#     if not x:
#         return Response({"error": "no Authentication"})
#     if permission_classes:
#         if request.query_params:
#             item=User.objects.filter(**request.query_params.dict())
#         else:
#             item=User.objects.all()
#         if item:
#             serializer=UserSerializer(item,many=True)
#             return Response({"message":"The all records of"+str(request.query_params.dict())+"is listed below","data":serializer.data,"status_code":200,"success":True})      
#     return Response({"error":"No records found","status_code":404,"success":False})


@api_view(['GET'])
@permission_classes([RolePermission])
def read_user(request):
    if request.GET:
        item = User.objects.filter(**request.GET.dict())
    else:
        item = User.objects.all()
    if item:
        serializer = UserSerializer(item, many=True)
        return Response({"message": "The all records of" + str(request.GET.dict()) + "is listed below", "data": serializer.data, "status_code": 200, "success": True})
    return Response({"error": "No records found", "status_code": 404, "success": False})

# Update User
@api_view(['PUT'])
# @permission_classes([IsAuthenticated, IsAdmin|IsManager])
@permission_classes([RolePermission])

def update_user(request,pk):
    if not isinstance(pk,int):
        return Response({"error":"Invalid id","status_code":400,"success":False})
    item=User.objects.get(id=pk)
    serializer=UserSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"User updated successfully","data":serializer.data,"status_code":200,"success":True})
    return Response({"error":serializer.errors,"status_code":400,"success":False})

# Delete User
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated, IsAdmin])
@permission_classes([RolePermission])

def delete_user(request,pk):
    if not isinstance(pk,int):
        return Response({"error":"Invalid id","status_code":400,"success":False})
    item=User.objects.get(id=pk)
    if item.delete():
        return Response({"message":"User deleted successfully","status_code":200,"success":True})
    return Response({"error":"User not deleted","status_code":400,"success":False})


#========================================POST=========================================
# Create Post
@api_view(['POST']) 
@permission_classes([PostRolePermission])

def create_post(request):
    item=PostSerializer(data=request.data)
    user = request.data['user_id']
    print(request.user_id)
    
    if request.user_id == user:
        if item.is_valid():
            post=item.save()

            return Response({"status": "Post created", "data": item.data,"status_code":201,"success":True,"message":"Post created successfully"})

        return Response({"error":item.errors,"status_code":400,"success":False,"message":"Post not created"})
    else:
        return Response({"error": "You are not authorized to create post for other user"})

CSV_DIR = os.path.join(settings.BASE_DIR, 'blog', 'csv_files')
CSV_FILE_PATH = os.path.join(CSV_DIR, 'post_clicks.csv')

os.makedirs(CSV_DIR, exist_ok=True)

@api_view(['GET'])
@permission_classes([PostRolePermission])
def read_post(request):
    if request.query_params:
        if(request.query_params.get("id")):
            post=request.query_params.get("id")
            post=int(post)
            item = Post.objects.filter(id=post).first()
        else:    
            item = Post.objects.filter(**request.query_params.dict()).first()  # Use .first() to get a single record
        user_id = request.user_id  # Assuming authentication is used
        post_id = item.id
        data=check_prediction(user_id, post_id)
        # print(data)
        if item :
            if request.session.get('post_id'):
                print("Session exists")
                user_id = request.user_id  # Assuming authentication is used
                clicks=item.id
                if user_id and post_id and clicks:
                    
                    post_id = request.session.get('post_id')
                    # print(user_id, post_id,clicks)

                    update_csv(user_id, post_id,clicks)
            serializer = PostSerializer(item)  # No need for many=True since it's a single object
            request.session['post_id'] = item.id
              # Directly access the id of the single post
           
            

            return Response({
                "message": f"The record for post ID {post_id} is listed below... you more can search about the post_id->{data}, most of the people are visting this post",
                "data": serializer.data,
                "status_code": 200,
                "success": True
            })
        else:
            return Response({
                "error": "No records found",
                "status_code": 404,
                "success": False
            })

    item = Post.objects.all()
    serializer = PostSerializer(item, many=True)

    return Response({
        "message": "All records are listed below",
        "data": serializer.data,
        "status_code": 200,
        "success": True
    })
import os
import csv
CSV_DIR = os.path.join(settings.BASE_DIR, 'blog', 'csv_files')
CSV_FILE_PATH = os.path.join(CSV_DIR, 'post_clicks.csv')
# CSV_FILE_PATH = "your_file.csv"  # Update this with the actual file path

def update_csv(user_id, post_id, clicks):
    """Appends or updates the CSV file with user_id, post_id, and click count."""
    data = []
    file_exists = os.path.isfile(CSV_FILE_PATH)

    # Ensure directory exists before writing the file
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)

    # Read existing data **before** the file is closed
    if file_exists:
        try:
            with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                data = [row for row in reader if row]  # Store data before file closes
                print("Existing data read from CSV:", data)
        except Exception as e:
            print(f"Error reading CSV: {e}")

    header = ['user_id', 'post_id', 'clicks']
    updated = False

    print("Checking for existing entries in CSV...")
    
    # Ensure we don't modify the header row
    if data and data[0] == header:
        data_rows = data[1:]  # Exclude header
    else:
        data_rows = data

    for row in data_rows:
        if row[0] == str(user_id) and row[1] == str(post_id):
            row[2] = str(int(row[2]) + 1)  # Increment click count
            updated = True
            print(f"Updated existing entry: {row}")
            break

    # If entry doesn't exist, add a new one
    if not updated:
        data_rows.append([str(user_id), str(post_id), str(clicks)])
        print("Added new entry:", [str(user_id), str(post_id), str(clicks)])

    # Write back the data
    try:
        with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Ensure header is written
            writer.writerows(data_rows)  # Write data rows
            print("CSV updated successfully.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

CSV_DIR = os.path.join(settings.BASE_DIR, 'blog', 'csv_files')
CSV_FILE_PATH = os.path.join(CSV_DIR, 'post_clicks.csv')

os.makedirs(CSV_DIR, exist_ok=True)
def check_prediction(user_id, post_id):
    """Check if the user_id and post_id are in the CSV file and return the prediction."""
    data = []
    file_exists = os.path.isfile(CSV_FILE_PATH)

    # Ensure directory exists before writing the file
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)

    # Read existing data
    if file_exists:
        try:
            with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                data = list(reader)
                # return data
                # print("Existing data read from CSV:", data)
        except Exception as e:
            print(f"Error reading CSV: {e}")

    for row in data:
        if row[0] == str(user_id) and row[1] == str(post_id):
            pass
            # return row[2]

        else:
            import pandas as pd
            from io import StringIO
            df=pd.read_csv(r'D:\Internship\NewBlog\Blog\Blog\csv_files\post_clicks.csv')
            x=df.iloc[:,0:2].values
            y=df.iloc[:,2].values

            import numpy as np
            import matplotlib.pyplot as plt
            from sklearn.model_selection import train_test_split
            x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=42)
            from sklearn.preprocessing import StandardScaler
            scaler=StandardScaler()
            x_train=scaler.fit_transform(x_train)
            x_test=scaler.transform(x_test)
            from sklearn.linear_model import LinearRegression
            #cross validation
            from sklearn.model_selection import cross_val_score

            regression=LinearRegression()
            regression.fit(x_train,y_train)
            mse=cross_val_score(regression,x_train,y_train,scoring='neg_mean_squared_error',cv=50)
            np.mean(mse)

            reg_preduct=regression.predict(x_test)
            import seaborn as sns
            sns.displot(reg_preduct-y_test,kind='kde')

            from sklearn.metrics import r2_score
            score=r2_score(reg_preduct,y_test)
            import numpy as np
            # user_id = 21
            # post_id = 52
            model = LinearRegression()

            model.fit(x_train, y_train)
            input_data = np.array([[user_id, post_id]])

             

            return int(prediction[0])


            # return y

@api_view(['PUT'])
@permission_classes([PostRolePermission])

def update_post(request,pk):
    if not isinstance(pk,int):
        return Response({"error":"Invalid id","status_code":400,"success":False})
    item=Post.objects.get(id=pk)
    serializer=PostSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Post updated successfully","data":serializer.data,"status_code":200,"success":True})
    return Response({"error":serializer.errors,"status_code":400,"success":False})
# Delete Post   
@api_view(['DELETE']) 
@permission_classes([PostRolePermission])

def delete_post(request,pk):
    if not isinstance(pk,int):
        return Response({"error":"Invalid id","status_code":400,"success":False})
    item=Post.objects.get(id=pk)
    if item.delete():
        item2=like_share.objects.get(post_id=pk)
        if item2.delete():
            return Response({"message":"Post deleted successfully","status_code":200,"success":True})
    return Response({"error":"Post not deleted","status_code":400,"success":False})

#========================================COMMENT=========================================
# Create Comment
@api_view(['POST'])
def create_comment(request):
    item=CommentSerializer(data=request.data)
    if item.is_valid():
        item.save()
        return Response({"status": "Comment created", "data": item.data,"status_code":201,"success":True,"message":"Comment created successfully"})

    return Response({"error":item.errors,"status_code":400,"success":False,"message":"Comment not created"})
# Read Comment
@api_view(['GET'])
def read_comment(request):
    if request.query_params:
        item=Comment.objects.filter(**request.query_params.dict())
    else:
        item=Comment.objects.all()
    if item:
        serializer=CommentSerializer(item,many=True)
        return Response({"message":"The all records of"+str(request.query_params.dict())+"is listed below","data":serializer.data,"status_code":200,"success":True})      
    return Response({"error":"No records found","status_code":404,"success":False})

# Update Comment
@api_view(['PUT'])
def update_comment(request,pk):
    if not isinstance(pk,int):
        return Response({"error":"Invalid id","status_code":400,"success":False})
    item=Comment.objects.get(id=pk)
    serializer=CommentSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Comment updated successfully","data":serializer.data,"status_code":200,"success":True})
    return Response({"error":serializer.errors,"status_code":400,"success":False})

# Delete Comment
@api_view(['DELETE'])
def delete_comment(request,pk):
    if not isinstance(pk,int):
        return Response({"error":"Invalid id","status_code":400,"success":False})
    item=Comment.objects.get(id=pk)
    if item.delete():
        return Response({"message":"Comment deleted successfully","status_code":200,"success":True})
    return Response({"error":"Comment not deleted","status_code":400,"success":False})
#========================================LIKE=========================================
# Create Like
@api_view(['PUT']) 
@permission_classes([IsAuthLikeComment])

def create_like(request, post_id):
    user_id = request.data.get('user_id')
    
    if not isinstance(post_id, int):
        return Response({"error": "Invalid Post ID", "status_code": 400, "success": False})
    if not isinstance(user_id, int):
        return Response({"error": "Invalid User ID", "status_code": 400, "success": False})

 
    post=Post.objects.filter(id=post_id).exists()
    user=User.objects.filter(id=user_id).exists()
    if post and user:
            item=like_share.objects.filter(post_id=post_id, user_id=user_id).exists()
            if item:
                item = like_share.objects.get(post_id=post_id, user_id=user_id)
                if item.like == 1:
                    item.like = 0
                    message = "Like removed successfully"
                else:
                    item.like = 1
                    message = "Like created successfully"
                item.save()
                return Response({"message": message, "status_code": 200, "success": True})
            else:
                like_share.objects.create(post_id=post_id, user_id=user_id, like=1, share=0)
                return Response({"message": "Like created successfully", "status_code": 200, "success": True})
    else:
            return Response({"error": "Post or User does not exist", "status_code": 400, "success": False})    
       

# Read Like
@api_view(['GET'])
@permission_classes([IsAuthLikeComment])

def read_like(request):
    # Check if `post_id` is provided as a query parameter
    post_id = request.query_params.get('post_id')
    if post_id:
        try:
            # Validate `post_id` as an integer
            post_id = int(post_id)
        except ValueError:
            return Response({"error": "Invalid Post ID", "status_code": 400, "success": False})

        # Fetch the total likes and shares for the specific post
        result = (
            like_share.objects.filter(post_id=post_id)
            .aggregate(total_likes=Sum('like'), total_shares=Sum('share'))
        )
        total_likes = result['total_likes'] or 0
        total_shares = result['total_shares'] or 0

        # Return the result for the specific post
        return Response({
            "post_id": post_id,
            "total_likes": total_likes,
            "total_shares": total_shares,
            "status_code": 200,
            "success": True
        })
    else:
        # Fetch total likes and shares grouped by `post_id`
        result = (
            like_share.objects.values('post_id')
            .annotate(total_likes=Sum('like'), total_shares=Sum('share'))
            .order_by('post_id')
        )

        # Return the result for all posts
        return Response({
            "message": "Total likes and shares for all posts",
            "data": list(result),
            "status_code": 200,
            "success": True
        })


# ========================================SHARE=========================================
# Create Share
@api_view(['PUT'])
@permission_classes([IsAuthLikeComment])

def create_share(request,post_id):
    user_id = request.data.get('user_id')
    
    if not isinstance(post_id, int):
        return Response({"error": "Invalid Post ID", "status_code": 400, "success": False})
    if not isinstance(user_id, int):
        return Response({"error": "Invalid User ID", "status_code": 400, "success": False})

 
    post=Post.objects.filter(id=post_id).exists()
    user=User.objects.filter(id=user_id).exists()
    if post and user:
            item=like_share.objects.filter(post_id=post_id, user_id=user_id).exists()
            if item:
                item = like_share.objects.get(post_id=post_id, user_id=user_id)
                if item.share == 1:
                    item.share = 0
                    message = "shared successfully"
                else:
                    item.share = 1
                    message = "Unshared successfully"
                item.save()
                return Response({"message": message, "status_code": 200, "success": True})
            else:
                like_share.objects.create(post_id=post_id, user_id=user_id, like=0, share=1)
                return Response({"message": "shared successfully", "status_code": 200, "success": True})
    else:
            return Response({"error": "Post or User does not exist", "status_code": 400, "success": False})    
       
# Read Share
@api_view(['GET'])
@permission_classes([IsAuthLikeComment])

def read_share(request):
    # Check if `post_id` is provided as a query parameter
    post_id = request.query_params.get('post_id')
    if post_id:
        try:
            # Validate `post_id` as an integer
            post_id = int(post_id)
        except ValueError:
            return Response({"error": "Invalid Post ID", "status_code": 400, "success": False})

        # Fetch the total likes and shares for the specific post
        result = (
            like_share.objects.filter(post_id=post_id)
            .aggregate(total_likes=Sum('like'), total_shares=Sum('share'))
        )
        total_likes = result['total_likes'] or 0
        total_shares = result['total_shares'] or 0

        # Return the result for the specific post
        return Response({
            "post_id": post_id,
            "total_likes": total_likes,
            "total_shares": total_shares,
            "status_code": 200,
            "success": True
        })
    else:
        # Fetch total likes and shares grouped by `post_id`
        result = (
            like_share.objects.values('post_id')
            .annotate(total_likes=Sum('like'), total_shares=Sum('share'))
            .order_by('post_id')
        )

        # Return the result for all posts
        return Response({
            "message": "Total likes and shares for all posts",
            "data": list(result),
            "status_code": 200,
            "success": True
        })



#========================================LOGIN=========================================
  
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .serializers import CustomTokenObtainPairSerializer
from dotenv import load_dotenv

load_dotenv()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class HelloView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        content = {'message': 'Hello, GeeksforGeeks'}
        return Response(content)

#========================================ACTUAL LOGIN=========================================

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # print("ffffffffff",)

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # env = environ.Env()
        # environ.Env.read_env()  # Read the .env file

# Fetch the secret key from the environment
        SECRET_KEY = os.environ.get('SECRET_KEY')
        # SECRET_KEY='secret'
        
        member = User.objects.get(username=username)
        if password == member.password:
            role = member.type

            payload = {
                'user_id': member.id,
                'role': role
            }
            token=jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            # refresh = RefreshToken.for_user(member)
            # access_token = (refresh.access_token)
            # access_token['role']=member.type
            # access_token=str(access_token)
            return Response({
                'message': f'Login successful as {role}!',
                
                'role': role,
                'access_token': token,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'Invalid username.'}, status=status.HTTP_401_UNAUTHORIZED)
