#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 29, 2013
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from dolphinopadmin.utils import response_json, md5
from dolphinopadmin.utils.errors import parameter_error
from dolphinopadmin.updateservice.models import XFFile
from dolphinopadmin.updateservice.form import ApkForm

logger = logging.getLogger("dolphinopadmin.admin")


@require_POST
@csrf_exempt
def file_upload(request):
    try:
        errors = []
        form = ApkForm(request.POST, request.FILES)
        if not form.is_valid():
            logger.warning(form.errors)
            return parameter_error(request, 'parameter')
        product = form.cleaned_data['product']
        hash_code = form.cleaned_data['hash_code']
        apk = form.cleaned_data['apk']
        apk_hash = md5(apk.read())
        logger.debug(hash_code)
        logger.debug(apk_hash)
        if apk_hash != hash_code:
            errors.append('hash is not the same, please retry!')
            result = {
                'errors': errors,
                'status': False,
            }
            return response_json(result)
        logger.debug(product)
        try:
            apk_obj = XFFile.objects.get(hash_code=hash_code, product=product)
            logger.debug(apk_obj)
        except Exception, e:
            logger.exception(e)
            apk_obj = XFFile()
        apk_obj.complete_file = apk
        apk_obj.save(request)
        storage = messages.get_messages(request)
        for message in storage:
            logger.debug(message)
            errors.append('%s' % message)
        if errors:
            result = {
                'errors': errors,
                'status': False,
            }
        else:
            result = {
                'status': True
            }
        return response_json(result)
    except Exception, e:
        logger.exception(e)
        return response_json({'status': False, 'errors': ['%s' % e]})
