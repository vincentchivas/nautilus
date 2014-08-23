#!/bin/bash
#
# This scripts is used to stop the application.
#
#
# Author : chzhong 
#

sudo service nginx stop
# remove nginx  cache
sudo rm -fr /var/lib/nginx/cache
