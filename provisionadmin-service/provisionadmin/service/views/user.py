# -*- coding: utf-8 -*-
# import datetime
from django.http import HttpResponse
from provisionadmin.model.user import User, Group, Permission
from provisionadmin.db import user
# from django.shortcuts import render_to_response
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.utils import json, respcode
import simplejson
from provisionadmin.settings import CUS_TEMPLATE_DIR
import os


@exception_handler()
def login(req):
    if req.method == 'POST':
        name = req.POST.get('user_name')
        password = req.POST.get('password')
        if (name and password):
            u = user.find_one_user({'user_name': name, 'password': password})
            if not u:
                return json.json_response_error(
                    respcode.AUTH_ERROR, {}, msg='user_name or password error')
            else:
                req.session["uid"] = u['_id']
                uid = int(u['_id'])
                permissions = user.init_menu_permissions(uid)
                return json.json_response_ok(
                    data=permissions, msg='get left navi menu')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED,
                msg='user_name or password is not allowed  empty')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def logout(req):
    # session_key = req.session.session_key
    req.session.delete()
    return json.json_response_ok(data={}, msg='logout success')


@exception_handler()
def change_password(req):
    if req.method == 'GET':
        return HttpResponse(file(
            os.path.join(CUS_TEMPLATE_DIR, 'changepwd.html')).read())
    old_pwd = req.POST.get('old_pwd')
    new_pwd = req.POST.get('new_pwd')
    uname = req.POST.get('user_name')
    usr = user.find_one_user({'user_name': uname})
    if usr:
        if usr.password == old_pwd:
            usr.password = new_pwd
            user.save_user(usr)
            return json.json_response_ok(data={}, msg='password changed')
        else:
            return json.json_response_error(
                respcode.PASSWORD_UNMATCH, data={},
                msg='old password is not match')
    else:
        return json.json_response_error(
            respcode.PARAM_ERROR, data={},
            msg='user name error')


@exception_handler()
@check_session
def user_list(req):
    if req.method == 'GET':
        users = user.find_users()
        return json.json_response_ok(data=users, msg='user list')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def user_detail_modify(req, user_id):
    uid = int(user_id)
    if req.method == 'GET':
        u = user.find_one_user({'_id': uid})
        if u:
            return json.json_response_ok(data=u, msg='one user detail')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED, data=u, msg='user id is not exist')
    elif req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        u = user.find_one_user({'_id': user_id})
        if u:
            u.user_name = temp.get('user_name')
            u.email = temp.get('email')
            u.is_active = temp.get('is_active')
            u.is_superuser = temp.get('is_superuser')
            u.group_id = temp.get('group_id')
            u.permission_list = temp.get('permission_list')
            instance = user.save_user(u)
            if instance:
                return json.json_response_ok(
                    data={}, msg='modify user success')
            else:
                return json.json_response_error(
                    respcode.SAVE_ERROR, data={},
                    msg='save modified user error')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED, data={}, msg='user id is not exist')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def add_user(req):
    if req.method == 'POST':
        temp = req.raw_post_data
        user_name = temp.get('user_name')
        u = User.new(user_name)
        u.password = temp.get('password')
        u.email = temp.get('email')
        u.is_active = temp.get('is_active')
        u.is_superuser = temp.get('is_superuser')
        u.group_id = temp.get('group_id')
        u.permission_list = temp.get('permission_list')
        instance = user.save_user(u)
        if instance:
            return json.json_response_ok(data={}, msg='add user success')
        else:
            return json.json_response_error(
                respcode.SAVE_ERROR, data={}, msg='save new user error')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def del_user(req):
    if req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        user_ids = temp.get('user_ids')
        if not user_ids:
            return json.json_response_error(
                respcode.PARAM_ERROR, data={}, msg='userids must not be empty')
        else:
            count = user.del_user(user_ids)
            return json.json_response_ok(
                data={
                    'passin_counts': len(user_ids), 'delete_counts': count},
                msg='delete success')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def group_list(req):
    if req.method == 'GET':
        groups = user.find_groups()
        return json.json_response_ok(data=groups, msg='get group list')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def group_detail_modify(req, group_id):
    gid = int(group_id)
    if req.method == 'GET':
        g = user.find_one_group({'_id': gid})
        if g:
            return json.json_response_ok(data=g, msg='get one group detail')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED, data={}, msg='group id is not exist')
    elif req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        g = user.find_one_group({'_id': group_id})
        if g:
            g.group_name = temp.get('group_name')
            g.permission_list = temp.get('permission_list')
            user.save_group(g)
            return json.json_response_ok(
                {}, 'modify group permission_list')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED, data={}, msg='group id is not exist')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def add_group(req):
    if req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        group_name = temp.get('group_name')
        g = Group.new(group_name)
        g.permission_list = temp.get('permission_list')
        user.save_group(g)
        return json.json_response_ok(data={}, msg='add group success')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def del_group(req):
    if req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        group_ids = temp.get('group_ids')
        if not group_ids:
            return json.json_response_error(
                respcode.PARAM_ERROR, data={},
                msg='group_ids must not be empty')
        else:
            count = user.del_group(group_ids)
            return json.json_response_ok(
                data={'passin_counts': len(group_ids), 'delete_counts': count},
                msg='delete success')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def perm_list(req):
    if req.method == 'GET':
        permissions = user.find_permissions()
        return json.json_response_ok(permissions, 'get permission list')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def perm_add(req):
    if req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        perm_name = temp.get('perm_name')
        p = Permission.new(perm_name)
        p.perm_profile = temp.get('perm_profile')
        p.container = temp.get('container')
        p.app_label = temp.get('app_label')
        p.model_label = temp.get('model_label')
        p.operator = temp.get('operator')
        user.save_permission(p)
        return json.json_response_ok('ok', 'add permission success')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def perm_del(req):
    if req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        perm_ids = temp.get('perm_ids')
        if not perm_ids:
            return json.json_response_error(
                respcode.PARAM_ERROR, data={},
                msg='perm_ids must not be empty')
        else:
            count = user.del_permission(perm_ids)
            return json.json_response_ok(
                data={'passin_counts': len(perm_ids), 'delete_counts': count},
                msg='delete success')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def perm_detail_modify(req, perm_id):
    pid = int(perm_id)
    if req.method == 'GET':
        p = user.find_one_permission({'_id': pid})
        if p:
            return json.json_response_ok({}, 'get one permission detail')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED, data={},
                msg='permission id is not exist')
    elif req.method == 'POST':
        dict_strs = req.raw_post_data
        temp = simplejson.loads(dict_strs)
        p = user.find_one_permission({'_id': pid})
        if p:
            p.perm_name = temp.get('perm_name')
            p.perm_profile = temp.get('perm_profile')
            p.container = temp.get('container')
            p.app_label = temp.get('app_label')
            p.model_label = temp.get('model_label')
            p.operator = temp.get('operator')
            instance = user.save_permission(p)
            if instance:
                return json.json_response_ok(
                    data={}, msg='modify permission success')
            else:
                return json.json_response_error(
                    respcode.SAVE_ERROR, data={},
                    msg='save modified permission error')
        else:
            return json.json_response_error(
                respcode.PARAM_REQUIRED, data={},
                msg='permission id is not exist')
    else:
        return json.json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")
