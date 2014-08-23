'''
Created on Jun 20, 2011

@author: chzhong
'''


class SetRemoteAddrMiddleware(object):

    def process_request(self, request):
        if 'HTTP_X_REAL_IP' in request.META:
            try:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
            except:
                # This will place a valid IP in REMOTE_ADDR but this shouldn't
                # happen
                request.META['REMOTE_ADDR'] = '0.0.0.0'
