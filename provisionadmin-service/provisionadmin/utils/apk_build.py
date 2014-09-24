# -*- coding: utf-8 -*-
"""
@author: zhhfang
@date: 2014-07-15
@description: put apk unbuild. build and sign actions here
"""

import os
import time
import logging
import subprocess
from django.conf import settings
from provisionadmin.utils.qrcode_generator import make_qr
from provisionadmin.utils import exception

STATIC_ROOT = settings.STATIC_ROOT
HOST = settings.HOST
_LOGGER = logging.getLogger("apk")


def build_apk(appname, appversion, snap_id):
    """
    put apk unbuild. build and sign actions here
    Parameters:
        -None
    Return:
        -full_ret_url: the download link of apk file
        -full_ret_img_url: the download link of QRcode file
    """
    if not snap_id:
        raise exception.DataError("snap_id %s is not valid", snap_id)
    appdir = os.path.join(STATIC_ROOT, appname, appversion)
    apkfiledir = os.path.join(appdir, 'apk_data')
    new_apkfilepath = os.path.join(appdir, "apk_%s.apk" % snap_id)
    _LOGGER.info(
        "build apk data from %s to apk file %s", apkfiledir, new_apkfilepath)
    subprocess.call(
        "apktool b %s %s" % (apkfiledir, new_apkfilepath), shell=True)
    apk_url_filepath = "/tmp/apk_url_%s.txt" % snap_id
    _LOGGER.info(
        "re-assign the apkfile %s, save url to file %s",
        new_apkfilepath, apk_url_filepath)
    subprocess.call(
        "curl -F \"apkfile=@%s\" "
        "http://172.16.7.25:1234/handle_sign_redirect "
        "-o %s" % (new_apkfilepath, apk_url_filepath), shell=True)
    new_apkfilepath_withsign = os.path.join(
        appdir, "apk_%s_withsign.apk" % snap_id)
    time.sleep(2)
    _LOGGER.info(
        "fetch the re-assigned apk file and save to %s",
        new_apkfilepath_withsign)
    subprocess.call(
        "curl -o %s " % new_apkfilepath_withsign +
        "`awk '{printf \"http://172.16.7.25:1234%s\", $1}' " +
        "%s`" % apk_url_filepath, shell=True)
    ret_url = "/admin/download?type=apk&file=%s&appname=%s&appversion=%s" % \
        (os.path.basename(new_apkfilepath_withsign), appname, appversion)
    _LOGGER.info("generate apk url %s", ret_url)
    qrcode_pic_filename = "qrcode_pic_%s.jpg" % snap_id
    ret_img_path = os.path.join(appdir, qrcode_pic_filename)
    full_ret_img_url = \
        "http://%s/admin/download?type=qrcode&file=%s&appname=%s"\
        "&appversion=%s" % (HOST, qrcode_pic_filename, appname, appversion)
    full_ret_url = "http://%s%s" % (HOST, ret_url)
    _LOGGER.info(
        "use full_ret_url %s to generate a qrcode %s, and the ret_img_url %s",
        full_ret_url, ret_img_path, full_ret_img_url)
    make_qr(full_ret_url, ret_img_path)
    return full_ret_url, full_ret_img_url
