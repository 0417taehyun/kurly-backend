import re

from django.core.exceptions import ValidationError

from .models import User

def account_validate(input_account):
    if re.match('(?=.*[a-zA-Z])(?=.*[0-9]).{6,}|(?=.*[a-zA-Z]).{6,}$', input_account):
        return True
    return False

def account_overlap(input_account):
    if User.objects.filter(account = input_account).exists():
        return True
    return False

def password_validate(input_password):
    password_pattern = '^(?=.*[a-zA-Z])(?=.*[0-9]).[\S]{9,}|(?=.*[!@#$%^*+=-])(?=.*[0-9]).[\S]{9,}|(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-]).[\S]{9,}|(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).[\S]{9,}$'
    white_space = re.search(r'(\d)\1\1', input_password)
    if re.search(password_pattern, input_password) and not(white_space):
        return
    raise ValidationError('INVALID_PASSWORD_INPUT')

def email_validate(input_email):
    if re.match('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', input_email):
        return
    raise ValidationError('INVALID_EMAIL_INPUT')

def email_overlap(input_email):
    if User.objects.filter(email = input_email).exists():
        raise ValidationError('EXISTING_EMAIL')

def phone_number_validate(input_phone_number):
    phone_pattern = '^[0-9]*$'
    if re.search(phone_pattern, input_phone_number):
        return
    raise ValidationError('INVALID_PHONENUMBER_INPUT')

