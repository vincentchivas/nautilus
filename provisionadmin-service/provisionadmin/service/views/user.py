# -*- coding: utf-8 -*-
import os
import simplejson
from django.http import HttpResponse
from provisionadmin.model.user import User, Group, Permission
from provisionadmin.db import user
from provisionadmin.decorator import check_session, exception_handler
from provisionadmin.utils.json import json_response_error, json_response_ok
from provisionadmin.utils import respcode
from provisionadmin.settings import CUS_TEMPLATE_DIR


@exception_handler()
def login(req):
    '''
    login api is used for user to login in the system
    and return the left navigation and permissions

    Request URL: admin/login

    HTTP Method: POST

    Parameters:
     --user_name:user name to login
     --password:

    Return:
    {
     "status":0
     "data":{
              "features":["aa","bb"] ,
              "menu":{"items":[{"display":"Translation","model":"translate"}]},
              "permissions":[{"action":"add","model":"translation"}]
            }
        }
    '''

    if req.method == 'POST':
        name = req.POST.get('user_name')
        password = req.POST.get('password')
        if name and password:
            u = user.find_one_user({'user_name': name, 'password': password})
            if not u:
                return json_response_error(
                    respcode.AUTH_ERROR, {}, msg='user_name or password error')
            else:
                req.session["uid"] = u['_id']
                uid = int(u['_id'])
                permissions = user.init_menu_permissions(uid)
                return json_response_ok(
                    data=permissions, msg='get left navi menu')
        else:
            return json_response_error(
                respcode.PARAM_REQUIRED,
                msg='user_name or password is not allowed  empty')
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method wrong")


@exception_handler()
@check_session
def logout(req):
    # session_key = req.session.session_key
    req.session.delete()
    return json_response_ok(data={}, msg='logout success')


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
            return json_response_ok(data={}, msg='password changed')
        else:
            return json_response_error(
                respcode.PASSWORD_UNMATCH, data={},
                msg='old password is not match')
    else:
        return json_response_error(
            respcode.PARAM_ERROR, data={},
            msg='user name error')


def list_group(req):
    '''
    list api for show group list.

    Request URL:  /auth/group/list

    Http Method:  GET

    Parameters : None

    Return :
    {
     "status":0
     "data":{
              "items":[
              {
              "_id":"2",
              "group_name":"admin",
              "permission_list":[19,20,21,22]
              },
              {
                "_id":4,
                "group_name":"translator",
                "permission_list":[22,23]
              }
              ]
            }
        }

    '''
    if req.method == 'GET':
        cond = {}
        groups = Group.find_group(cond)
        data = {}
        data.setdefault("items", groups)
        return json_response_ok(data, "get group list")
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")


def create_group(req):
    '''
    create api to add group.

    Request URL:  /auth/group/add

    Http Method:  POST

    Parameters:
        {
           "group_name":"xxx",
           "perm_list":[1,2,3,4]
        }

    Return :
    {
     "status":0
     "data":{}
     "msg":"add successfully"
    }
    '''
    if req.method == 'POST':
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        group_name = temp_dict.get('group_name')
        if not group_name:
            return json_response_error(
                respcode.PARAM_REQUIRED,
                msg="parameter group_name invalid")
        group_Perm_list = temp_dict.get('perm_list')
        group = Group.new(group_name, group_Perm_list)
        Group.save_group(group)
        return json_response_ok({'info': group})
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg='http method error')


def detail_modify_group(req, group_id):
    '''
    this api is used to view or modify one group

    Request URL: /auth/group/{gid}

    HTTP Method:GET
    Parameters: None
    Return
     {
     "status":0
     "data":{
              "item":[
              {
              "_id":"2",
              "group_name":"admin",
              "permission_list":[19,20,21,22]
              }
            }
        }

    HTTP Method:POST
    Parameters:
        {
           "group_name":"xxx",
           "perm_list":[1,2,3,4]
        }
    Return :
     {
     "status":0
     "data":{}
     "msg":"modify successfully"
    }
    '''
    group_id = int(group_id)
    if req.method == "GET":
        cond = {"_id": group_id}
        groups = Group.find_group(cond)
        data = {}
        if groups:
            group = groups[0]
            data.setdefault("item", group)
            return json_response_ok(
                data, msg="get group one group detail")
        else:
            return json_response_error(
                respcode.PARAM_ERROR, msg="the id is not exist")
    elif req.method == "POST":
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        group_name = temp_dict.get('group_name')
        if not group_name:
            return json_response_error(
                respcode.PARAM_REQUIRED,
                msg="parameter group_name invalid")
        group_Perm_list = temp_dict.get('perm_list')
        group = Group.new(group_name, group_Perm_list)
        group["_id"] = group_id
        Group.save_group(group)
        return json_response_ok({'info': group})
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")


def delete_group(req):
    '''
    this api is used to delete group,when one group removed,the user who
    in this group ,the group id will remove too.

    Request URL: /auth/group/delete

    HTTP Method: POST

    Parameters:
        {
            "gids":[2,3]
            }

    Return:
     {
     "status":0
     "data":{}
     "msg":"delete successfully"
     }
    '''
    if req.method == "POST":
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        gids = temp_dict.get("gids")
        assert gids
        ids = Group.del_group(gids)
        if not ids:
            return json_response_ok({}, msg="delete successfully")
        else:
            return json_response_error(
                respcode.PARAM_ERROR, msg="ids:%s is invalid" % ids)
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")


def list_user(req):
    '''
        list api for show user list.

        Request URL:  /auth/user/list

        Http Method:  GET

        Parameters : None

        Return :
        {
        "status":0
        "data":{
                "items":[
                {
                "_id":"2",
                "user_name":"admin",
                "email":"xx@bainainfo.com",
                "permission_list":[19,20,21,22]
                },
                {
                    "_id":4,
                    "user_name":"translator",
                    "email":"xx@bainainfo.com",
                    "permission_list":[22,23]
                }
                ]
                }
            }

        '''
    if req.method == 'GET':
        cond = {}
        users = User.find_users(cond)
        data = {}
        data.setdefault("items", users)
        return json_response_ok(data, "get user list")
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")


def create_user(req):
    '''
        create api to add user.

        Request URL:  /auth/user/add

        Http Method:  POST

        Parameters:
            {
            "user_name":"xxx",
            "password":"zxcf",
            "email":"zxy@bainainfo.com"
            "perm_list":[1,2,3,4]
            }

        Return :
        {
        "status":0,
        "data":{},
        "msg":"add successfully"
        }
        '''
    if req.method == 'POST':
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        required_list = ('user_name', 'password', 'email')
        for required_para in required_list:
            if not temp_dict.get(required_para):
                return json_response_error(
                    respcode.PARAM_REQUIRED,
                    msg="parameter %s invalid" % required_para)
        user_name = temp_dict.get('user_name')
        password = temp_dict.get('password')
        email = temp_dict.get('email')
        # is_active = temp_dict.get('is_active')
        # is_superuser = temp_dict.get('is_superuser')
        # group_id = temp_dict.get('group_id')
        # permission_list = temp_dict.get('permission_list')
        user_instance = User.new(user_name, password, email)
        # user_instance.group_id = group_id
        # user_instance.permission_list = permission_list
        User.save(user_instance)
        return json_response_ok({"info": user_instance})
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg='http method error')


def detail_modify_user(req, user_id):
    '''
        this api is used to view or modify one user

        Request URL: /auth/user/{uid}

        HTTP Method:GET
        Parameters: None
        Return
        {
        "status":0
        "data":{
                "item":[
                {
                "_id":"2",
                "user_name":"xxx",
                "permission_list":[19,20,21,22]
                }
                }
            }

        HTTP Method:POST
        Parameters:
            {
            "group_name":"xxx",
            "perm_list":[1,2,3,4]
            }
        Return :
        {
        "status":0
        "data":{}
        "msg":"modify successfully"
        }
        '''
    user_id = int(user_id)
    if req.method == "GET":
        cond = {"_id": user_id}
        users = User.find_users(cond)
        data = {}
        if users:
            user = users[0]
            data.setdefault("item", user)
            return json_response_ok(
                data, msg="get  one user detail")
        else:
            return json_response_error(
                respcode.PARAM_ERROR, msg="the user is not exist")
    elif req.method == "POST":
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        required_list = ('user_name', 'password', 'email')
        for required_para in required_list:
            if not temp_dict.get(required_para):
                return json_response_error(
                    respcode.PARAM_REQUIRED,
                    msg="parameter %s invalid" % required_para)
        user_name = temp_dict.get('user_name')
        password = temp_dict.get('password')
        email = temp_dict.get('email')
        # is_active = temp_dict.get('is_active')
        # is_superuser = temp_dict.get('is_superuser')
        group_id = temp_dict.get('group_id')
        # permission_list = temp_dict.get('permission_list')
        user_instance = User.new(user_name, password, email)
        # user_instance.group_id = group_id
        # user_instance.permission_list = permission_list
        User.save(user_instance)
        user_instance.group_id = group_id
        return json_response_ok({'info': user_instance})
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")


def delete_user(req):
    '''
        this api is used to delete user.

        Request URL: /auth/user/delete

        HTTP Method: POST

        Parameters:
            {
                "uids":[2,3]
                }

        Return:
        {
        "status":0
        "data":{}
        "msg":"delete successfully"
        }
    '''
    if req.method == "POST":
        temp_strs = req.raw_post_data
        temp_dict = simplejson.loads(temp_strs)
        uids = temp_dict.get("uids")
        assert uids
        ids = User.del_user(uids)
        if not ids:
            return json_response_ok({}, msg="delete successfully")
        else:
            return json_response_error(
                respcode.PARAM_ERROR, msg="ids:%s is invalid" % ids)
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")


def list_perm(req):
    '''
    list api for show user perm.

    Request URL:  /auth/perm/list

    Http Method:  GET

    Parameters : None

    Return :
    {
    "status":0
    "data":{
            "items":[
            {
                "_id":"2",
                "app_label":"translations-tool",
                "model_label":"translations",
                "operator":"add"
            },
            {
                "_id":4,
                "app_label":"translator-tool",
                "model_label":"revsion",
                "operator":"list"
            }
            ]
            }
        }

    '''
    if req.method == 'GET':
        cond = {}
        perms = Permission.find_perm(cond)
        data = {}
        data.setdefault("items", perms)
        return json_response_ok(data, "get permission list")
    else:
        return json_response_error(
            respcode.METHOD_ERROR, msg="http method error")
