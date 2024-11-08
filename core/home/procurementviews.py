from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .middleware.middleware import VerifyUser
from .models import Procurement,Demand,Vendor
from rest_framework import status
from .helpers import SendEmail
import string, secrets, jwt, datetime

@api_view(['GET'])
def demandsForProcurementTeams(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    print(token)
    
    if not token:
        return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = VerifyUser(request)
    print("user is", user.data['message'])
    
    if not user:
        return Response({'message': 'Invalid token or user not found'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if user.data['message']['role'] != 'admin' and user.data['department'] == 'procurement':
        return Response({'message': 'Only procurement team with admin access has access to it'}, status=status.HTTP_401_UNAUTHORIZED)
    
    userId = user.data['message']['id']
    myOrders = Demand.objects.filter(status="in procurement").values('productId','subAsset','quantityPlaced','quantity','status','delivery','demandId')
    print(myOrders)
    
    # Use a dictionary to store orders grouped by demandId
    myOrdersInDemandIdFormat = {}

    for orders in myOrders:
        print("orders are", orders)
        
        # Check if the demand_id already exists in the dictionary
        if orders['demandId'] not in myOrdersInDemandIdFormat:
            myOrdersInDemandIdFormat[orders['demandId']] = []  # Initialize a list if this is the first time we see the demandId
        
        myOrdersInDemandIdFormat[orders['demandId']].append(orders)  # Append the order to the list
    # Convert the dictionary values to a list of lists (of orders)
    orders_data = [{"demandId":demand_id,"orders": list(orders)} for demand_id, orders in myOrdersInDemandIdFormat.items()]
    
    # Responding with the orders data
    return Response({"message": orders_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def SelectVendor(request):
    data=request.data
    print(data)
    token = request.META.get('HTTP_AUTHORIZATION') 
    if not token:
            return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user=VerifyUser(request)
    if (user.data['message']['department'].lower()!='procurement' or user.data['message']['role'].lower()!='admin'):
         return Response({'message':'Department should be procurement and role should be admin'},status=status.HTTP_401_UNAUTHORIZED)
    try:
        print(datetime.datetime.strptime(data['validTill'], '%Y-%m-%d').date())
        print("here")
        for vendorArray in data["selectionarray"]:
            print(vendorArray)
            vendorId=vendorArray['value']
            print(data)
            procurement=Procurement(
                demandId=Demand.objects.get(demandId=data['demandId']),
                productId=Demand.objects.get(productId=data['productId']),
                vendorId=Vendor.objects.get(id=vendorId),
                lastDate=datetime.datetime.strptime(data['validTill'], '%Y-%m-%d').date()
            )
            procurement.full_clean()
            procurement.save()
        return Response({"message":"Successfully made request to vendor"},status=status.HTTP_201_CREATED)
    
    except Exception as e:
         return Response({'message':'unable to create procurement request', 'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getVendors(request):
    data=request.data
    print(data)
    token = request.META.get('HTTP_AUTHORIZATION') 
    if not token:
            return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user=VerifyUser(request)

    if (user.data['message']['role'].lower()!='admin'):
         return Response({'message':'Department should be procurement and role should be admin'},status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        vendors=Vendor.objects.all().values("id","name")
        print(vendors)
        vendorsList=list(vendors)
        return Response({"message":vendorsList},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message":str(e)},status=status.HTTP_400_BAD_REQUEST)
