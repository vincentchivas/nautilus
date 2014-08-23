#!/bin/bash
#
# This scripts is used to setup the configuration for the application.
#
#
# Author : chzhong 
#

CONFIG_FILE=dolphin-operation.nginx
HOME_FILE=home.nginx
GLOBAL_FILE=nginx.conf
BASE_CONFIG=/etc/nginx/
ENABLE_CONFIG=/etc/nginx/sites-enabled

cp -lf ${CONFIG_FILE} ${ENABLE_CONFIG}/dolphin-operation
cp -lf ${HOME_FILE} ${ENABLE_CONFIG}/home

if [ -f "${GLOBAL_FILE}" ] ; then
    cp -f ${GLOBAL_FILE} ${BASE_CONFIG}/
fi

if [ -f "${ENABLE_CONFIG}/default" ] ; then
    rm "${ENABLE_CONFIG}/default"
fi

