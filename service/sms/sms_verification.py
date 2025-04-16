from service.sms.make_code import  generate_verification_code
from service.sms.send_message import send_message

def sms_verification(phone_number : str):
    code = generate_verification_code()
    send_message(phone_number=phone_number, code = code)
