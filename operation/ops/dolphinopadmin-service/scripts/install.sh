#!/bin/bash
#
# This scripts is used to install the application.
# This scripts is required for all projects.
#
#
# Author : kunli
#

python setup.py -q build

SCRIPT_DIR=`dirname $0`
PROJECT=dolphinopadmin-service

if [ "$1" = "checkdeps" ] ; then

    if [ -f "${SCRIPT_DIR}/install_deps.sh" ]; then
        ${SCRIPT_DIR}/install_deps.sh
    fi
fi 

if [ -f "${SCRIPT_DIR}/setup_conf.sh" ]; then
    ${SCRIPT_DIR}/setup_conf.sh
fi

python setup.py -q build

PTH_FILE='dolphinopadmin.pth'
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    pwd > ${PTH_FILE}
    sudo python scripts/install.py
fi

echo Installing service...
test -z `grep "^dolphinopadmin:" /etc/passwd`  && sudo useradd -r dolphinopadmin -M -N

# make media dir for the storage for the files
# by liu cong
if [ -d "/var/app/enabled/$PROJECT/media" ] ; then
    chmod -R a+rw /var/app/enabled/$PROJECT/media
    chown dolphinopadmin:nogroup /var/app/enabled/$PROJECT/media
else
    mkdir -p /var/app/enabled/$PROJECT/media 
    chmod -R a+rw /var/app/enabled/$PROJECT/media
    chown dolphinopadmin:nogroup /var/app/enabled/$PROJECT/media
fi
###

#chmod -R a+rw /var/app/data/$PROJECT
chmod -R a+rw /var/app/log/$PROJECT
chown dolphinopadmin:nogroup /var/app/data/$PROJECT
chown dolphinopadmin:nogroup /var/app/log/$PROJECT

ln -sf /var/app/enabled/$PROJECT/scripts/$PROJECT-init.sh /etc/init.d/$PROJECT
update-rc.d $PROJECT defaults

