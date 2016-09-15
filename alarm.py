#import the GPIO and time package
import RPi.GPIO as GPIO
import time
import subprocess
import threading, Queue

#ftp
import ftplib
import os
#import traceback

GPIO.setwarnings(False)
GPIO.cleanup()

#GPIO ports (Physical Ports)
sensor = 4
led_green = 17
led_red = 27
speaker = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)
GPIO.setup(speaker, GPIO.OUT)

previous_state = False
current_state = False

#Default values
GPIO.output(led_green,True)
GPIO.output(led_red,False)
GPIO.output(speaker,False)

#Function: buzz(pitch, duration)
#Author: LearningEmbedded.com
def buzz(pitch, duration):   #create the function "buzz" and feed it the pitch and duration)
    period = 1.0 / pitch     #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delay = period / 2     #calcuate the time for half of the wave
    cycles = int(duration * pitch)   #the number of waves to produce is the duration times the frequency
 
    for i in range(cycles):    #start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(speaker, True)   #set pin 18 to high
        time.sleep(delay)    #wait with pin 18 high
        GPIO.output(speaker, False)    #set pin 18 to low
        time.sleep(delay)    #wait with pin 18 low

def webcam(q,cam):
    #call webcam shell script
    if cam == 1:
    	result = subprocess.check_output(['/home/pi/projetos/led_speaker_sensor/webcam_script.sh'], shell=True)
    else:
        result = subprocess.check_output(['/home/pi/projetos/led_speaker_sensor/webcam_script2.sh'], shell=True)
    
    q.put(result)

def ftp(f):
    try:      

        ftp = ftplib.FTP()
        host = "ftp.1socorros.com.br"
        port = 21
        ftp.connect(host, port)
    
        pathLocal = "/home/pi/projetos/webcam/"
        pathFTP = "/public_html/1socorros.com.br/imgRB"

        ftp.login("username", "password")
        file = open(pathLocal + f, "r")
        ftp.cwd(pathFTP)
        ftp.storbinary('STOR ' + f, file)
        file.close()
    finally:
        ftp.quit()
        
        #removing temporary photo (optional)
        if os.path.exists(pathLocal + f):
            os.remove(pathLocal + f)

while True:
    previous_state = current_state
    current_state = GPIO.input(sensor)
    if current_state != previous_state:
        new_state = "HIGH" if current_state else "LOW"
        #print("GPIO pin %s is %s" % (sensor, new_state))
        if new_state == "HIGH":
            print(time.strftime("%d/%m/%y - %H:%M:%S") + " > INTRUSO DETECTADO!!!")
            
            q = Queue.Queue()
            q1 = Queue.Queue()
            try:
                #start new thread for webcam1 (usb)
                t1 = threading.Thread(target=webcam, args=(q,1,))
                t1.start()
              
                #start new thread for webcam2 (usb)
                t1a = threading.Thread(target=webcam, args=(q1,2,))            
                t1a.start()

                #start new thread for speaker
                t2 = threading.Thread(target=buzz, args=(200,1))
                t2.start()
            except:
                print "Error: Unable to start thread"
            GPIO.output(led_green,False) #turn off green led
            GPIO.output(led_red,True) #turn on red led
           
            #wait for stop processes
            #t2.join()
            #t1.join()
            
            #start new thread for ftp
            t3 = threading.Thread(target=ftp, args=(q.get(),))
            t3.start()
            t4 = threading.Thread(target=ftp, args=(q1.get(),))
            t4.start()

            #print q.get()
            #ftp(q.get())
        else:
            print(time.strftime("%d/%m/%y - %H:%M:%S") + " > IDLE. :)")
            GPIO.output(led_red,False)
            GPIO.output(led_green,True)
            GPIO.output(speaker,False)
