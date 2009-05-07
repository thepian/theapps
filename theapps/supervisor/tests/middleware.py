from django.test import TestCase, Client
from django.http import HttpResponse
from django.conf import settings
from request_factory import RequestFactory

#from django.test import Client, LastRequestMiddleware

from theapps.supervisor.middleware import DeviceMiddleware

import re
SET_COOKIE = r'Set-Cookie: %s; Domain=%s; expires=%s; Path=/'
AFFINITY_COOKIE_PATTERN = re.compile(SET_COOKIE % (r'affinity="(?P<affinity>[^;]*)"',r'(?P<domain>[^\.]*\.local)',settings.AFFINITY_EXPIRY))
ACCESS_COOKIE_PATTERN = re.compile(SET_COOKIE % (r'affinity_access="(?P<affinity_access>[^;]*)"',r'(?P<domain>[^\.]*\.local)',settings.AFFINITY_EXPIRY))

class DeviceTest(TestCase):
    
    factory = RequestFactory()
    
    def setUp(self):
        self.middleware = DeviceMiddleware()
        
    def test_new_visitor(self):
        request = self.factory.get('/')
        self.middleware.process_request(request)
        assert hasattr(request,'affinity')
        assert hasattr(request,'affinity_access')
        assert request.affinity.generated
        assert request.affinity_access.generated
        assert request.affinity.changed
        assert request.affinity_access.changed
        
        response = HttpResponse('')
        r2 = self.middleware.process_response(request,response)
        assert isinstance(r2,HttpResponse)
        cookie_output = response.cookies.output()
        m = AFFINITY_COOKIE_PATTERN.match(cookie_output)
        assert request.affinity.encoded == m.group('affinity').split(":")[1], "Affinity cookie doesn't match encoded affinity"
        assert len(request.affinity.encoded) == 36, "new affinity should be 36 characters"
        assert m.group("domain") == "test.local", "new affinity should have 'test.local' as the cookie domain"
        
        #TODO affinity_access
    
    def no_test_new_visitor(self):
        lr = LastRequestMiddleware()
        c = Client(middleware_instances = [lr])
        response = c.get('/')
        cookie_output = response.cookies.output()
        m = AFFINITY_COOKIE_PATTERN.match(cookie_output)
        affinity = lr.request.affinity
        assert affinity.encoded == m.group('affinity'), "Affinity cookie doesn't match encoded affinity"
        assert affinity.new and affinity.changed, "A new affinity wasn't created"
        KNOWN.add(affinity.encoded)
        assert lr.request.affinity.extract_ip4() == "127.0.0.1", "Affinity is not tied to local host"
        assert len(affinity.encoded) == 92, "new affinity should be 92 characters"
        assert str(affinity).startswith('2002000000000000000000007f000001'), "new affinity should have 127.0.0.1 as ip address"
        
    def no_test_different_ip(self):
        c = Client(REMOTE_ADDR='127.0.0.2',HTTP_HOST="test.local")
        response = c.get('/')
        cookie_output = response.cookies.output()
        m = AFFINITY_COOKIE_PATTERN.match(cookie_output)
        domain = m.group('domain')
        affinity = m.group('affinity')
        assert domain == "test.local", "new affinity should have 'test.local' as the cookie domain"
        assert affinity.startswith('2002000000000000000000007f000002'), "new affinity should have 127.0.0.2 as ip address"
