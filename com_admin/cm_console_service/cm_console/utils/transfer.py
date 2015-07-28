# -*- coding: utf-8 -*-
import os
import errno
import shutil
import subprocess
import logging
import urllib

from cm_console.settings import (
    MEDIA_ROOT, REMOTEDB_SETTINGS, S3_DOMAIN, LOCAL_STATIC_RESOURCE, KEY_FILE)

_LOGGER = logging.getLogger(__name__)


def check_name(name):
    encode_name = name.encode('utf-8')
    if len(encode_name) != len(name):
        _LOGGER.warning("The name of %s contains invalid characters.", name)
        return False
    new_name = urllib.quote(name)
    if len(new_name) != len(name):
        _LOGGER.warning("The name of %s contains invalid characters.", name)
        return False
    else:
        return True


def save_file(fileobj, base_dir, short_path):
    file_content = os.path.join(MEDIA_ROOT, base_dir)
    if not os.path.exists(file_content):
        os.makedirs(file_content)
    file_path = os.path.join(MEDIA_ROOT, short_path)
    fileobj.save(file_path)
    return file_content, file_path


def sdel(hosts, user, key_file, remote):
    servers = ['%s@%s' % (user, ip) for ip in hosts]
    for server in servers:
        sdel_file = 'ssh -oConnectTimeout=120 -oStrictHostKeyChecking=no \
                -i %s %s "rm %s"' % (key_file, server, remote)
        _LOGGER.debug(sdel_file)
        try:
            result = subprocess.call(sdel_file, shell=True)
            if result != 0:
                _LOGGER.error(result)
            _LOGGER.info(result)
        except Exception, e:
            _LOGGER.exception(e)
            return False
    return True


def scp(hosts, user, key_file, local, remote):
    remote_dir = os.path.dirname(remote)
    servers = ['%s@%s' % (user, ip) for ip in hosts]
    for server in servers:
        mkdir = 'ssh -oConnectTimeout=120 -oStrictHostKeyChecking=no \
                -i %s %s "mkdir -p %s"' % (key_file, server, remote_dir)
        scp_file = 'scp -oConnectTimeout=120 -oStrictHostKeyChecking=no \
                -i %s %s %s:%s' % (key_file, local, server, remote)
        _LOGGER.debug(scp_file)
        try:
            result = subprocess.call(scp_file, shell=True)
            if result != 0:
                dir_result = subprocess.call(mkdir, shell=True)
                if dir_result != 0:
                    _LOGGER.error(dir_result)
                    return False
                result = subprocess.call(scp_file, shell=True)
            _LOGGER.info(result)
            if result != 0:
                return False
        except Exception, e:
            _LOGGER.exception(e)
            return False
    return True


def transfer_file(file_obj, server, is_del=False, from_s3=True):
    if file_obj and server:
        local_base = MEDIA_ROOT
        server_conf = REMOTEDB_SETTINGS[server]
        # if not configed remote, use this dir
        remote_base = server_conf['remote_base'] if server_conf.get(
            'remote') else LOCAL_STATIC_RESOURCE
        s3_flag = False
        if from_s3 and server_conf.get('s3_remote'):
            remote_base = server_conf["s3_remote"]
            s3_flag = True
        remote = os.path.join(remote_base, file_obj)
        if is_del:
            if s3_flag:
                try:
                    os.unlink(remote)
                    result = True
                except OSError as e:
                    result = False
            else:
                result = sdel(
                    server_conf["statics"], 'static', KEY_FILE, remote)
            return (result, "")
        else:
            local = os.path.join(local_base, file_obj)
            if s3_flag:
                try:
                    mkdir = os.path.dirname(remote)
                    os.makedirs(mkdir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise ValueError(
                            ('mkdir file path %s for s3 fail') % file_obj)
                try:
                    shutil.copy(local, remote)
                except EnvironmentError as e:
                    raise ValueError(('upload file %s to s3 fail') % file_obj)
                return (True, '%s/%s' % (S3_DOMAIN, file_obj))
            else:
                result = scp(
                    server_conf['statics'], 'static', KEY_FILE, local, remote)
                if not result:
                    raise ValueError(('upload file %s fail') % file_obj)
                    return (False,)
                else:
                    return (
                        True, 'http://%s/resources/%s' % (
                            server_conf['domain'], file_obj))
