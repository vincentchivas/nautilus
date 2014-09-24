import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'provisionadmin.settings'
import time
import logging
import requests
from common import log_handler
from enhanced_daemon import Daemon
from provider.model.buildtask import BuildTask
from provider.db.database import get_session, save
from provider.settings import HOST, BUILD_URL, STATUS_URL
from provider.utils.buildstatus import UNBUILD, BUILDING, BUILT, TIME_OUT

LOG_FILE = '/var/app/log/provider-service/build.log'
handler = log_handler(LOG_FILE)

logger = logging.getLogger('build')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


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
        logger.info("client buildservice accept request")
    else:
        logger.info("client failed to receive request")


def send_timeout_status(taskid):
    parameters = {}
    parameters['taskid'] = taskid
    parameters['status'] = TIME_OUT
    r = requests.post(STATUS_URL, data=parameters)
    if r.status_code < 300 and r.status_code > 199:
        logger.info('accept for send_status')
    else:
        logger.info('error for send_status')


def get_first():
    try:
        sess = get_session()
        first_task = sess.query(BuildTask
                                ).filter(BuildTask.status == UNBUILD
                                         ).order_by(BuildTask.creattime.asc()
                                                    ).first()
    except Exception, e:
        logger.info("get first task exception %s" % str(e))
    finally:
        sess.close()
    return first_task


def get_status(taskid):
    try:
        sess = get_session()
        taskforbuild = sess.query(BuildTask).filter(
            BuildTask.taskid == taskid).first()
    except Exception, e:
        logger.error("get_status exception:%s" % str(e))
    finally:
        sess.close()
    if taskforbuild:
        return taskforbuild.status
    else:
        return None


class Task(Daemon):

    def run(self):
        delay = 60
        overtime_count = 12
        # set the counts to control the overtime
        while True:
            taskone = get_first()
            if taskone:
                taskone.status = BUILDING
                save(taskone)
                buildservice(taskone)
                count = 1
                while True:
                    task_status = get_status(taskone.taskid)
                    if task_status != BUILT:
                        time.sleep(10 * count)
                        count += 1
                        # over time
                        if count > overtime_count:
                            logger.info("taskid:%s overtime" % taskone.taskid)
                            taskone.status = TIME_OUT
                            send_timeout_status(taskone.taskid)
                            logger.info(
                                "taskid:%s send status " % taskone.taskid)
                            break
                        logger.info("the count that wait:%d" % count)
                    else:
                        break
                if taskone.status == TIME_OUT:
                    save(taskone)
            else:
                time.sleep(delay)

if __name__ == '__main__':
    try:
        Task(name="buildtask").start()
    except Exception, e:
        logger.info("process exception occurred:%s" % str(e))
