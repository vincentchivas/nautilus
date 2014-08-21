from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
import datetime
from provider.db.database import engine

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
    creattime = Column(DateTime, default=datetime.datetime.now)
    modifytime = Column(DateTime, default=datetime.datetime.now)

    __table_args__ = (UniqueConstraint('taskid', name='_taskid_uc'),)
# status unbuild/building/builded

    def __init__(
            self, taskid=None, appname='', appversion='', xml_link='',
    ):
        self.taskid = taskid
        self.appname = appname
        self.appversion = appversion
        self.xml_link = xml_link


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

Base.metadata.create_all(engine)
