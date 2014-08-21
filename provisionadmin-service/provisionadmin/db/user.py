# -*- coding: utf-8 -*-
from provisionadmin.db.config import USER_DB
from provisionadmin.model.user import User, Group, Permission
from provisionadmin.db.seqid import get_next_id
from provisionadmin.settings import CONTAINERS, APPS, OPERATOR


def save_user(user):
    assert user
    if not user.get('_id'):
        # assign sequential id
        user._id = get_next_id('user')
    return USER_DB.user.save(user)


def find_one_user(filters={}):
    item = USER_DB.user.find_one(filters)
    if item:
        user = User(item)
        return user
    else:
        return None


def del_user(user_ids=[]):
    assert user_ids
    count = len(user_ids)
    for user_id in user_ids:
        flag = USER_DB.user.remove({'_id': user_id})
        if flag.get('n') == 1:
            count = count - 1
    return count


def find_users(filters={}):
    users = []
    items = USER_DB.user.find(filters)
    if items:
        for item in items:
            users.append(User(item))
    return users


def find_session(filters={}):
    item = USER_DB.sessions.find_one(filters)
    return item


def save_group(group):
    assert group
    if not group.get('_id'):
        group._id = get_next_id('group')
    return USER_DB.groups.save(group)


def find_one_group(filters={}):
    item = USER_DB.groups.find_one(filters)
    if item:
        group = Group(item)
        return group
    else:
        return None


def del_group(group_ids=[]):
    assert group_ids
    count = len(group_ids)
    for group_id in group_ids:
        all_users = find_users({'group_id': group_id})
        for u in all_users:
            glist = u.group_id
            glist.remove(group_id)
            u.change_group(glist)
            save_user(u)
        flag = USER_DB.groups.remove({'_id': group_id})
        if flag.get('n') == 1:
            count = count - 1
    return count


def find_groups(filters={}):
    groups = []
    items = USER_DB.groups.find(filters)
    if items:
        for item in items:
            groups.append(Group(item))
    return groups


def save_permission(permission):
    assert permission
    if not permission.get('_id'):
        # assign sequential id
        permission._id = get_next_id('permission')
    return USER_DB.permission.save(permission)


def find_one_permission(filters={}):
    item = USER_DB.permission.find_one(filters)
    if item:
        permission = Permission(item)
        return permission
    else:
        return None


def check_perm_in_users_groups(permission_id):  # used for delete group
    check = False
    all_groups = find_groups()
    for g in all_groups:
        if permission_id in g.permission_list:
            check = True
            return check
    all_users = find_users()
    for u in all_users:
        if permission_id in u.permission_list:
            check = True
            return check
    return check


def del_permission(permission_ids=[]):
    assert permission_ids
    count = len(permission_ids)
    # perm_ids_cannot_delete=[]
    for permission_id in permission_ids:
        if not check_perm_in_users_groups(permission_id):
            flag = USER_DB.permission.remove({'_id': permission_id})
            if flag.get('n') == 1:
                count = count - 1
        else:
            # perm_ids_cannot_delete.append(permission_id)
            continue
    return count


def find_permissions(filters={}):
    permissions = []
    items = USER_DB.permission.find(filters)
    if items:
        for item in items:
            permissions.append(Permission(item))
    return permissions


def get_permissions_by_perm_ids(ids=[]):
    assert ids
    permissions = []
    for perm_id in ids:
        perm = find_one_permission({'_id': perm_id})
        if perm:
            permissions.append(perm)
        else:
            continue
    return permissions


def get_permission_by_uid(uid):
    assert uid
    perms_list = []
    uid = int(uid)
    u = find_one_user({'_id': uid})
    if u:
        perms_list = u.permission_list
        gids = u.group_id
        if gids:
            for gid in gids:
                g = find_one_group({'_id': gid})
                perms_list = perms_list + g.permission_list
            perms_list = list(set(perms_list))
        return get_permissions_by_perm_ids(perms_list)
    else:
        return None


def init_perms():
    count = 0
    containers = CONTAINERS
    apps = APPS
    ops = OPERATOR
    try:
        for key in containers:
            container = key
            app_labels = containers[key]
            for app_label in app_labels:
                model_labels = apps.get(app_label)
                for model_label in model_labels:
                    for op in ops:
                        p = Permission()
                        p.perm_profile  = op + '_' + model_label + \
                            '_' + app_label + '_' + container    # check unique
                        if not find_one_permission({'perm_profile': p.perm_profile}):
                            p.perm_name = 'can ' + op + ' ' + model_label
                            p.container = container
                            p.app_label = app_label
                            p.model_label = model_label
                            p.operator = op
                            count = count + 1
                            save_permission(p)
    except Exception as e:
        raise e
    return count


def init_superuser_menu():
    special_names = ['i18n', ]
    menu = []
    containers = USER_DB.permission.distinct('container')
    con_index = 0
    for container in containers:
        if container in special_names:
            menu.append(
                {'title': container, 'display': container.upper(), 'items': []})
        else:
            menu.append(
                {'title': container, 'display': container.title(), 'items': []})
        apps = USER_DB.permission.find(
            {'container': container}).distinct('app_label')
        app_index = 0
        for app in apps:
            menu[con_index]['items'].append(
                {'title': app, 'display': app.title(), 'items': []})
            models = USER_DB.permission.find(
                {'container': container, 'app_label': app}).distinct('model_label')
            for model in models:
                if model != app:
                    menu[con_index]['items'][app_index][
                        'items'].append({'title': model, 'display': model.title(), 'url': container + '/' + app + '/' + model})
                else:
                    menu[con_index]['items'][
                        app_index]['url'] = container + '/' + app
                    menu[con_index]['items'][app_index].pop('items')
            app_index = app_index + 1
        con_index = con_index + 1
    return menu


def init_menu(uid):
    assert uid
    special_names = ['i18n', ]
    perms = get_permission_by_uid(uid)
    if perms:
        menu = []
        containers = []
        apps = []
        models = []
        for perm in perms:
            containers.append(perm.get('container'))
        containers = list(set(containers))
        con_index = 0
        for container in containers:
            if container in special_names:
                menu.append(
                    {'title': container, 'display': container.upper(), 'items': []})
            else:
                menu.append(
                    {'title': container, 'display': container.title(), 'items': []})
            apps[:] = []
            for perm in perms:
                if perm.get('container') == container:
                    apps.append(perm.get('app_label'))
            apps = list(set(apps))
            app_index = 0
            for app in apps:
                menu[con_index]['items'].append(
                    {'title': app, 'display': app.title(), 'items': []})
                models[:] = []
                for perm in perms:
                    if perm.get('app_label') == app:
                        models.append(perm.get('model_label'))
                models = list(set(models))
                for model in models:
                    if model != app:
                        menu[con_index]['items'][app_index][
                            'items'].append({'title': model, 'display': model.title(), 'url': container + '/' + app + '/' + model})
                    else:
                        menu[con_index]['items'][
                            app_index]['url'] = container + '/' + app
                        menu[con_index]['items'][app_index].pop('items')
                app_index = app_index + 1
            con_index = con_index + 1
        return menu
    else:
        return None


def init_menu_permissions(uid):
    user = find_one_user({'_id': uid})
    if user:
        gid = user.group_id[0]
        group = find_one_group({'_id': gid})
        if user.is_superuser:
            menu = init_superuser_menu()
            role = 'superuser'
        elif group:
            menu = init_menu(uid)
            role = group.group_name
        else:
            menu = init_menu(uid)
            role = 'norole'
        item1 = {'menu': menu}
        item2 = {'role': role}  # 临时增加的，以后可能删掉
        items = []
        items.append(item1)
        items.append(item2)
        return items
    else:
        return None
