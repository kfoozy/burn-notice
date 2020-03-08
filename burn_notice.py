# The user will probably call this program somehow
# and it should take the spf they are wearing, and the 
# UV returned by the sensor, and return the time they 
# reapply sunscreen

## UV information source: https://www.researchgate.net/profile/Thomas_Frei3/publication/288523666_UV-Index_for_the_Public/links/569d4f9908ae16fdf0796d77/UV-Index-for-the-Public.pdf
import serial
import numpy as np
from time import sleep,time
from crontab import CronTab
from twilio.rest import Client
import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import sys
import argparse

#port = "/dev/ttyACM0"
#ser = serial.Serial(port,2400,timeout = 0.050)
#ser.baudrate=9600

# p.timestep is also number of minutes to wait/sleep

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

app= Flask(__name__)
app.config.from_object(__name__)

callers = {
    "+14039701456": "Suliat"
}

body = ''

@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():

    resp = MessagingResponse()
    resp.message("Time to reapply sunscreen? Is this executing?")
    return str(resp)

UV_INDEX = { 0: 800000,
             1: 60,
             2: 60,
             3: 60,
             4: 30, 
             5: 30,
             6: 30,
             7: 20,
             8: 20,
             9: 15}

class UVLevel(object):
    def __init__(self):
        self._uv_level = 0
        self._observers = []

    @property
    def uv_level(self):
        return self._uv_level

    @uv_level.setter
    def uv_level(self, value):
        self._uv_level = UV_INDEX[value]
        for callback in self._observers:
            callback(self._uv_level)

    def bind_to(self, callback):
        self._observers.append(callback)

class ProtectionLevel(object):
    def __init__(self, data, user_spf, timestep):
        self.protection_level = 100
        self.user_spf = user_spf
        self.timestep = timestep
        self.data = data
        self.data.bind_to(self.update_protection_level)

    def _new_protection_level(self, spf, uv, prot_old):
            prot_new = prot_old - self.timestep* (100/(uv*spf))
            return prot_new

    def update_protection_level(self, uv_level):
            new_prot = self._new_protection_level(self.user_spf, uv_level, self.protection_level)
            self.protection_level =  new_prot


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("spf")
    parser.add_argument("timestep")
    args = parser.parse_args()
    
    data = UVLevel()
    p = ProtectionLevel(data, args.spf, args.timestep) # data, spf, timestep
    i = 0
    while(i <2):
        sleep(10)
        i= i+1
    
    message = client.messages.create(
        body = 'Time to reapply sunscreen!',
        from_ ='+12056515230',
        to='+14039701456'
    )
    print(message.sid)
            
    #    while (1==1):
    #        raw = ser.readline() # looks like b'0\r\n'
    #        string_n = raw.decode()
    #        string = string_n.rstrip()
    #        # if needed convert to float with flt = float(string) but check to make sure it's not nothing
    #        if (string != ''):
    #            integer = int(string)
    #            data.uv_level = integer # 
    #            print(p.protection_level) 
    #
    #        sleep(p.timestep)  # sleeps for number of minutes
        

