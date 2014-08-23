import logging
from dolphinopadmin.utils import utc2local
from dolphinopadmin.remotedb.feedback import get_feedbacks
from dolphinopadmin.feedback.models import Feedback, VersionCode


_OS = {
    'android': 'Android',
    'ipad': 'iPad',
    'iphone': 'iPhone',
    'unknown': 'unknown',
    'pc': 'PC'
}

_LOCALE = {
    'zh_cn': 'zh_CN',
    'en_us': 'en_US',
    'unknown': 'unknown'
}


logger = logging.getLogger("dolphinopadmin.admin")


def _sync_feedbacks_from_remotedb(env):
    message = ''
    feedbacks = get_feedbacks(env)
    logger.debug(feedbacks)
    if len(feedbacks) <= 0:
        message += 'There is no feedback data to update!'
    else:
        try:
            # insert the feedback data into mysql
            for feedback in feedbacks:
                try:
                    logger.info(feedback)
                    temp_os = feedback['os'].lower()
                    temp_os = _OS[temp_os] if temp_os in _OS else 'unknown'
                    temp_locale = feedback['locale'].lower()
                    temp_locale = _LOCALE[
                        temp_locale] if temp_locale in _LOCALE else 'unknown'
                    try:
                        product = VersionCode.objects.get(
                            product=feedback['package'], version=int(feedback['version']))
                        vname = product.vname
                    except:
                        vname = 'unknown'

                    f = Feedback(
                        name=feedback['name'], contact_info=feedback[
                            'contact_info'],
                        locale=temp_locale, message=feedback[
                            'message'],
                        time=utc2local(feedback['time']),
                        os=temp_os, remote_address=feedback[
                            'remote_address'],
                        feedback_type=feedback[
                            'feedback_type'], deleted=False,
                        package=feedback[
                            'package'], source=feedback['source'],
                        version=feedback['version'], vname=vname)

                    f.save()
                except Exception, e:
                    logger.exception(e)
            message += 'Update Feedbacks Successfully!'
        except Exception, e:
            message += 'sync feedbacks failed!'
            logger.exception(e)
        logger.info(message)
    return message


def sync_feedbacks(server):
    _sync_feedbacks_from_remotedb(server)
