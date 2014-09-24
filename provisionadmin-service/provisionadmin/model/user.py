# -*- coding: utf-8 -*-
import logging
from provisionadmin.utils.common import md5digest, unix_time
from provisionadmin.model.base import ModelBase
from provisionadmin.utils.common import now_timestamp

_LOGGER = logging.getLogger("model")


class User(ModelBase):
    db = 'user'
    collection = 'user'
    required = ('user_name', 'password', 'email')
    unique = ('user_name',)
    optional = (
        ('is_active', True),
        ('is_superuser', False),
        ('group_id', []),
        ('permission_list', []),
        ('modified', now_timestamp),
        ('department', [])
    )

    @classmethod
    def new(cls, user_name, password='', email='', is_active=True,
            is_superuser=False, group_id=[], permission_list=[]):
        '''
        create user instance
        '''
        instance = cls()
        instance.user_name = user_name
        # if password: 密码已经在前端md5加密
        #  instance.password_hash = User.calc_password_hash(password)
        instance.password = password
        instance.email = email
        instance.is_active = is_active
        instance.is_superuser = is_superuser
        instance.group_id = group_id
        instance.permission_list = permission_list
        instance.created = instance.modified = unix_time()
        return instance

    @classmethod
    def save_user(cls, instance):
        return cls.save(instance, check_unique=False)

    @classmethod
    def update_user(cls, cond, upt_dict):
        return cls.update(cond, upt_dict)

    @classmethod
    def find_users(cls, cond, toarray=True):
        return cls.find(cond, toarray=toarray)

    @classmethod
    def find_one_user(cls, cond, toarray=True):
        users = cls.find(cond, toarray=toarray)
        if users:
            return users[0]
        else:
            return None

    @classmethod
    def del_user(cls, ids):
        for uid in ids:
            user = cls.find_users({"_id": uid})
            if user:
                cls.remove({"_id": uid})
                _LOGGER.info("remove group id %d" % uid)
                ids.remove(uid)
            else:
                _LOGGER.info("group id %d is not exist" % uid)
        return ids

    @classmethod
    def calc_password_hash(cls, password):
        return unicode(md5digest(password))

    @classmethod
    def change_password(cls, new_password):
        cls.password = User.calc_password_hash(new_password)
        cls.modified = unix_time()

    @classmethod
    def change_group(cls, new_group_id):
        cls.group_id = new_group_id
        cls.modified = unix_time()

    @classmethod
    def change_permission(cls, new_permission_list):
        cls.permission_list = new_permission_list
        cls.modified = unix_time()


class Group(ModelBase):
    db = 'user'
    collection = 'groups'
    required = ('group_name',)
    unique = ('group_name',)
    optional = (('permission_list', []),)

    @classmethod
    def new(cls, group_name, permission_list=[]):
        """
        creat group instance
        """
        instance = cls()
        instance.group_name = group_name
        instance.permission_list = permission_list
        return instance

    @classmethod
    def save_group(cls, instance):
        return cls.save(instance, check_unique=False, extract=False)

    @classmethod
    def update_group(cls, cond, upt_dict):
        return cls.update(cond, upt_dict)

    @classmethod
    def find_group(cls, cond, toarray=True):
        return cls.find(cond, toarray=True)

    @classmethod
    def find_one_group(cls, cond, toarray=True):
        groups = cls.find(cond, toarray)
        if groups:
            return groups[0]
        else:
            return None

    @classmethod
    def del_group(cls, ids):
        for gid in ids:
            group = cls.find_group({"_id": gid})
            if group:
                cls.remove({"_id": gid})
                users_in_group = User.find_users({"group_id": gid})
                if users_in_group:
                    for user in users_in_group:
                        glist = user.get("group_id")
                        glist.remove(gid)
                        User.update_user(
                            {"_id": user["_id"]}, {"group_id": glist})
                        _LOGGER.info(
                            "remove group id:%d from user %d" %
                            (gid, user["_id"]))
                ids.remove(gid)
            else:
                _LOGGER.info("group id %d is not exist" % gid)
        return ids


class Permission(ModelBase):
    db = 'user'
    collection = 'permission'
    required = ('perm_type', 'perm_name', 'app_label', 'model_label',
                'container', 'action')

    @classmethod
    def new(cls, perm_type, perm_name, app_label, model_label, container,
            action):
        instance = cls()
        instance.perm_type = perm_type
        instance.perm_name = perm_name
        instance.app_label = app_label
        instance.model_label = model_label
        instance.container = container
        instance.action = action
        return instance

    @classmethod
    def save_perm(cls, instance):
        return cls.save(instance, check_unique=False, extract=False)

    @classmethod
    def find_perm(cls, cond, toarray=True):
        return cls.find(cond, toarray=toarray)

    @classmethod
    def find_one_perm(cls, cond, toarray=True):
        perms = cls.find(cond, toarray=toarray)
        if perms:
            return perms[0]
        else:
            return None

    @classmethod
    def del_perm(cls, ids):
        for pid in ids:
            perm = cls.find_perm({"_id": pid})
            if perm:
                cls.remove({"_id": pid})
                users_has_perm = User.find_users({"permission_list": pid})
                if users_has_perm:
                    for user in users_has_perm:
                        plist = user.get("permission_list")
                        plist.remove(pid)
                        User.update_user(
                            {"_id": user["_id"]}, {"permission_list": plist})
                        _LOGGER.info(
                            "remove group id:%d from user %d" %
                            (pid, user["_id"]))
                group_has_perm = Group.find_group({"permission_list": pid})
                if group_has_perm:
                    for group in group_has_perm:
                        plist = group.get("permission_list")
                        plist.remove(pid)
                        Group.update_group(
                            {"_id": group["_id"]}, {"permission_list": plist})
                        _LOGGER.info(
                            "remove Permission id:%d from group %d" %
                            (pid, group["_id"]))
                ids.remove(pid)
            else:
                _LOGGER.info("group id %d is not exist" % pid)
        return ids

    @classmethod
    def get_perms_by_uid(uid):
        perm_list = []
        user = User.find_users({"_id": int(uid)})
        if user:
            if user.is_superuser:
                return Permission.find_perm({})
            else:
                perm_list = user.permission_list
                gids = user.goup_id
                if gids:
                    for gid in gids:
                        group = Group.find_one_group({"_id": gid})
                        perm_list = perm_list + group.permission_list
                    perm_list = list(set(perm_list))
                return Permission.get_perms_by_ids(perm_list)
        else:
            return None

    @classmethod
    def get_perms_by_ids(pids):
        assert pids
        permissions = []
        for pid in pids:
            perm = Permission.find_one_perm({"_id": pid})
            if perm:
                permissions.append(perm)
        return permissions
