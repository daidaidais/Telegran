# coding: utf-8

import cv2 
import RPi.GPIO as GPIO
import time
import picamera
import os
import pyaudio
import sys
import wave

img = cv2.imread('test.jpg')

cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
cv2.imshow('image', img)

cv2.waitKey(800)

chunk = 24000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

p = pyaudio.PyAudio()
frames = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def callback(in_data, frame_count, time_info, status):
        frames.append(in_data)
        return(None, pyaudio.paContinue)


def playFunction(channel):
	time.sleep(1)
        print("Button 16 Pressed!")
        os.system("sudo sh play_video.sh")
	time.sleep(1)

#def quitFunction(channel):
#	print("Button 19 Pressed!")
#	GPIO.cleanup()
#	cv2.destroyAllWindows()

def startRecFunction(channel):
	 with picamera.PiCamera() as camera:
                time.sleep(1)
                print("Button 17 Pressed!")
                camera.resolution = (800, 480)
                camera.start_preview()
		
		stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=0,
                        frames_per_buffer=chunk,
                        stream_callback=callback
                        )


	        print("recording...")
       		#stream.start_stream()
	
		timestr = time.strftime("%Y%m%d%H%M%S")
	
		camera.start_recording('message_out/' + timestr + '.h264')
		stream.start_stream()

                print("recording started")
                #camera.start_recording('video.h264', 'h264', intra_period = 60)
                time.sleep(2) #initializing camera?
		GPIO.wait_for_edge(18, GPIO.FALLING)
		print("Button 18 Pressed, recording stopped")
		camera.stop_recording()
		
		stream.close()

        	waveFile = wave.open('message_out/' + timestr + ".wav", 'wb')
        	waveFile.setnchannels(CHANNELS)
        	waveFile.setsampwidth(p.get_sample_size(FORMAT))
        	waveFile.setframerate(RATE)
        	waveFile.writeframes(b''.join(frames))
        	waveFile.close
        	#p.terminate()
        	print("save...DONE")

		camera.stop_preview()

def stopRecFunction(channel):
	with picamera.PiCamera() as camera:
		print("Button 18 Pressed!")
		print("recording stopped")
		camera.stop_recording()
		camera.stop_preview()

GPIO.add_event_detect(16, GPIO.FALLING, callback=playFunction, bouncetime=300)
#GPIO.add_event_detect(19, GPIO.FALLING, callback=quitFunction, bouncetime=300) 
GPIO.add_event_detect(17, GPIO.FALLING, callback=startRecFunction, bouncetime=300)
#GPIO.add_event_detect(18, GPIO.FALLING, callback=stopRecFunction, bouncetime=300)

while True:
	k = cv2.waitKey(0)
	if k == 27:
		break

p.terminate()
GPIO.cleanup()
cv2.destroyAllWindows()
