# -*- coding: utf-8 -*-
import logging
from armory.marine.util import unixto_string

_LOGGER = logging.getLogger(__name__)

_EC2 = "ec2"
_LOCAL = "local"


def upload_status(item):
    item['first_created'] = unixto_string(item.get('first_created'))
    item['last_modified'] = unixto_string(item.get('last_modified'))
    server_names = [_LOCAL, _EC2]
    for server in server_names:
        last_release_server = "last_release_%s" % server
        if item.get(last_release_server):
            item[last_release_server] = unixto_string(
                item.get(last_release_server))
        else:
            item[last_release_server] = ''
    return item


def common_filter(model_dict):
    modeltitle = model_dict.get('title') or model_dict.get('name')
    if not modeltitle:
        modeltitle = 'no title or name field'
    new_dict = {
        'modelid': model_dict.get('id'),
        'modeltitle': modeltitle}
    return new_dict
