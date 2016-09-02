import RPi.GPIO as GPIO
import time
import message
import json
from datetime import datetime

with open('scripts/data.json','r') as f:
    data = json.load(f)

GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
MOTOR = 18

max_ht = 18
min_ht = 3
lit = 0
dur = 0.0083  #Give it in hours


message_sent = 0
last_sent = 0


print("Distance Measurement in Progress")

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(MOTOR,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)


GPIO.output(TRIG,False)
print ("Waiting for sensor to settle")
time.sleep(2)
GPIO.output(MOTOR,False)
try:
    while True:
        with open('scripts/data.json','r') as f:
            data = json.load(f)
        id = data["last_id"]
        last = datetime.strptime(data['last'],'%Y-%m-%d %H:%M:%S.%f')
        print (datetime.today()-last).days
        if ((datetime.today()-last).days != 0):
            print ("inside if")
            id = str(time.strftime("%d/%m/%Y"))
            data.update({'last_id':id})
            data['details'].update({id:{'used':0}})
            data.update({'last':str(datetime.today())})
        prev_lvl = data["level"]
        GPIO.output(TRIG,True)
        time.sleep(0.00001)
        GPIO.output(TRIG,False)

        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration*17150
        distance = round(distance,2)
        cur_lvl = distance
        if(cur_lvl>prev_lvl):
            data["content_used"] = data["content_used"]+(cur_lvl-prev_lvl)*3.14*4*4/1000
            data["details"][id]["used"]=data["details"][id]["used"]+(cur_lvl-prev_lvl)*3.14*4*4/1000
            #print data["details"][id]["used"]
        print ("Distance: ",distance," cm")
        if(time.time()-last_sent >= dur*60*60):
            message_sent = 0
        if(max_ht-distance <= min_ht):
            GPIO.output(MOTOR,True)
            if message_sent == 0:
                print("Message sent")     
                message_sent = 1
                last_sent = time.time()
                #print time.time()
                #message.sendMessage(max_ht-distance)
                #time.sleep(dur)
        else:
            GPIO.output(MOTOR,False)
        data.update({"level":distance})
        with open('scripts/data.json','w') as f:
            data = json.dump(data,f)
except KeyboardInterrupt:
    print ("End")
print ("End")
GPIO.cleanup()
