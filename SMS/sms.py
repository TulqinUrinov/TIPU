import hashlib
import os
from random import randint
import time

import requests
from requests import post
from icecream import ic
# from dotenv import load_dotenv
#
# # .env faylni yuklab olamiz
# load_dotenv()


class SayqalSms:
    def __init__(self):
        self.username = os.environ.get("SAYQAL_USERNAME")
        self.token = os.environ.get("SAYQAL_TOKEN")

        assert (
                self.username is not None
        ), "Environment variable SAYQAL_USERNAME is not set"

        assert self.token is not None, "Environment variable SAYQAL_TOKEN is not set"

        self.url = "https://routee.sayqal.uz/sms/"

    def generateToken(self, method: str, utime: int):
        access = f"{method} {self.username} {self.token} {utime}"
        token = hashlib.md5(access.encode()).hexdigest()
        return token

    def fixNumber(self, number: str):
        # Telefon raqamini to'g'ri formatga keltirish
        if number.startswith("+"):
            return number[1:]
        return number

    def send_sms(self, number: str, message: str):
        utime = int(time.time())
        token = self.generateToken("TransmitSMS", utime)

        number = self.fixNumber(number)
        url = self.url + "TransmitSMS"

        data = {
            "utime": utime,
            "username": self.username,
            "service": {"service": 1},
            "message": {
                "smsid": randint(111111, 999999),
                "phone": number,
                "text": message,
            },
        }

        response = post(url, json=data, headers={"X-Access-Token": token})
        ic("Sms response", data, response.text)

        return response


if __name__ == "__main__":
    sms = SayqalSms()
    response = sms.send_sms("+998935096115", message="Salom bu test")

    print(response)
