#!/bin/bash
PATH=$PATH:/etc/zabbix/externalscripts
export PATH
#shift
BASE_DIR="`dirname $0`"
/usr/bin/php $BASE_DIR/mikoomi-mongodb-plugin.php $* 
echo 0
