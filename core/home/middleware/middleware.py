import jwt
from ..models import RegisterUser
from rest_framework.response import Response
from rest_framework import status

def VerifyUser(request):
        token = request.META.get('HTTP_AUTHORIZATION') 
        if not token:
            return Response({'message': 'Token is missing'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(token.split(' ')[1], 'secret', algorithms=['HS256'])
            user_id = payload['id']
            user = RegisterUser.objects.get(id=user_id)
            user_json=user.to_json()
            if user!="":
                return Response({'message': user_json}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except RegisterUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)