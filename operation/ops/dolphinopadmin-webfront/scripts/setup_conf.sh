#!/bin/bash
#
# This scripts is used to setup the configuration for the application.
#
#
# Author : chzhong 
#

CONFIG_FILE=dolphin-operation-admin.nginx
ENABLE_CONFIG=/etc/nginx/sites-enabled

cp -lf ${CONFIG_FILE} ${ENABLE_CONFIG}/dolphin-operation-admin

if [ -f "${ENABLE_CONFIG}/default" ] ; then
    rm "${ENABLE_CONFIG}/default"
fi

