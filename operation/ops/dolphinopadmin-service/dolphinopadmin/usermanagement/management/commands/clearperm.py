# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from dolphinopadmin.utils.sites import custom_site


class Command(BaseCommand):

    def handle(self, *args, **options):
        admin.autodiscover()
        allRegisteredModel = custom_site._registry

        appModelNeed = []
        inlineModels = []

        for model_item in allRegisteredModel:
            print model_item._meta.app_label, model_item._meta.module_name, model_item._meta.object_name
            appModelNeed.append(
                (model_item._meta.app_label, model_item._meta.module_name))

            admin_item = allRegisteredModel[model_item]
            if hasattr(admin_item, "inlines") and len(admin_item.inlines) > 0:
                for inline in admin_item.inlines:
                    inlineModels.append(
                        (inline.model._meta.app_label, inline.model._meta.module_name))

        print "length of all rgistered models is ", len(appModelNeed)
        print "length of all inlines models is ", len(inlineModels)

        allContentType = ContentType.objects.all()
        modelsDelete = []
        for item_model in allContentType:
            tempTuple = (item_model.app_label, item_model.model)
            # 增加逻辑防止 xxxxship的权限被误删
            if not (tempTuple in appModelNeed or tempTuple in inlineModels):
                modelsDelete.append(item_model)
        print len(modelsDelete), "model items to be delete"

        counter = 0
        for ct_item in modelsDelete:
            deletePerm = ct_item.permission_set.all()
            if len(deletePerm) == 0:
                print ">>>> miss match ", ct_item.app_label, ct_item.model, ct_item.id, " <<<<"
                continue
            print ">>>> deleting permission.... ", ct_item.app_label, ct_item.model, ct_item.id, " <<<<"
            for subItem in deletePerm:
                print "  ", subItem
                sss = subItem.delete()
                counter += 1
        print counter, " permission deleted.."
        counter = 0
        for ct_item in modelsDelete:
            print ">>>> deleting content_type.... ", ct_item.app_label, ct_item.model, ct_item.id, " <<<<"
            ct_item.delete()
            counter += 1
        print counter, "content_types deleted..."
