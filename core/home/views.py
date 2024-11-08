from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .middleware.middleware import VerifyUser
from .models import RegisterUser,Vendor,Demand
from rest_framework import status
from .helpers import SendEmail,generate_unique_code
import string, secrets, jwt, datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.forms.models import model_to_dict
# Create your views here.
@api_view(['GET'])
def authenticateMiddleware(request):
        token = request.META.get('HTTP_AUTHORIZATION') 
        print(token)
        if not token or token=="Bearer undefined":
            print("here")
            return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
        user=VerifyUser(request)
        print(user)
        if user.status_code != 200:
            return Response({'message':'Invalid User'},status.HTTP_401_UNAUTHORIZED)
        return Response({'message':user.data['message']},status.HTTP_200_OK)

#users login
@api_view(['POST'])
def login(request):
    print("Logging in")
    email=request.data['email']
    password=request.data['password']
    print("email is"+" "+email+"password is"+" "+password)
    user=RegisterUser.objects.filter(email=email).first()
    print("user is ",user)
    if user is None:
        raise AuthenticationFailed('User not found')
    if not user.check_password(password):
        raise AuthenticationFailed('Incorrect password')
    payload={
        'id':user.id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(days=1),
        'iat':datetime.datetime.utcnow()
    }
    token=jwt.encode(payload,'secret',algorithm='HS256')
    return Response({
        'message':'success',
        'jwt':token
    })
#register new users
@api_view(['POST'])
def register(request):
    data=request.data
    print('All users are:', RegisterUser.objects.all().values_list('email', flat=True))
    if RegisterUser.objects.filter(email=data['email']).exists():
        print(data)
        return Response({'message': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user=RegisterUser(
        name=data['name'],
        email=data['email'],
        role=data['role'].lower(),
        department=data['department'].lower(),
        username=data['email']
    )

    print('data is:',data)
    try:
        user.set_password(data['password'])  # Hash the password
        user.save()  # Save the user
    except Exception as e:
        print('Error during user signup:', e)
        return Response({'message': 'Failed to create user', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    payload={
            'id':user.id,
            'name':'karan',
            'exp':datetime.datetime.utcnow()+datetime.timedelta(days=1),
            'iat':datetime.datetime.utcnow()
        }
    print('Above token')

    token=jwt.encode(payload,'secret',algorithm='HS256')
    print('below token')
    return Response({
            'message':'success',
            'jwt':token
        }) 

# user will store vendor to db(if user has admin access)
@api_view(['POST'])
def MakeVendor(request):
    print(request.data)
    data=request.data['data']
    print(request.META)
    token = request.META.get('HTTP_AUTHORIZATION') 
    if not token:
            return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user=VerifyUser(request)
    role=user.data['message']['role']
    if user.status_code != 200:
        return Response({'Invalid User'},status.HTTP_401_UNAUTHORIZED)
    
    if role!='admin':
        return Response({'unable to create vendor as role not admin'},status.HTTP_401_UNAUTHORIZED)
    
    try:
        if Vendor.objects.filter(emailId=data['emailId']).exists():
            return Response({'Email already exists'},status=status.HTTP_200_OK)
        
        characters = string.ascii_letters + string.digits  # Alphanumeric characters
        random_string = ''.join(secrets.choice(characters) for _ in range(8))
        print("here")
        vendor=Vendor(
            name=data['name'],
            address=data['address'],
            city=data['city'],
            country=data['country'],
            PAN=data['PAN'],
            GST=data['GST'],
            contactNumber=data['contactNumber'],
            emailId=data['emailId']
        )
        vendor.set_password(random_string)
        vendor.full_clean() 
        vendor.save()
        SendEmail(random_string,data['emailId'])

    except Exception as e:
        print(str(e))
        return Response({'message': 'Failed to create vendor', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message':'successfuly stored password'},status=status.HTTP_200_OK)


@api_view(['POST'])
def CreateDemand(request):
    data=request.data['data']
    print('data is',data)
    token = request.META.get('HTTP_AUTHORIZATION') 
    if not token:
            return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user=VerifyUser(request)
    print('user is',user.data)
    role=user.data['message']['role']
    print('role is',role)
    if user.status_code != 200:
        return Response({'Invalid User'},status.HTTP_401_UNAUTHORIZED)
    
    if role!='admin':
        return Response({'your role is not admin'},status.HTTP_401_UNAUTHORIZED)
    print('here')
    unique_code = generate_unique_code()
    try:
        for i in range(0,len(data)):
            print(data[i])
            createDemand = Demand(
                demandId=unique_code,
                productId=generate_unique_code(),
                personId=user.data['message']['id'],
                assetType=data[i]['assetType'].lower(),
                subAsset=data[i]['subAsset'],
                location=data[i]['location'].lower(),
                department=data[i]['department'].lower(),
                category=data[i]['category'].lower(),
                description=data[i]['description'],
                make=data[i]['make'],
                model=data[i]['model'],
                version=data[i]['version'],
                quantity=data[i]['quantity'],
                partCode=data[i]['partCode'],
                delivery=data[i]['delivery'],
                leased="" if data[i]['leasedEndDate'] is None else data[i]['leased'],
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            print('creating demand')
            createDemand.full_clean()
            createDemand.save()

    except Exception as e:
        print(str(e))
        return Response({'message': 'Failed to create demand', 'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message':'Made demand Successfully'},status=status.HTTP_201_CREATED)

@api_view(['GET'])
def getMyOrders(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    print(token)
    print("queries are",request.GET.get('demandId'))
    
    if not token:
        return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Assuming VerifyUser returns user info
    user = VerifyUser(request)
    if not user:
        return Response({'message': 'Invalid token or user not found'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.GET.get('demandId'):
            print('here')
            productId=Demand.objects.filter(demandId=request.GET.get('demandId')).values('productId','subAsset','quantityPlaced','quantity','status','delivery')
            print("productIds are",productId)

            productList=list(productId)

            return Response({"message": productList}, status=status.HTTP_200_OK)


    userId = user.data['message']['id']
    myOrders = Demand.objects.filter(personId=userId).values('demandId').distinct()
    
    # Convert queryset to a list of dictionaries
    orders_data = list(myOrders)
    
    # Responding with the orders data
    return Response({"message": orders_data}, status=status.HTTP_200_OK)
