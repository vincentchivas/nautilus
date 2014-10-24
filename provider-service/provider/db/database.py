from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging
from provider.settings import DBS, HOST

_LOGGER = logging.getLogger('db')
dbstr = DBS['default']
conn_string = ''.join((dbstr['ENGINE'], '://', dbstr['USER'], ':',
                       dbstr['PASSWORD'], '@', HOST, ':', dbstr['PORT'], '/',
                       dbstr['NAME']))
engine = create_engine(conn_string)


def get_session():
    Session = sessionmaker(bind=engine)
    return Session()


def save(instance):
    try:
        session = get_session()
        cls = instance.__class__
        ret = session.query(cls).filter(cls.id == instance.id).first()
        if ret is None:
            session.add(instance)
            _LOGGER.info(
                "@database_insert---table : %s ",
                instance.__tablename__)
        else:
            instance_id = instance.id
            ret = session.query(cls).get(instance_id)
            uptdata = instance.__dict__
            if uptdata.get('_sa_instance_state'):
                uptdata.pop('_sa_instance_state')
            uptdata.pop('id')
            for k, v in uptdata.items():
                ret.__setattr__(k, v)
            _LOGGER.info(
                "@database_update---table : %s id: %d",
                instance.__tablename__, instance_id)
        session.commit()
    except Exception, exception:
        _LOGGER.info("save exception occurred:%s" % exception)
    finally:
        session.close()


def query_results(module_name, class_name, cond, first=True):
    sess = get_session()
    exec('from %s import %s' % (module_name, class_name))
    if first:
        querystr = 'sess.query(%s).filter(%s).first()' % (class_name, cond)
    else:
        querystr = 'sess.query(%s).filter(%s).all()' % (class_name, cond)
    try:
        results = eval(querystr)
    except:
        sess.rollback()
        _LOGGER.info("@database_query---table:%s", class_name)
    finally:
        sess.close()
        return results
