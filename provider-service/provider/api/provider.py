# -*- coding: UTF-8 -*-
import logging
import time
import os
import re
import requests
import json
from xml.etree import ElementTree as ET
from ..utils.jsons import json_response_error, json_response_ok
from ..utils.respcode import UNKNOWN_ERROR, METHOD_ERROR, PARAM_ERROR
from ..utils.buildstatus import BUILT
from ..utils.md5tool import md5web, md5sum
from ..settings import STATIC_ROOT, HOST, STATUS_URL
from ..decorator import exception_handler
from ..db.database import save, query_results
from ..model.buildtask import XmlList, BuildTask, TagList, Lint_Result
from ..utils.common import download_file

_LOGGER = logging.getLogger('provider')


def _path_to_url(xpath):
    '''
    change the file path into a http url
    '''
    splits_path = xpath.split('/')
    array_for_url = ('http:/', HOST, 'provider', 'download',
                     splits_path[-3], splits_path[-2], splits_path[-1])
    return '/'.join(array_for_url)


def _send_status(task, lint_result_url):
    '''
    send status to i18n studio through http request
    '''
    parameters = {}
    parameters["taskid"] = task.taskid
    parameters["status"] = task.status
    parameters["apk_uri"] = task.apk_uri
    parameters["reason"] = task.reason
    parameters["log_uri"] = task.log_uri
    parameters["lint_url"] = lint_result_url
    lints = []
    raw_results = Lint_Result.get_lint_results(task.taskid)
    if raw_results:
        for result in raw_results:
            lint_dict = {
                "string_name": result.string_name,
                "error_msg": result.error_msg}
            lints.append(lint_dict)
    parameters["lint_result"] = lints
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    req = requests.post(
        STATUS_URL, data=json.dumps(parameters), headers=headers)
    if req.status_code < 300 and req.status_code > 199:
        _LOGGER.info("_send_status:send request success")
    else:
        _LOGGER.info("_send_status:error occurred")


def _save_lint_result(taskid, lint_result_url):
    rev = requests.get(lint_result_url, stream=True)
    filename = lint_result_url.split('/')[-1]
    file_path = os.path.join(STATIC_ROOT, 'lint_result', filename)
    download_file(rev, file_path)
    root = ET.parse(file_path).getroot()
    results = root.findall("issue")
    if results:
        patt = '<string name=\"(.+)\">'
        for item in results:
            error = item.get("errorLine1")
            group = re.search(patt, error)
            string_name = group.group(1)
            error_msg = item.get("message")
            result = Lint_Result(
                taskid=taskid,
                string_name=string_name,
                error_msg=error_msg)
            save(result)
            # callback url to send the lint_result to i18n, will be here
            _LOGGER.info("taskid:%s saved lint" % taskid)
    else:
        _LOGGER.info("taskid:%s has no lint errors" % taskid)


@exception_handler()
def submit_build(request):
    '''
    this is callback api, when the client build server finished the build task
    it will callback the url

    HTTP Method : POST

    Parameters:
     - context: context  to record taskid value
     - result: the builed result,it has 'BUILD_COMPLETE', 'error'
     - log: the log url
     - apk: the apk url
     - lint_result: check the lint error

     Return:
      1.built task finished, and it returns a parameter of 'error'
      {
        "status":0
        "data":{"info":"handle error"}
        }

      2.built task finished, and it returns a parameters of 'BUILD_COMPLETE'
      {
        "status":0
        "data":{"info":"handle correct"}
        }
    '''
    if request.method == 'POST':
        cur_time = int(time.time())
        taskid = request.POST.get('context')
        cond = "BuildTask.taskid=='%s'" % taskid
        task = query_results('provider.model.buildtask', 'BuildTask', cond)
        pass_tag = request.POST.get('result')
        task.status = BUILT
        lint_result = request.POST.get("lint_result")
        if lint_result:
            _save_lint_result(taskid, lint_result)
        else:
            lint_result = ""
        # save lint_result to table
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
            task.log_uri = _path_to_url(log_path)
            save(task)
            _send_status(task, lint_result)
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
            task.apk_uri = _path_to_url(apk_path)
            save(task)
            _send_status(task, lint_result)
            return json_response_ok({'info': 'handle correct'})
        else:
            return json_response_error(
                UNKNOWN_ERROR, msg='neither gives error or complete')
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


@exception_handler()
def download_xml(req):
    '''
    this is a callback api, when the client server finished package xml,it
    will return a url for us to download

    HTTP Method: POST

    Parameters
    version: version name
    package: package name
    result : the url of packaged xml

    Return:
    1.the client has no changes on current xmlfile
    {
      "status":0
      "data":{"info":"no more new xmlfile"}
        }

    2.the client updates the xmlfile
    {
      "status":0
      "data":{"info":"new ver xml download"}
        }
    '''
    if req.method == 'POST':
        appversion = req.POST.get('version')
        appname = req.POST.get('package')
        xml_url = req.POST.get('result')
        # download xml
        filecontent = os.path.join(STATIC_ROOT, 'xml', appversion)
        if not os.path.exists(filecontent):
            os.mkdir(filecontent)
        urlfilemd5 = md5web(xml_url)
        latest_xml = XmlList.get_latest_xml()
        cond = "XmlList.md5code =='%s'" % urlfilemd5
        chk_md5 = query_results('provider.model.buildtask', 'XmlList', cond)
        if not chk_md5:
            r = requests.get(xml_url, stream=True)
            cur_time = int(time.time())
            xmlfilepath = os.path.join(
                filecontent, 'xml_%s.zip' % cur_time)
            download_file(r, xmlfilepath)
            xml_uri = _path_to_url(xmlfilepath)
            unzipdir = os.path.splitext(xmlfilepath)[0]
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
                    except Exception, exception:
                        _LOGGER.info("exception occurred:%s" % str(exception))
                    return json_response_ok({'info': 'new version downloaded'})
                else:
                    os.system(
                        'cd %s && rm -rf %s && rm %s' %
                        (filecontent, unzipdir, xmlfilepath))
                    return json_response_ok({'info': 'no more new xmlfile'})
            else:
                md5code = md5sum(xmlfilepath)
                xml = XmlList(
                    appname=appname, appversion=appversion,
                    xml_link=xml_uri, md5code=md5code)
                try:
                    save(xml)
                except Exception, exception:
                    _LOGGER.info("exception occurred:%s" % str(exception))
                return json_response_ok({'info': 'new ver xmlfile downloaded'})
        else:
            return json_response_ok({'info': 'no new xml file'})
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


def _filter_tags(url):
    '''
    filter the tags we got from a http url
    '''
    tags = {}
    patterm = r'v[1-9][0-9].[0-9].[0-9]'
    r = requests.get(url)
    for line in r.iter_lines():
        m = re.match(patterm, line)
        if m:
            tag_key = m.group().replace('v', '')
            tags.setdefault(tag_key, []).append(line)
    return tags


@exception_handler()
def downtag(req):
    '''
    this a callback api ,when the client server finished packaging tags, it
    will return an url fo us to fetch.

    HTTP Method: POST

    Parameters:
    result: the tag url

    Return:
    {
      "status":0
      "data":{"info":[{"11.2.4":"v11.2.4"}]}
        }
    '''
    if req.method == 'POST':
        tagurl = req.POST.get('result')
        tags = _filter_tags(tagurl)
        for item in tags.iteritems():
            appversion = item[0]
            if appversion > '11.1.6':
                tagname = '|'.join(item[1])
                cond = "TagList.appversion =='%s'" % appversion
                tag_exist = query_results(
                    'provider.model.buildtask', 'TagList', cond)
                if tag_exist:
                    if tag_exist.tagname == tagname:
                        continue
                    else:
                        tag_exist.tagname = tagname
                        save(tag_exist)
                else:
                    tag = TagList(appversion=appversion, tagname=tagname)
                    save(tag)
        return json_response_ok({'info': tags})
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


@exception_handler()
def get_tags(req):
    '''
    this is an api for i18n studio to get the tags

    HTTP Method: GET

    Parameters:
    appversion: the version name , such as '11.2.4'

    Return:
    when you give an appversion, it will return the tags for this appversion,
    when you give nothing at all,it will return all the tags
    {
    "status":0
    "data":{"info":[{"11.2.4":"v11.2.4"}]}
        }
    '''
    if req.method == 'GET':
        version = req.GET.get('appversion')
        tags = {}
        if not version:
            taglist = TagList.get_taglist()
            for item in taglist:
                tags.setdefault(item.appversion, item.tagname.split('|'))
        else:
            cond = "TagList.appversion == '%s'" % version
            tag_for_version = query_results(
                'provider.model.buildtask', 'TagList', cond)
            if tag_for_version:
                tags.setdefault(
                    tag_for_version.appversion,
                    tag_for_version.tagname.split('|'))
            else:
                tags.setdefault(version, 'new')
        return json_response_ok({'tags': tags})
    else:
        return json_response_error(METHOD_ERROR, msg='http method error')


@exception_handler()
def get_latest_xml(req):
    '''
    this is an api for i18n studio to get the newest xml file

    HTTP Method: GET

    Parameters:
    md5:the file md5 code

    Return:
    when u give nothing at all u will get the newest xml zip file
    when u pass in md5 code,if the code is different from the code of the
    newest xml file,then u download the newer one, else u got nothing.
    '''
    if req.method == 'GET':
        mdc = req.GET.get('md5')
        # appname = req.GET.get('appname')
        # appversion = req.GET.get('appversion')
        latest = XmlList.get_latest_xml()
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


@exception_handler()
def submit_task(req):
    '''
    this is an api for i18n studio to accept the build task.
    POST parameters:

    HTTP Method: POST

    Parameters:
    snap_id:the task id
    appname:the package name
    appversion: the version name, eg:'11.2.4'
    xml_link: the url to get xml, eg:'http://xxxxxxxx/xxx.zip'
    tag:the tag that we need to build task
    '''
    if req.method == 'POST':
        taskid = req.POST.get('snap_id')
        appname = req.POST.get('appname')
        appversion = req.POST.get('appversion')
        xml_file = req.POST.get('xml_link')
        tag = req.POST.get('tag')
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
                         xml_link=xml_file, tag=tag
                         )
        try:
            save(task)
            return json_response_ok({})
        except:
            return json_response_error(
                PARAM_ERROR, {}, msg='param error saved failed')
    else:
        return json_response_error(METHOD_ERROR, {}, msg='http method error')


@exception_handler()
def get_build_status(req):
    '''
    this is an api for i18n studio to provider the status for the tasks
    GET parameters:
    snap_id:the task id
    '''
    if req.method == 'GET':
        taskid = req.GET.get('snap_id')
        cond = "BuildTask.taskid =='%s'" % taskid
        task = query_results('provider.model.buildtask', 'BuildTask', cond)
        if task:
            result = task.__dict__
            result.pop('_sa_instance_state')
            result.pop('id')
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
