import sys
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
from core.config import ADMIN_PHONE_NUMBER

##  @brief This sample code demonstrate how to send sms through CoolSMS Rest API PHP
if __name__ == "__main__":

    # set api key, api secret
    api_key = "API KEY"
    api_secret = "SECRET KEY"

    ## 4 params(to, from, type, text) are mandatory. must be filled
    params = dict()
    params['type'] = 'sms' # Message type ( sms, lms, mms, ata )
    params['to'] = '01063032285' # 받을 사람 번호
    params['from'] = ADMIN_PHONE_NUMBER # 보내는 사람 번호
    params['text'] = 'META LLM MSP 테스트' # 문자 내용

    cool = Message(api_key, api_secret)
    try:
        response = cool.send(params)
        print("Success Count : %s" % response['success_count'])
        print("Error Count : %s" % response['error_count'])
        print("Group ID : %s" % response['group_id'])

        if "error_list" in response:
            print("Error List : %s" % response['error_list'])

    except CoolsmsException as e:
        print("Error Code : %s" % e.code)
        print("Error Message : %s" % e.msg)

    sys.exit()