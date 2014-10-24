import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'provisionadmin.settings'
import time
import logging
import requests
import json
from common import log_handler
from enhanced_daemon import Daemon
from provider.model.buildtask import BuildTask
from provider.db.database import get_session
from provider.settings import HOST, BUILD_URL, STATUS_URL
from provider.utils.buildstatus import UNBUILD, BUILDING, BUILT, TIME_OUT

LOG_FILE = '/var/app/log/provider-service/build.log'
_HANDLER = log_handler(LOG_FILE)

_LOGGER = logging.getLogger('build')
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.DEBUG)


def buildservice(task):
    callback_url = '/'.join(('http:/', HOST, 'provider/submit'))
    parameters = {'callback_url': callback_url}
    parameters['context'] = task.taskid
    parameters['translated_strings_url'] = task.xml_link
    if not task.tag == 'new':
        parameters['tag'] = task.tag
    author = ('bhuang', '6a49153ec7c421c9b15e3cdae104c7b3')
    r = requests.post(BUILD_URL, auth=author, params=parameters)
    if r.status_code < 300 and r.status_code > 199:
        _LOGGER.info("client buildservice accept request")
    else:
        _LOGGER.info("client failed to receive request")


def send_build_status(taskid, status):
    parameters = {}
    parameters['taskid'] = taskid
    parameters['status'] = status
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    _LOGGER.info("parameters:" + json.dumps(parameters))
    req = requests.post(
        STATUS_URL, data=json.dumps(parameters), headers=headers)
    if req.status_code < 300 and req.status_code > 199:
        _LOGGER.info('accept for send_status')
    else:
        _LOGGER.info('error for send_status')


def get_first():
    try:
        sess = get_session()
        first_task = sess.query(BuildTask
                                ).filter(BuildTask.status == UNBUILD
                                         ).order_by(BuildTask.creattime.asc()
                                                    ).first()
    except Exception, ept:
        _LOGGER.info("get first task exception %s" % str(ept))
    finally:
        sess.close()
    return first_task


def get_status(taskid):
    try:
        sess = get_session()
        taskforbuild = sess.query(BuildTask).filter(
            BuildTask.taskid == taskid).first()
    except Exception, e:
        _LOGGER.error("get_status exception:%s" % str(e))
    finally:
        sess.close()
    if taskforbuild:
        return taskforbuild.status
    else:
        return None


def update_status(taskid, status):
    try:
        sess = get_session()
        task = sess.query(BuildTask).filter(BuildTask.taskid == taskid)
        task.update({"status": status})
        sess.flush()
        sess.commit()
    except Exception, ept:
        _LOGGER.error("update_status exception:%s" % str(ept))
    finally:
        sess.close()


class Task(Daemon):

    def run(self):
        delay = 60
        overtime_count = 12
        # set the counts to control the overtime
        while True:
            taskone = get_first()
            if taskone:
                update_status(taskone.taskid, BUILDING)
                send_build_status(taskone.taskid, BUILDING)
                buildservice(taskone)
                count = 1
                while True:
                    task_status = get_status(taskone.taskid)
                    # get the status of the building task
                    if task_status != BUILT:
                        time.sleep(10 * count)
                        count += 1
                        # over time
                        if count > overtime_count:
                            _LOGGER.info("taskid:%s overtime" % taskone.taskid)
                            update_status(taskone.taskid, TIME_OUT)
                            send_build_status(taskone.taskid, TIME_OUT)
                            _LOGGER.info(
                                "taskid:%s send status " % taskone.taskid)
                            break
                        _LOGGER.info("the count that wait:%d" % count)
                    else:
                        break
            else:
                time.sleep(delay)

if __name__ == '__main__':
    try:
        Task(name="buildtask").start()
    except Exception, ept:
        _LOGGER.info("process exception occurred:%s" % str(ept))
