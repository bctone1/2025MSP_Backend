from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
from core.config import COOL_SMS_API, COOL_SMS_SECRET
from core.config import ADMIN_PHONE_NUMBER

def send_message(phone_number : str, code : str):
    api_key = COOL_SMS_API
    api_secret = COOL_SMS_SECRET

    params = dict()
    params['type'] = 'sms' # Message type ( sms, lms, mms, ata )
    params['to'] = phone_number # 받을 사람 번호
    params['from'] = ADMIN_PHONE_NUMBER # 보내는 사람 번호
    params['text'] = f'[META LLM MSP] 인증번호 {code}' # 문자 내용

    cool = Message(api_key, api_secret)
    try:
        cool.send(params)

    except CoolsmsException as e:
        print("Error Code : %s" % e.code)
        print("Error Message : %s" % e.msg)
        return "fail"

