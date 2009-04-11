from django.test import TestCase

from django.test import Client, LastRequestMiddleware

import re
SET_COOKIE = r'Set-Cookie: %s; Domain=%s; expires=Mdy, 01-Jan-2038 00:00:00 GMT; Path=/'
COOKIE_PATTERN = re.compile(SET_COOKIE % (r'affinity=(?P<affinity>\w*)',r'(?P<domain>\w*\.local)'))

class DeviceTest(TestCase):
    
    def test_new_visitor(self):
        lr = LastRequestMiddleware()
        c = Client(middleware_instances = [lr])
        response = c.get('/')
        cookie_output = response.cookies.output()
        m = COOKIE_PATTERN.match(cookie_output)
        affinity = lr.request.affinity
        assert affinity.encoded == m.group('affinity'), "Affinity cookie doesn't match encoded affinity"
        assert affinity.new and affinity.changed, "A new affinity wasn't created"
        KNOWN.add(affinity.encoded)
        assert lr.request.affinity.extract_ip4() == "127.0.0.1", "Affinity is not tied to local host"
        assert len(affinity.encoded) == 92, "new affinity should be 92 characters"
        assert str(affinity).startswith('2002000000000000000000007f000001'), "new affinity should have 127.0.0.1 as ip address"
        
    def test_different_ip(self):
        c = Client(REMOTE_ADDR='127.0.0.2',HTTP_HOST="test.local")
        response = c.get('/')
        cookie_output = response.cookies.output()
        m = COOKIE_PATTERN.match(cookie_output)
        domain = m.group('domain')
        affinity = m.group('affinity')
        assert domain == "test.local", "new affinity should have 'test.local' as the cookie domain"
        assert affinity.startswith('2002000000000000000000007f000002'), "new affinity should have 127.0.0.2 as ip address"
