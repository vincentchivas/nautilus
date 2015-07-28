# -*- coding: utf-8 -*-


class Image(object):
    '''
     diff size of images for ios devices
    '''
    Iph4_5s = 'iphone2x'
    Iph6_ = 'iphone3x'
    Ipad = 'ipad3x'


class PackageType(object):
    # package way diff
    '''
     package data is used to be two parts,
     one is rule and the other is meta
     {
       'id': xxx,
       '_rule': {},
       '_meta': {}
        }
    '''
    Common = 'meta'  # almost used this style
    Inject = 'inject'
    Intersect = 'inter'


class UploadStatus(object):
    '''
     when press upload, the status will be changed
    '''
    UNUPLOAD_LOCAL = 1  # red poit
    UNUPLOAD_EC2 = 2  # origin poit
    NOMORAL = 0      # none


class TypeStatus(object):
    '''
     different message has different type,
     spd is short for speeddial ; bkm is short for bookmark,sech to searcher
    '''
    SPD_ADD = 1
    SPD_MOD = 2
    SPD_DEL = 3
    BKM_ADD = 4
    BKM_MOD = 5
    BKM_DEL = 6
    SECH_SAVE = 7
    SECH_DEL = 9
    PC_BKM_ADD = 1
    PC_BKM_MOD = 2
    PC_BKM_DEL = 3


class NameFactory(object):
    '''
    get the field to the real model name
    '''
    modify_fields = [
        'speeddial', 'bookmark', 'speeddialfolder', 'bookmarkfolder']
    other_fields = [
        'searcher', 'ispeeddial', 'ibookmark', 'isearcher', 'pcbookmark']

    @classmethod
    def fetch_name(cls, name):
        model_name = None
        if name == 'logo':
            # when pass logo it ref to icon collection
            model_name = 'icon'
        elif name.find('modify') != -1:
            # bookmark_modify is ref to bookmark
            model_name = name.split('_')[0]
        else:
            model_name = name
        return model_name

    @classmethod
    def combine_cond(cls, name, nid):
        '''
        used to deal with some modify_fields, when delete or find
        '''
        cond = {}
        pattern = name + '.id'
        mod_pattern = None
        if name in cls.modify_fields:
            cond1 = {pattern: nid, 'push_type': name}
            if name.endswith('folder'):
                mod_pattern = name.split('folder')[0] + '_modify.id'
            else:
                mod_pattern = name + '_modify.id'
            cond2 = {mod_pattern: nid, 'push_type': name}
            cond['$or'] = [cond1, cond2]
        elif name in cls.other_fields:
            mod_pattern = name + '_modify.id'
            cond['$or'] = [{pattern: nid}, {mod_pattern: nid}]
        else:
            cond.update({pattern: nid})
        return cond
