#!/usr/bin/python3
import serial 
import time
import pynmea2
import requests
import logging
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler
import asyncio

logger = logging.getLogger('OpenALPR GPS Log')

def post_gps_data(gps_latitude, gps_longitude):

    try:
        response = requests.get('http://127.0.0.1:8355/gps/set',
                                 params={'latitude': gps_latitude,
                                        'longitude': gps_longitude}
                                )

        if response.status_code != 200:
            logger.info(f"Failed to update local webservice.  Response: {response.status_code}")
        else:
            print(f"updated GPS coordinates to {gps_latitude} {gps_longitude}")

    except KeyboardInterrupt:
        raise
    except:
#        logger.exception("Failed to send GPS data to webservice")
        pass



class GPSServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        # print('Received %r from %s' % (message, addr))

        try:

            lines = message.splitlines()
            for line in lines:
                if line.upper().startswith("$GPGGA"):
                    gps_msg = pynmea2.parse(line.strip())

                    if gps_msg.latitude and gps_msg.longitude:
                        if gps_msg.latitude != 0 and gps_msg.longitude != 0:
                            gps_latitude = gps_msg.latitude
                            gps_longitude = gps_msg.longitude
                            post_gps_data(gps_latitude, gps_longitude)
                            #return
                            # print(gps_msg.latitude)
                            # print(gps_msg.longitude)
        except:
            logger.exception("Failed to send GPS data to webservice")




if __name__ == "__main__":

    parser = ArgumentParser(description='OpenALPR GPS Update Daemon')


    parser.add_argument('-f', '--foreground', action='store_true', default=False,
                        help="Run the daemon program in the foreground.  Default=false")

    parser.add_argument('-l', '--log', action='store', default='/var/log/openalpr_gps.log',
                        help="log file for daemon process")

    parser.add_argument('-p', '--port', action='store', default='22338',
                        help="UDP Port to listen on")

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


    loop = asyncio.get_event_loop()
    print("Starting UDP server")

    # One protocol instance will be created to serve all client requests
    listen = loop.create_datagram_endpoint(
        GPSServerProtocol, local_addr=('0.0.0.0', int(options.port)))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()



    logger.info("Script complete.  Shutting down")

