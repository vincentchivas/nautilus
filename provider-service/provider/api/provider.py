import logging
from ..utils.jsons import json_response_error, json_response_ok
from ..utils.respcode import *
from ..utils.md5tool import md5web, md5sum
import requests
import time
import os
from ..settings import STATIC_ROOT,  HOST
from ..db.database import save, get_session
from ..model.buildtask import XmlList, BuildTask
from ..utils.common import download_file

_LOGGER = logging.getLogger('provider')


def submit_build(request):
    if request.method == 'POST':
        cur_time = int(time.time())
        taskid = request.POST.get('context')
        sess = get_session()
        task = sess.query(BuildTask).filter(BuildTask.taskid == taskid).first()
        sess.close()
        pass_tag = request.POST.get('result')
        task.status = 2
        if pass_tag == 'error':
            task.reason = request.POST.get('reason')
            log_uri = request.POST.get('log')
            task.result = 'buildfailed'
            filecontent = os.path.join(STATIC_ROOT, 'log', task.appversion)
            if not os.path.exists(filecontent):
                os.mkdir(filecontent)
            r = requests.get(log_uri, stream=True)
            log_path = os.path.join(
                filecontent, '%s_%s.log' % (task.taskid, cur_time))
            download_file(r, log_path)
            l = log_path.split('/')
            a = ('http:/', HOST, 'provider', 'download', l[-3], l[-2], l[-1])
            task.log_uri = '/'.join(a)
            save(task)
            return json_response_ok({'info': 'handle error'})
        elif pass_tag == 'BUILD_COMPLETE':
            task.result = 'buildsuccess'
            apk_uri = request.POST.get('apk')
            filecontent = os.path.join(STATIC_ROOT, 'apk', task.appversion)
            if not os.path.exists(filecontent):
                os.mkdir(filecontent)
            r = requests.get(apk_uri, stream=True)
            apk_path = os.path.join(
                filecontent, '%s_%s.apk' % (task.taskid, cur_time))
            download_file(r, apk_path)
            l = apk_path.split('/')
            a = ('http:/', HOST, 'provider', 'download', l[-3], l[-2], l[-1])
            task.apk_uri = '/'.join(a)
            save(task)
            return json_response_ok({'info': 'handle correct'})
        else:
            json_response_error(
                UNKNOWN_ERROR, msg='neither gives error or complete')
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


def download_xml(req):
    if req.method == 'POST':
        appversion = req.POST.get('version')
        appname = req.POST.get('package')
        xml_url = req.POST.get('result')
        # download xml
        filecontent = os.path.join(STATIC_ROOT, 'xml', appversion)
        if not os.path.exists(filecontent):
            os.mkdir(filecontent)
        urlfilemd5 = md5web(xml_url)
        sess = get_session()
        latest_xml = sess.query(XmlList
                                ).filter(XmlList.appversion == appversion
                                         ).order_by(XmlList.timestamp.desc()
                                                    ).first()
        chk_md5 = sess.query(XmlList).filter(
            XmlList.md5code == urlfilemd5).first()
        sess.close()
        if not chk_md5:
            r = requests.get(xml_url, stream=True)
            cur_time = int(time.time())
            xmlfilepath = os.path.join(
                filecontent,  'xml_%s.zip' % cur_time)
            download_file(r, xmlfilepath)
            l = xmlfilepath.split('/')
            a = ('http:/', HOST, 'provider', 'download', l[-3], l[-2], l[-1])
            xml_uri = '/'.join(a)
            filename = l[-1].split('.')[0]
            unzipdir = os.path.join(filecontent, filename)
            os.mkdir(unzipdir)
            os.system('cd %s && unzip %s' % (unzipdir, xmlfilepath))
            if latest_xml:
                pre_xml_link = latest_xml.xml_link
                ll = pre_xml_link.split('/')
                pre_dirname = ll[-1].split('.')[0]
                aa = (STATIC_ROOT, ll[-3], ll[-2], pre_dirname)
                pre_xmlfilepath = '/'.join(aa)
                value = os.system('diff -ruNa %s %s' %
                                  (unzipdir, pre_xmlfilepath))
                if value:
                    md5code = md5sum(xmlfilepath)
                    xml = XmlList(
                        appname=appname, appversion=appversion,
                        xml_link=xml_uri, md5code=md5code)
                    try:
                        save(xml)
                    except Exception, e:
                        print e
                    return json_response_ok({'info': 'old ver downloaded'})
                else:
                    return json_response_ok({'info': 'no more new xmlfile'})
            else:
                md5code = md5sum(xmlfilepath)
                xml = XmlList(
                    appname=appname, appversion=appversion,
                    xml_link=xml_uri, md5code=md5code)
                try:
                    save(xml)
                except Exception, e:
                    print e
                return json_response_ok({'info': 'new ver xmlfile downloaded'})
        else:
            return json_response_ok({'info': 'no new xml file'})
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


def get_latest_xml(req):
    if req.method == 'GET':
        mdc = req.GET.get('md5')
        #appname = req.GET.get('appname')
        #appversion = req.GET.get('appversion')
        sess = get_session()
        latest = sess.query(XmlList
                            ).order_by(XmlList.timestamp.desc()).first()
        sess.close()
        result = latest.__dict__
        result.pop('_sa_instance_state')
        result.pop('id')
        result.pop('timestamp')
        if mdc:
            md5code = latest.md5code
            if mdc == md5code:
                return json_response_ok(
                    data={'info': 'newest'}, msg='u got newest xml')
            else:
                return json_response_ok(data=result, msg='get newest xml')
        else:
            return json_response_ok(data=result, msg='get newest xml')
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


def submit_task(req):
    if req.method == 'POST':
        taskid = req.POST.get('snap_id')
        appname = req.POST.get('appname')
        appversion = req.POST.get('appversion')
        xml_file = req.POST.get('xml_link')
        '''
        filecontent = os.path.join(STATIC_ROOT, 'uploads', appversion)
        if not os.path.exists(filecontent):
            os.mkdir(filecontent)
        cur_time = int(time.time())
        xmlfilepath = os.path.join(filecontent, 'xml_%s.zip' % cur_time)
        r = requests.get(xml_file, stream=True)
        download_file(r, xmlfilepath)
        l = xmlfilepath.split('/')
        a = ('http:/', HOST, 'provider', 'download', l[-3], l[-2], l[-1])
        xml_link = '/'.join(a)
        '''
        task = BuildTask(taskid=taskid, appname=appname, appversion=appversion,
                         xml_link=xml_file
                         )
        try:
            save(task)
            return json_response_ok({})
        except Exception, e:
            return json_response_error(
                PARAM_ERROR, {}, msg='param error saved failed')
    else:
        return json_response_error(METHOD_ERROR, {}, msg='http method error')


def get_build_status(req):
    if req.method == 'GET':
        taskid = req.GET.get('snap_id')
        sess = get_session()
        task = sess.query(BuildTask).filter(BuildTask.taskid == taskid).first()
        sess.close()
        if task:
            result = task.__dict__
            result.pop('_sa_instance_state')
            result.pop('id')
            result.pop('taskid')
            result.pop('creattime')
            result.pop('modifytime')
            result.pop('appname')
            result.pop('appversion')
            result.pop('xml_link')
            return json_response_ok(data=result, msg='get task info')
        else:
            return json_response_error(
                PARAM_ERROR, {}, msg='taskid is not exist')
    else:
        return json_response_error(METHOD_ERROR, {}, msg='http method error')
