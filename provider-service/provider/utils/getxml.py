import requests


def send_req():
    parameters = {'callback_url': u'httP://172.16.7.14/provider/downxml'}
    parameters['context'] = '123'
    # parameters['version'] = 'v11.2.0'
    url = u'http://172.16.77.22:8080/jenkins/job/DolphinINT_strings/' \
        'buildWithParameters'
    author = ('bhuang', '6a49153ec7c421c9b15e3cdae104c7b3')
    r = requests.post(url, auth=author, params=parameters)
    if r.status_code < 300 and r.status_code > 199:
        return 'accept'
    else:
        return 'error'

if __name__ == '__main__':
    try:
        result = send_req()
        print result
    except Exception, e:
        print e
