from django.db import models
from django.utils.translation import ugettext_lazy as _

from dolphinopadmin.configure.models import Rule
from dolphinopadmin.resource.models import Icon
from dolphinopadmin.base.base_model import BaseStatus

# to conent
APP_TAGS = (
    ('unknown', _('unknown')),
    ('new', _('new')),
    ('hot', _('hot')),
)
PRIORITY_CHOICES = tuple([(i, i) for i in range(1, 8)])


class WebappsBase(BaseStatus):

    platform = models.CharField(max_length=100, editable=False)

    def save(self, *args, **kwargs):
        self.platform = self.__class__.filters['platform']
        super(WebappsBase, self).save(*args, **kwargs)

    class Meta:
        abstract = True


def getcate_order():
    categories = Category.objects.order_by('-order')
    max_pos = 1 if len(categories) == 0 else \
        categories[0].order + 1
    return max_pos


def getapp_order():
    applications = Application.objects.order_by('-order')
    max_pos = 1 if len(applications) == 0 else \
        applications[0].order + 1
    return max_pos


class Category(WebappsBase):

    name = models.CharField(max_length=50, verbose_name=_('name'))
    description = models.TextField(
        max_length=256, blank=True, verbose_name=_('description'))
    order = models.IntegerField(default=getcate_order, verbose_name=_('order'))
    icon = models.ForeignKey(Icon, verbose_name=_('icon'))
    rule = models.ForeignKey(Rule, related_name='+', verbose_name=_('rule'))
    priority = models.IntegerField(choices=PRIORITY_CHOICES, help_text=_(
        'larger num mean higher priority'), default=1, verbose_name=_('priority'))

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    "id": self.id
                }
            }

        self.icon.upload_file(server)
        result_dict = {
            "_sync_key": {
                "id": self.id
            },
            "_key": {
                "id": self.id
            },
            "_priority": self.priority,
            "_rule": self.rule.content_dict(),
            "_meta": {
                "id": self.id,
                "name": self.name,
                "desp": self.description,
                "order": self.order,
                "icon": self.icon.get_url(server)
            }
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'webapps'
        verbose_name = _('category')


class Application(WebappsBase):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    promote = models.BooleanField(verbose_name=_('promote'))
    url = models.CharField(max_length=2000, verbose_name=_('url'))
    description = models.CharField(
        max_length=500, verbose_name=_('description'))
    color = models.CharField(
        max_length=50, help_text=_('example: "#FF0000"'), verbose_name=_('color'))

    order = models.IntegerField(
        default=getapp_order, verbose_name=_('Promote order'))
    category_order = models.IntegerField(
        default=getcate_order, verbose_name=_('category_order'))

    icon = models.ForeignKey(Icon, verbose_name=_('icon'))
    category = models.ForeignKey(Category, verbose_name=_('category'))
    rule = models.ForeignKey(Rule, verbose_name=_('rule'))
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES, default=1, help_text=_('larger num mean higher priority'))
    tag = models.CharField(max_length=100, choices=APP_TAGS,
                           default='unknown', verbose_name=_('application tag'))

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    "id": self.id
                }
            }

        self.icon.upload_file(server)
        result_dict = {
            "_sync_key": {
                "id": self.id
            },
            "_key": {
                "id": self.id
            },
            "_priority": self.priority,
            "_rule": self.rule.content_dict(),
            "_meta": {
                "id": self.id,
                "name": self.name,
                "promote": self.promote,
                "url": self.url,
                "desp": self.description,
                "color": self.color,
                "order": self.order,
                "cat_order": self.category_order,
                "icon": self.icon.get_url(server),
                "cid": self.category.id,
                "cat_name": self.category.name,
                "tag": self.tag
            }
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'webapps'
        verbose_name = _('application')


class Subject(WebappsBase):

    name = models.CharField(max_length=100, verbose_name=_('name'))
    description = models.CharField(
        max_length=500, verbose_name=_('description'))
    banner = models.BooleanField(verbose_name=_('banner'))

    order = models.IntegerField(verbose_name=_('order'))
    icon = models.ForeignKey(Icon, verbose_name=_('icon'))
    rule = models.ForeignKey(Rule)
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES, default=1, help_text=_('larger num mean higher priority'))

    tag = models.CharField(max_length=100, choices=APP_TAGS,
                           default='unknown', verbose_name=_('subject tag'))

    def get_tag(self):
        return ['unknown', 'new', 'hot'][self.tag]

    def content_dict(self, server, is_del=False):
        if is_del:
            return {
                "_sync_key": {
                    "id": self.id
                }
            }

        self.icon.upload_file(server)
        result_dict = {
            "_sync_key": {
                "id": self.id
            },
            "_key": {
                "id": self.id
            },
            "_priority": self.priority,
            "_rule": self.rule.content_dict(),
            "_meta": {
                "id": self.id,
                "name": self.name,
                "desp": self.description,
                "banner": self.banner,
                "order": self.order,
                "icon": self.icon.get_url(server),
                "tag": self.tag
            },
            "_meta_extend": {
                "apps": [{'id': item.application.id, 'order': item.order} for item in self.webapps_subjectapplicationship_set.all()]
            }
        }
        return result_dict

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'webapps'
        verbose_name = _('subject')
