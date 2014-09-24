import requests
import logging
from common import log_handler
from provider.settings import HOST, XML_URL

LOG_FILE = '/var/app/log/provider-service/xml.log'
handler = log_handler(LOG_FILE)

_LOGGER = logging.getLogger('xml')
_LOGGER.addHandler(handler)


def send_req():
    callback_url = '/'.join(('http:/', HOST, 'provider', 'downxml'))
    parameters = {'callback_url': callback_url}
    parameters['context'] = '123'
    author = ('bhuang', '6a49153ec7c421c9b15e3cdae104c7b3')
    r = requests.post(XML_URL, auth=author, params=parameters)
    if r.status_code < 300 and r.status_code > 199:
        _LOGGER.info("client service accepted request")
    else:
        _LOGGER.info("failed to send request to client service")

if __name__ == '__main__':
    try:
        send_req()
    except Exception, exception:
        _LOGGER.info("exception occurred:%s" % str(exception))
