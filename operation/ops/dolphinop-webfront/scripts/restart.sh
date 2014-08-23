#!/bin/bash
#
# This scripts is used to restart the application.
# This scripts is required for all projects.
#
#
# Author : chzhong 
#

if [ -f "/var/run/nginx.pid" ]; then
    # remove nginx  cache
    sudo rm -fr /var/lib/nginx/cache
	sudo service nginx reload
else
    # remove nginx  cache
    sudo rm -fr /var/lib/nginx/cache
	sudo service nginx start
fi

