import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'provisionadmin.settings'
from enhanced_daemon import Daemon
import time
from provider.model.buildtask import BuildTask
from provider.db.database import get_session, save
import requests


def writelog(info):
    with open('/var/app/log/provider-service/autobuild.log', 'a+') as f:
        f.write(info)
        f.write('\n')


def buildservice(task):
    parameters = {'callback_url': u'http://172.16.7.14/provider/submit'}
    parameters['context'] = task.taskid
    parameters['translated_strings_url'] = task.xml_link
    #parameters['version'] = task.appversion
    url = u'http://172.16.77.22:8080/jenkins/job/DolphinINT_build/'\
        'buildWithParameters'
    author = ('bhuang', '6a49153ec7c421c9b15e3cdae104c7b3')
    r = requests.post(url, auth=author, params=parameters)
    if r.status_code < 300 and r.status_code > 199:
        writelog('accept')
    else:
        writelog('error')


def get_first():
    sess = get_session()
    first_task = sess.query(BuildTask
                            ).filter(BuildTask.status == 0
                                     ).order_by(BuildTask.creattime.asc()
                                                ).first()
    sess.close()
    return first_task


def check_status(taskid):
    sess = get_session()
    taskforbuild = sess.query(BuildTask).filter(
        BuildTask.taskid == taskid).first()
    sess.close()
    if taskforbuild:
        return taskforbuild.status == 2
    else:
        return False


class Task(Daemon):
    def run(self):
        delay = 60
        while True:
            taskone = get_first()
            if taskone:
                taskone.status = 1
                save(taskone)
                buildservice(taskone)
                count = 1
                while True:
                    if not check_status(taskone.taskid):
                        time.sleep(10 * count)
                        count += 1
                        # over time
                        if count > 20:
                            writelog('overtime')
                            break
                        writelog(str(count))
                    else:
                        break
            else:
                time.sleep(delay)

if __name__ == '__main__':
    Task(name="buildtask").start()
