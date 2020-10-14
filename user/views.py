import json
import bcrypt
import jwt

from django.views           import View
from django.http            import JsonResponse
from django.core.exceptions import (
    ValidationError,
    ObjectDoesNotExist
)

from user.models  import (
    User
)
from user.utils import login_required

from kurly import local_settings
from .validator import (
    account_validate,
    account_overlap,
    password_validate,
    email_validate,
    email_overlap,
    phone_number_validate
)

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            account      = data['account']
            if(account_validate(account)):
                if(account_overlap(account)):
                    raise ValidationError('ACCOUNT_OVERLAPED')
            else:
                raise ValidationError('INVALID_ACCOUNT_INPUT')
                
            email        = data.get('email', None)
            
            if (email):
                password     = data['password']
                name         = data['name']
                email        = data['email']
                phone_number = data['phone_number']
                address      = data['address']

                email_validate(email)
                email_overlap(email)
                password_validate(password)
                phone_number_validate(phone_number)

                password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                password = password.decode('utf-8')

                User(
                    account        = account,
                    password       = password,
                    name           = name,
                    email          = email,
                    phone_number   = phone_number,
                    gender         = data['gender'],
                    birth          = data['birth']
                ).save()
                return JsonResponse({'message':'SIGNUP_SUCCESS'}, status = 200)

            return JsonResponse({'message':'ACCOUNT_SUCCESS'}, status = 400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)

        except ValidationError as e:
            return JsonResponse({'message':e.message}, status = 400)

class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            account    = data['account']
            password   = data['password']

            if User.objects.filter(account = account).exists():
                user = User.objects.get(account = account)

                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    access_token = jwt.encode(
                        {'id':user.id}, local_settings.SECRET_KEY, algorithm = local_settings.ALGORITHM
                    ).decode('utf-8')
                    return JsonResponse({'ACCESS_TOKEN': access_token}, status = 200)

                return JsonResponse({'message':'INVALID_INPUT'}, status = 400)

            return JsonResponse({'message':'INVALID_USER'}, status = 400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)

class KakaoSignInView(View):
    def get(self, request):
        try:
            access_token    = request.headers.get('Authorization', None)
            if access_token == None:
                return JsonResponse({'message' : 'no_auth_token'}, status = 401)

            payload_json = requests.get(
                'https://kapi.kakao.com/v2/user/me', 
                headers = {
                    "Authorization": f"Bearer {access_token}"
                }
            ).json

            email      = payload_json.get('kakao_account')['email']
            kakao_id   = payload_json.get('id', None)

            if kakao_id == None:
                return JsonResponse({'message' : 'INVALID_KEY'}, status = 400)

            if not User.objects.filter(kakao_id = kakao_id).exists():
                User.objects.create(account = kakao_id, email = email, kakao_id = kakao_id)
            user         = User.objects.get(kakao_id = kakao_id)

            access_token = jwt.encode(
                        {'id':user.id}, local_settings.SECRET_KEY, algorithm = local_settings.ALGORITHM
                    ).decode('utf-8')
            return JsonResponse({'ACCESS_TOKEN': access_token}, status = 200)
        
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY'}, status = 400)

class CartView(View):
    @login_required
    def get(self, request):
        user     = request.user
        carts    = user.cart_set.prefetch_related('productseries', 'productseries__product'. 'productseries__product__discount').all()
        response = {
            'cart':[{
                'cart_id'             : cart.id,
                'product_image'       : cart.productseries.product.image,
                'product_name'        : cart.productseries.product.name,
                'product_series_name' : cart.productseries.name,
                'product_price'       : cart.productseries.product.price,
                'discount_price'      : cart.productseries.product.discount.percentage,
                'count'               : cart.count
            } for cart in carts]
        }

        return JsonResponse(response, status = 200)

    @login_required
    def post(self, request):
        data = json.loads(request.body)
        try:
            product_series_id    = data['product_series_id']
            product_count        = data['product_count']
            user                 = request.user

            if user.cart_set.filter(series = product_series_id).exists():
                cart = user.cart_set.get(series = product_series_id)
                cart.count += product_count
                cart.save()
            else:
                Cart.objects.create(
                    series = ProductSeries.objects.get(id = product_series_id),
                    user = user,
                    count = product_count
                )
            return JsonResponse({'message':'SUCCESS'}, status = 200)

        except ProductSeries.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)

    @login_required
    def put(self, request):
        data = json.loads(request.body)
        try:
            cart_id       = data['cart_id']
            product_count = data['product_count']

            cart = Cart.objects.get(id = cart_id)
            cart.count = product_count
            cart.save()

            return JsonResponse({'message':'SUCCESS'}, status = 200)

        except Cart.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)

    @login_required
    def delete(self, request):
        data = json.loads(request.body)
        try:
            cart_id = data['cart_id']

            Cart.objects.get(id = cart_id).delete()

            return JsonResponse({'message':'SUCCESS'}, status = 200)

        except Cart.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)