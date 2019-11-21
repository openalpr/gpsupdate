#!/usr/bin/python3
import serial 
import time
import pynmea2
import requests
import logging
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('OpenALPR GPS Log')

gps_latitude = None
gps_longitude = None

def get_gps_data(device_handle):
    global gps_latitude, gps_longitude


    ser = serial.Serial(device_handle, baudrate=4800, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) 

    ser.flushInput()
    ser.flushOutput()
    bytebuffer = ''
    line = []

    while True:

        rcv = ser.read()
        try:
            line.append(rcv.decode('utf-8'))
        except:
            time.sleep(0.15)
            continue

        if rcv == b'\n':
            #print("Got one")
            line = "".join(line)
            try:
                gps_msg = pynmea2.parse(line.strip())
    #            gps_msg = pynmea2.parse('$GPGGA,204551.000,4106.4792,N,07348.4209,W,1,05,2.7,92.4,M,-34.2,M,,0000*52')

                if gps_msg.latitude and gps_msg.longitude:
                    if gps_msg.latitude != 0 and gps_msg.longitude != 0:
                        gps_latitude = gps_msg.latitude
                        gps_longitude = gps_msg.longitude
                        return
            #            print(gps_msg.latitude)
            #            print(gps_msg.longitude)

            except KeyboardInterrupt:
                raise
            except:
                pass
#                logger.exception("Failed to get GPS data")
            line = []

def post_gps_data():

    try:
        response = requests.get('http://127.0.0.1:8355/gps/set',
                                 params={'latitude': gps_latitude,
                                        'longitude': gps_longitude},)

        if response.status_code != 200:
            logger.info(f"Failed to update local webservice.  Response: {response.status_code}")
        else:
            print(f"updated GPS coordinates to {gps_latitude} {gps_longitude}")

    except KeyboardInterrupt:
        raise
    except:
        logger.exception("Failed to send GPS data to webservice")

if __name__ == "__main__":

    parser = ArgumentParser(description='OpenALPR GPS Update Daemon')


    parser.add_argument('-f', '--foreground', action='store_true', default=False,
                        help="Run the daemon program in the foreground.  Default=false")

    parser.add_argument('-l', '--log', action='store', default='/var/log/openalpr_gps.log',
                        help="log file for daemon process")

    parser.add_argument('-d', '--device', action='store', default='/dev/ttyUSB0:',
                        help="TTY device")

    options = parser.parse_args()


    logger.setLevel(logging.DEBUG)

    if options.foreground:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    else:
        # Setup the logging

        # add a rotating file handler
        handler = RotatingFileHandler(options.log, maxBytes=20 * 1024 * 1024,
                                      backupCount=3)

        fmt = logging.Formatter("%(asctime)-15s %(thread)d: %(message)s", datefmt='%Y-%m-%dT%H:%M:%S')
        handler.setFormatter(fmt)

        logger.addHandler(handler)


    logger.info("Script initialized")



    while True:
        try:
            get_gps_data(options.device)
            post_gps_data()


            time.sleep(1.0)

        except KeyboardInterrupt:
            raise
        except:
            time.sleep(1.0)
            #logger.exception("Error in get/post loop")


    logger.info("Script complete.  Shutting down")

