import os
#import re
#from dolphinopadmin.base.content import ALL_FLAG, OTHER
#from dolphinopadmin.utils import scp
import logging
import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
#from dolphinopadmin.remotedb import config, basedb
from django.utils.translation import ugettext_lazy as _
from django.db.models.base import ModelBase
from dolphinopadmin.base import CustomManager
from dolphinopadmin.base.management import create_permission
from django.core.management.color import no_style
from dolphinopadmin.utils import scp

from django.db import connections, DEFAULT_DB_ALIAS

logger = logging.getLogger('dolphinopadmin.admin')

#config(basedb, settings.ENV_CONFIGURATION)

DB_SERVERS = settings.ENV_CONFIGURATION

EPOCH = datetime.datetime(1970, 1, 1)


def total_seconds(delta):
    """return total seconds of a time delta."""
    if not isinstance(delta, datetime.timedelta):
        raise TypeError('delta must be a datetime.timedelta.')
    return delta.days * 86400 + delta.seconds + delta.microseconds / 1000000.0


def datetime2timestamp(dt, convert_to_utc=False):
    '''
    Converts a datetime object to UNIX timestamp in milliseconds.
    '''
    if isinstance(dt, datetime.datetime):
        if convert_to_utc:
            dt = dt + datetime.timedelta(hours=-8)
        timestamp = total_seconds(dt - EPOCH)
        return long(timestamp)
    return dt


def custom_syncdb(dynamic_model):
    # refer to django.core.management.commonds.syncdb
    global tables, connection
    # print dynamic_model
    db = DEFAULT_DB_ALIAS
    if 'connection' not in globals():
        connection = connections[db]
        tables = connection.introspection.table_names()
    cursor = connection.cursor()
    table_style = no_style()
    pending_references = {}

    dynamic_table_name = dynamic_model._meta.db_table
    if dynamic_table_name not in tables:
        sql, references = connection.creation.sql_create_model(
            dynamic_model, table_style)
        for refto, refs in references.items():
            pending_references.setdefault(refto, []).extend(refs)
            sql.extend(connection.creation.sql_for_pending_references(
                refto, table_style, pending_references))
        sql.extend(connection.creation.sql_for_pending_references(
            dynamic_model, table_style, pending_references))
        print 'create dynamic talbe %s' % dynamic_table_name
        for statement in sql:
            cursor.execute(statement)
        tables.append(dynamic_table_name)


def model_factory(class_prefix, model_prefix, model, app_name, filter_dict):

    def _get_meta():
        class Meta:
            proxy = True
            app_label = app_name
            verbose_name = '%s %s' % (class_prefix, meta_name)
            verbose_name_plural = '%s %s' % (class_prefix, meta_name)

        return Meta
    # filter_dict.update({'is_hide':False}
    meta_name = unicode(model._meta.verbose_name) if hasattr(
        model, '_meta') and hasattr(model._meta, 'verbose_name') else model.__name__
    class_attrs = {
        'Meta': _get_meta(),
        '__module__': model.__module__,
        'filters': filter_dict,
        'objects': CustomManager(filter_dict)
    }
    # class_attrs.update(filter_dict)
    class_name = '%s%s' % (model_prefix, model.__name__)
    model_class = ModelBase(class_name, (model,), class_attrs)
    create_permission(model_class)
    if class_name not in globals():
        globals()[model_class.__name__] = model_class
    return model_class


def ship_factory((master, slave), unicode_str, extra='{}',):

    def _get_meta(tablename):
        class Meta:
            db_table = tablename
            verbose_name = _('%(m)s Link %(s)s') % {
                'm': meta_name_m, 's': meta_name_s}
            verbose_name_plural = _(
                '%(m)s Link %(s)s') % {'m': meta_name_m, 's': meta_name_s}

        return Meta

    def _get_unicode(tmp_str):
        return lambda self: eval(tmp_str)
        """
        def test(self):
            tmp = eval(unicode_str)
            return tmp
        return test()
        """
    # filter_dict.update({'is_hide':False}
    applabel = master._meta.app_label
    base_class_name = '%s%sship' % (master.__name__, slave.__name__)
    db_name = '%s_%s' % (applabel, base_class_name.lower())
    class_name = '%s_%s' % (applabel, base_class_name)
    # if class_name in globals():
    #    return (globals()[class_name],True)
    meta_name_m = unicode(master._meta.verbose_name) if hasattr(
        master, '_meta') and hasattr(master._meta, 'verbose_name') else master.__name__
    meta_name_s = unicode(slave._meta.verbose_name) if hasattr(
        slave, '_meta') and hasattr(slave._meta, 'verbose_name') else slave.__name__
    class_attrs = {
        'Meta':  _get_meta(db_name),
        '__module__': master.__module__,
        #'__unicode__': _get_unicode(unicode_str),
    }
    for i in (master, slave):
        class_attrs[i.__name__.lower()] = models.ForeignKey(i)
    class_attrs.update(eval(extra))
    model_class = ModelBase(class_name, (models.Model,), class_attrs)
    #model_class._meta.db_table = db_name
    custom_syncdb(model_class)
    create_permission(model_class)
    # if class_name not in globals():
    #    globals()[class_name] = model_class
    return (model_class, False)


class allPlatformBase(models.Model):
    platform = models.CharField(max_length=100, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.platform = self.filters['platform']
        super(allPlatformBase, self).save(*args, **kwargs)


class BaseStatus(models.Model):
    is_upload_local = models.BooleanField(
        default=False, verbose_name=_('upload to local'))
    is_upload_china = models.BooleanField(
        default=False, verbose_name=_('upload to china'))
    is_upload_ec2 = models.BooleanField(
        default=False, verbose_name=_('upload to ec2'))
    modifier = models.ForeignKey(
        User, verbose_name=_('modifier'), related_name="+", editable=False)
    creator = models.ForeignKey(
        User, verbose_name=_('creator'), related_name="+", editable=False)
    modified_time = models.DateTimeField(
        verbose_name=_('last modified'), editable=False)
    created_time = models.DateTimeField(
        verbose_name=_('create time'), editable=False)
    is_hide = models.BooleanField(
        default=False, verbose_name=_('hided'), editable=False)

    def __unicode__(self):
        log_keys = (('title', _('title')),
                    ('name', _('name')), ('url', _('url')))
        item_dict = self.__dict__
        return u''.join(['(%s:%s)' % (unicode(key[1]), item_dict[key[0]]) for key in log_keys if key[0] in item_dict])

    def transfer_file(self, file_obj, server, is_del=False):
        if file_obj and server:
            local_base = settings.MEDIA_ROOT
            server_conf = DB_SERVERS[server]
            remote_base = server_conf['remote_base'] if server_conf.has_key(
                'remote') else '/home/static/resources'
            remote = os.path.join(remote_base, file_obj)
            if is_del:
                result = scp.sdel(server_conf['statics'], 'static',
                                  '/var/app/data/dolphinopadmin-service/static.pem', remote)
                return (result,)
            else:
                local = os.path.join(local_base, file_obj)
                result = scp.scp(server_conf['statics'], 'static',
                                 '/var/app/data/dolphinopadmin-service/static.pem', local, remote)
                print result
                if not result:
                    raise ValueError(_('upload file %s fail') % file_obj)
                    return (False,)
                else:
                    return (True, 'http://%s/resources/%s' % (server_conf['domain'], file_obj))

    def delete(self):
        self.hide = 1
        self.save()

    class Meta:
        abstract = True
