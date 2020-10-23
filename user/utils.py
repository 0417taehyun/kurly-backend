import jwt
import json

from django.http             import JsonResponse
from .models                 import User
from kurly.settings          import SECRET_KEY, ALGORITHM

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            if access_token is None:
                JsonResponse({"message": 'INVALID_USER'}, status=401)
            payload = jwt.decode(access_token, SECRET_KEY, algorithm = ALGORITHM)
            user = User.objects.get(id = payload['id'])
            request.user = user
       
        except jwt.DecodeError:
            return JsonResponse({"message" : 'EXPIRED_TOKEN'}, status = 401)
        
        except User.DoesNotExist:
            return JsonResponse({'message' : 'NO_EXISTS_USER'}, status = 404)
        
        return func(self, request, *args, **kwargs)

    return wrapper