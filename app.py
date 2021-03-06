import socket
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD
import syslog

REMOTE_SERVER_LIST = {"www.google.com", "www.bing.com", "www.amazon.com"}
RETRIES = 3 				# Number of re-tries before resetting the system
RETRY_DELAY = 60 		# Time in seconds to wait bewtween retries.

RELAY_PIN = 26

def is_connected():
		retFlag = True;
		# see if we can resolve the host name -- tells us if there is
		# a DNS listening
		for server in REMOTE_SERVER_LIST: 
			try:	
				host = socket.gethostbyname(server)
				# connect to the host -- tells us if the host is actually
				# reachable
				s = socket.create_connection((host, 80), 2)
			except:
				pass
				retFlag = False
				
		return retFlag


def initRelayBoard():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(RELAY_PIN, GPIO.OUT)
	GPIO.output(RELAY_PIN, GPIO.LOW)

def resetRelayBoard():
	initRelayBoard()

	syslog.syslog(syslog.LOG_INFO, "InternetCheckAndReset: Resetting Relay Board")
	# Reset
	GPIO.output(RELAY_PIN, GPIO.HIGH)
	# Wait
	time.sleep(10)
	# Turn it back on
	GPIO.output(RELAY_PIN, GPIO.LOW)

# Print local Ip address on LCD
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

if __name__ == "__main__":
		# Initialize the LCD using the pins
		lcd = LCD.Adafruit_CharLCDPlate()
		lcd.set_color(0.0, 1.0, 1.0)
		lcd.clear()
		
		lcd.message('Checking internet status')

		retVal = True;

		# Chek status of internet. If it returns false (no connection), try N times
		# more before taking corrective measure.
		if(is_connected() == False):
			lcd.message('\n Connection DOWN')
			for i in range(0,RETRIES-1):
				# Wait N seconds before trying again
				time.sleep(RETRY_DELAY)
				if(is_connected() == True):
					break # Break out of loop if connection is back up
				else:
					if(i == RETRIES-2): # Final retry
						lcd.clear()
						lcd.message('Resetting Relay')
						syslog.syslog(syslog.LOG_INFO, "InternetCheckAndReset: All retires failed")
						retVal = False
						resetRelayBoard()

		else:
			lcd.message('\n Connection up')

		lcd.clear()
		lcd.message(str(get_ip_address()) + '\n' + time.strftime("%H:%M:%S") + ' ' + str(retVal))
