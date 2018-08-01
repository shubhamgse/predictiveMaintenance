import time
import datetime
import math
import subprocess
import RPi.GPIO as GPIO

#from Hologram.HologramCloud import HologramCloud

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
DEBUG = 1   # When DEBUG = 1, Modem connection is NOT used, only console output

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
  if ((adcnum > 7) or (adcnum < 0)):
    return -1
  GPIO.output(cspin, True)

  GPIO.output(clockpin, False)  # start clock low
  GPIO.output(cspin, False)     # bring CS low

  commandout = adcnum
  commandout |= 0x18  # start bit + single-ended bit
  commandout <<= 3    # we only need to send 5 bits here
  for i in range(5):
    if (commandout & 0x80):
      GPIO.output(mosipin, True)
    else:
      GPIO.output(mosipin, False)
    commandout <<= 1
    GPIO.output(clockpin, True)
    GPIO.output(clockpin, False)

  adcout = 0
  # read in one empty bit, one null bit and 10 ADC bits
  for i in range(12):
    GPIO.output(clockpin, True)
    GPIO.output(clockpin, False)
    adcout <<= 1
    if (GPIO.input(misopin)):
      adcout |= 0x1

  GPIO.output(cspin, True)
        
  adcout >>= 1       # first bit is 'null' so drop it
  return adcout

if not DEBUG:
  command = "lsusb | grep \"1546:1102 U-Blox AG\""
  try:
    proc = subprocess.check_output(command, shell=True)
  except:
    raise SystemExit("Modem NOT detected.")

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK  = 18
SPIMISO = 23
SPIMOSI = 24
SPICS   = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK,  GPIO.OUT)
GPIO.setup(SPICS,   GPIO.OUT)

ADC_CH = 0

def readCTSensor(ADC_CH):
  vRMS       = 120.0  # Assumed or measured
  offset     = 1.65   # Half the ADC max voltage
  numTurns   = 2000   # 1:2000 transformer turns
  rBurden    = 33   # Burden resistor value
  numSamples = 1000   # Number of samples before calculating RMS

#  if DEBUG:
#    print "\nCT Sensor number of turns:", numTurns
#    print "Actual burden resistor:", rBurden, "ohm"
#    print "Number of samples:", numSamples
#    print "AC (RMS Voltage):", vRMS, "V"

  voltage       = 0.0
  iPrimary      = 0.0
  acc           = 0.0
  apparentPower = 0.0
  stoveStatus   = "OFF"

  # Take a number of samples and calculate RMS current
  for i in range(0, numSamples):
    # Read ADC, convert to voltage, remove offset
    sample = readadc(ADC_CH, SPICLK, SPIMOSI, SPIMISO, SPICS)
    voltage = (sample * offset * 2) / 1024
    voltage = voltage - offset

    iPrimary = (voltage / rBurden) * numTurns

    acc += pow(iPrimary, 2)
    time.sleep(0.001)

  iRMS = math.sqrt(acc / numSamples)  # Calculate RMS from accumulated values
  apparentPower = vRMS * iRMS         # Calculate apparent power

  if ( apparentPower >= 1.5 ):
    stoveStatus = "ON"
  else:
    stoveStatus = "OFF"
    

  if DEBUG:
    print ("Current sensor -", \
          "%.2fA," % iRMS, \
           "Power -", \
          "%.2fW," % apparentPower, \
           )

    return iRMS, apparentPower



ADC_CH = 0

while True:
    xx = readCTSensor(ADC_CH)
    #print(xx)
