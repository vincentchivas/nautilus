from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import logging
from provider.settings import DBS

logger = logging.getLogger('db')
dbstr = DBS['default']
s = ''.join((dbstr['ENGINE'], '://', dbstr['USER'], ':', dbstr['PASSWORD'],
             '@', dbstr['HOST'], ':', dbstr['PORT'], '/', dbstr['NAME']))
engine = create_engine(s)


def save(self):
    Session = sessionmaker(bind=engine)
    session = Session()
    cls = self.__class__
    ret = session.query(cls).filter(cls.id == self.id).first()
    if ret is None:
        session.add(self)
        logger.info(
            "@database_insert---table : %s ",
            self.__tablename__)
    else:
        instance_id = self.id
        ret = session.query(cls).get(instance_id)
        uptdata = self.__dict__
        if uptdata.get('_sa_instance_state'):
            uptdata.pop('_sa_instance_state')
        uptdata.pop('id')
        for k, v in uptdata.items():
            ret.__setattr__(k, v)
        logger.info(
            "@database_update---table : %s id: %d",
            self.__tablename__, instance_id)
    session.commit()
    session.close()
    return ret


def delete_by_id(self):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.delete(self)
    session.commit()
    session.close()


def get_session():
    Session = sessionmaker(bind=engine)
    return Session()
