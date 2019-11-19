openalpr-gpsupdate
============================

This Python daemon pulls GPS coordinates from a USB or serial GPS device and POSTs it to the OpenALPR agent.  Using this will allow you to automatically update 
the GPS coordinates of a moving OpenALPR agent system running on Linux.

Install Notes
---------------

    sudo apt-get update
    sudo dpkg -i openalpr-gpsupdate_1.0.1-20191117104820.deb
    sudo apt-get install -f -y

After installing the software, configure OpenALPR daemon as follows.

Add the following to /etc/openalpr/alprd.conf

    web_server_enabled = 1
    gps_use_webservice = 1


Restart OpenALPR services

    sudo service openalpr-link restart

The TTYUSB device can be set in /etc/init.d/openalpr-gpsupdate

