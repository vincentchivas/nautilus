from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
import logging
import datetime
from provider.db.database import engine, get_session

_LOGGER = logging.getLogger('model')
Base = declarative_base()


class BuildTask(Base):
    __tablename__ = 'buildtask'

    id = Column(Integer, primary_key=True)
    taskid = Column(String(100), nullable=False)
    appname = Column(String(100))
    appversion = Column(String(50))
    xml_link = Column(String(200))
    status = Column(Integer, default=0)
    result = Column(String(50))
    reason = Column(String(50))
    apk_uri = Column(String(200))
    log_uri = Column(String(200))
    tag = Column(String(200))
    creattime = Column(DateTime, default=datetime.datetime.now)
    modifytime = Column(DateTime, default=datetime.datetime.now)

    __table_args__ = (UniqueConstraint('taskid', name='_taskid_uc'),)
# status unbuild/building/built/time-out

    def __init__(
            self, taskid=None, appname='', appversion='', xml_link='', tag=''
    ):
        self.taskid = taskid
        self.appname = appname
        self.appversion = appversion
        self.xml_link = xml_link
        self.tag = tag


class XmlList(Base):
    __tablename__ = 'xmllist'

    id = Column(Integer, primary_key=True)
    md5code = Column(String(1000))
    appname = Column(String(100))
    appversion = Column(String(50))
    xml_link = Column(String(1000))
    timestamp = Column(DateTime, default=datetime.datetime.now)

    def __init__(
            self, appname='', appversion='', xml_link='', md5code=''
    ):
        self.appname = appname
        self.appversion = appversion
        self.xml_link = xml_link
        self.md5code = md5code

    @classmethod
    def get_latest_xml(cls):
        '''
        get the newest  xmlfile from providerdb
        '''
        try:
            sess = get_session()
            latest_xml = sess.query(XmlList
                                    ).order_by(XmlList.timestamp.desc()
                                               ).first()
            return latest_xml
        except Exception, exception:
            _LOGGER.info("get_latest_xml  occurred:%s" % str(exception))
        finally:
            sess.close()


class TagList(Base):
    __tablename__ = 'taglist'

    id = Column(Integer, primary_key=True)
    appversion = Column(String(50))
    tagname = Column(String(300))

    __table_args__ = (UniqueConstraint('appversion', name='_version_uc'),)

    def __init__(self, appversion, tagname):
        self.appversion = appversion
        self.tagname = tagname

    @classmethod
    def get_taglist(cls):
        '''
        get taglist
        '''
        try:
            sess = get_session()
            results = sess.query(TagList)
            return results
        except Exception, exception:
            _LOGGER.info("get_taglist occurred:%s" % str(exception))
        finally:
            sess.close()


class Lint_Result(Base):
    __tablename__ = 'lint_result'

    id = Column(Integer, primary_key=True)
    taskid = Column(String(100), nullable=False)
    string_name = Column(String(100))
    error_msg = Column(String(1000))
    create_time = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, taskid="", string_name="", error_msg=""):
        self.taskid = taskid
        self.string_name = string_name
        self.error_msg = error_msg

    @classmethod
    def get_lint_results(cls, taskid):
        '''
        get lint results
        '''
        try:
            sess = get_session()
            results = sess.query(
                Lint_Result).filter(Lint_Result.taskid == taskid)
            return results
        except Exception, expt:
            _LOGGER.info("get Lint_Result occurred:%s" % str(expt))
        finally:
            sess.close()


Base.metadata.create_all(engine)
