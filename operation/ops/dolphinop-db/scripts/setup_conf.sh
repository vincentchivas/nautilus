#! /bin/bash

if [ -f /etc/mongodb.conf ];then
    sudo mv /etc/mongodb.conf /etc/mongodb.conf.bak
fi
sudo cp -rf mongodb.conf /etc/
