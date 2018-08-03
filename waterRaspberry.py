import RPi.GPIO as GPIO
import time, sys

GPIO.setmode(GPIO.BOARD)
inpt = 13
GPIO.setup(inpt,GPIO.IN)


def init():
	storage_val = calcWaterForHour()






print('water-flow approximate')

def calcWaterForHour():

	rate_cnt = 0
	tot_cnt = 0
	minutes = 0
	constant = 0.10
	time_new = 0.0
	stop_time = 0.0
	gpio_last = 2

	timeout = time.time() + 60*1 #timer for 1 minute break

	while True:
		for sec_mult in range(0,1):
			time_new = time.time() + 1
			rate_cnt = 0
			while time.time() <= time_new:
				gpio_cur = GPIO.input(inpt)
				if gpio_cur != gpio_last:
					rate_cnt += 1
					tot_cnt += 1
				else:
					rate_cnt = rate_cnt
					tot_cnt = tot_cnt
				
				try:
					None
				except KeyboardInterrupt:
					print('\nCTRL C - Exiting')
					
					GPIO.cleanup()
					print('done')
					sys.exit()
					
				gpio_last = gpio_cur
		
		minutes += 1

		flow = round(rate_cnt * constant / 60,4)
		
		print('\nLiters / sec', flow , 'approximate')

		'''for i in range(1,60):
	                total += flow '''

	    final_val = round(tot_cnt * constant / 60,4)
		print('Total Liters', final_val)
		print('Time (min&clock)',minutes, '\t',
			time.asctime(time.localtime(time.time())),'\n')

		if time.time > timeout:		#check if it is time to store
			break

		return final_val
			
			
			
