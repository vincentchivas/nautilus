# -*- coding: utf-8 -*-

import sys
import qrcode
from urllib import quote

url = "http://www.baidu.com"


def make_qr(url, path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # url = quote(url)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(path)


if __name__ == "__main__":
    make_qr(url)

##需要安装qrcode和PIL，安装方法：
##easy_install qrcode
##easy_install PIL
