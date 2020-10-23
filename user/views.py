import json
import bcrypt
import jwt
import requests

from django.views           import View
from django.http            import JsonResponse
from django.core.exceptions import (
    ValidationError,
    ObjectDoesNotExist
)

from user.models  import (
    User, CartList
)
from products.models import Product, ProductSeries

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
        print(data)
        try:
            account = data['account']
            if account_validate(account):
                if account_overlap(account):
                    raise ValidationError('ACCOUNT_OVERLAPED')
            else:
                raise ValidationError('INVALID_ACCOUNT_INPUT')
                
            email        = data.get('email', None)
            
            if (email):
                password     = data['password']
                name         = data['name']
                phone_number = data['phone_number']
                address      = data['address']

                email_validate(email)
                email_overlap(email)
                password_validate(password)
                phone_number_validate(phone_number)
                password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                password = password.decode('utf-8')
                print(password)
                User(
                    account        = account,
                    password       = password,
                    name           = name,
                    email          = email,
                    phone_number   = phone_number,
                    address        = address,
                    gender         = data['gender'],
                    birth          = data['birth'],
                ).save()
                return JsonResponse({'message':'SIGNUP_SUCCESS'}, status = 200)

            return JsonResponse({'message':'ACCOUNT_SUCCESS'}, status = 200)

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

class GoogleSignInView(View):
    def get(self, request):
        GOOGLE_TOKEN_URL = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token="
        
        try:
            access_token      = request.headers.get('Authorization', None)

            if access_token == None:
                return JsonResponse({'message' : 'no_auth_token'}, status = 401)

            google_response   = requests.get(GOOGLE_TOKEN_URL + access_token)
            google_user       = google_response.json()
            google_email      = google_user['email']
            google_id         = google_user['id']

            if not User.objects.filter(google_id = google_id).exists():
                User.objects.create(account = google_email, email = google_email, google_id = google_id)
            user = User.objects.get(google_id = google_id)

            access_token = jwt.encode(
                        {'id':user.id}, local_settings.SECRET_KEY, algorithm = local_settings.ALGORITHM
                    ).decode('utf-8')
            return JsonResponse({'ACCESS_TOKEN': access_token}, status = 200)

        except KeyError:
            return JsonResponse({"message": "INVALID_GOOGLE_TOKEN"}, status = 401)

class CartView(View):
    @login_required
    def get(self, request):
        user     = request.user
        carts    = CartList.objects.filter(user_id = user.id).select_related('product', 'series').prefetch_related('product__discount').all()
        data_list = []

        for cart in carts:
            if cart.product.discount is None:
                if cart.series is None:
                    data =  {
                                'cart_id'             : cart.id,
                                'product_id'          : cart.product.id,
                                'product_image'       : cart.product.image,
                                'product_name'        : cart.product.name,
                                'product_series_name' : None,
                                'product_price'       : cart.product.price,
                                'discount_price'      : None,
                                'count'               : cart.count
                            }
                    data_list.append(data) 

                else:
                    data =  {
                                'cart_id'             : cart.id,
                                'product_id'          : cart.product.id,
                                'product_image'       : cart.product.image,
                                'product_name'        : cart.product.name,
                                'product_series_name' : cart.series.name,
                                'product_price'       : cart.series.price,
                                'discount_price'      : None,
                                'count'               : cart.count
                            }
                    data_list.append(data)
            else:
                if cart.series is None:
                    data =  {
                                'cart_id'             : cart.id,
                                'product_id'          : cart.product.id,
                                'product_image'       : cart.product.image,
                                'product_name'        : cart.product.name,
                                'product_series_name' : None,
                                'product_price'       : cart.product.price,
                                'discount_price'      : cart.product.price * (1 - cart.product.discount.percentage/100),
                                'count'               : cart.count
                            }
                    data_list.append(data)

                else:
                    data =  {
                                'cart_id'             : cart.id,
                                'product_id'          : cart.product.id,
                                'product_image'       : cart.product.image,
                                'product_name'        : cart.product.name,
                                'product_series_name' : cart.series.name,
                                'product_price'       : cart.series.price,
                                'discount_price'      : cart.product.price * (1 - cart.product.discount.percentage/100),
                                'count'               : cart.count
                            }
                    data_list.append(data)

        return JsonResponse({'cart' : data_list}, status = 200)
    
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.body)
            user              = request.user
            product_id        = data['product_id']
            product_series_id = data.get('product_series_id', None)
            product_count     = data['product_count'] 

            if not(Product.objects.filter(id = product_id).exists()):
                return JsonResponse({'message':'WRONG_PRODUCT_ID'}, status = 400)

            target_product = Product.objects.get(id = product_id)

            if product_series_id == None:
                if CartList.objects.filter(user_id = user.id, product_id = target_product).exists():
                    return JsonResponse({'message':'Product Already Exist!'}, status = 400)
                
                CartList(
                    user           = user,
                    product        = target_product,
                    count          = product_count
                ).save()
                return JsonResponse({'message':'New CartList Added'}, status = 201)

            target_series  = ProductSeries.objects.get(id = product_series_id)

            if CartList.objects.filter(user_id = user.id, product_id = target_product, series_id = product_series_id).exists():
                return JsonResponse({'message':'Product Already Exist!'}, status = 400)

            CartList(
                user           = user,
                product        = target_product,
                series         = target_series,
                count          = product_count
            ).save()

            return JsonResponse({'message':'New CartList Added'}, status = 201)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)

    @login_required
    def put(self, request):
        data = json.loads(request.body)
        try:
            cart_id       = data['cart_id']
            product_count = data['product_count']

            cart = CartList.objects.get(id = cart_id)
            cart.count = product_count
            cart.save()

            return JsonResponse({'message':'UPDATE SUCCESS'}, status = 200)

        except CartList.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)

    @login_required
    def delete(self, request):
        data = json.loads(request.body)
        try:
            cart_id = data['cart_id']

            CartList.objects.get(id = cart_id).delete()

            return JsonResponse({'message':'DELETE SUCCESS'}, status = 200)

        except CartList.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 400)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)