import requests
import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.environ.get('OTP_AUTH')
class otpAuth:
    def __init__(self, phoneNum):
        self.phoneNum = phoneNum
        self.cookies = {}
        self.flag_allow_auth_name = ''
        self.finalResp = {}
    def getOtp(self):
        data = {
            'phone_country': '+91',
            'phone_no': self.phoneNum,
            'client_id': CLIENT_ID,
        }
        response = requests.post('https://auth.phone.email/submit-login', data=data)
        if response.json().get('flag') in [1,2]:
            self.cookies = response.cookies.get_dict()
            self.flag_allow_auth_name = response.json().get('flag_allow_auth_name')
            return {"success": True, "msg": "OTP Sent Successfully", "cookies": self.cookies, "flag_allow_auth_name": self.flag_allow_auth_name}
        else:
            print(response.json())
            return {"success": False, "msg": response.json().get('flag')}

    def verifyOtp(self, otp, data=None):
        if data is not None:
            self.cookies = data.get('cookies')
            self.flag_allow_auth_name = data.get('flag_allow_auth_name')
        if self.cookies == {}:
            return {"success": False, "msg": "OTP not sent"}
        data = {
            'otp': otp,
            'client_id': CLIENT_ID,
            'device': '',
            'business_name': '',
            'redirect_url': 'http://127.0.0.1:5000/',
            'fname': 'f',
            'lname': 'f',
            'ue': '0',
            'flag_allow_auth_name': self.flag_allow_auth_name,
        }
        response = requests.post('https://auth.phone.email/verify-login', cookies=self.cookies, data=data)
        respData = dict(response.json())
        if respData.get('flag') == 1:
            respData.update({"success": True})
            self.finalResp = respData
            return respData
        else:
            respData.update({"success": False})
            return respData

    def getPhoneNum(self):
        if self.finalResp == {}:
            return {"success": False, "msg": "OTP not verified"}
        response = requests.get('https://user.phone.email/user_' + self.finalResp.get('access_token') + '.json')
        return response.json().get('user_phone_number')