import mock
    
from django.test import TestCase, Client

from django.http import HttpRequest, HttpResponse
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from theapps.supervisor.cookie import CookieSigner

class SillyIdentity(object):
    def __init__(self,meta=None,encoded=None,**kwargs):
        self.encoded = encoded
        self.kwargs = kwargs
        
    def __repr__(self):
        return "Silly<%s>" % self.encoded
        
def get_secret(key,identity,context):
    return "not very secret"#settings.SECRET_KEY
    
"""
fudge.clear_expectations()
fudge.clear_calls()
response = (fudge.Fake('response')
                .expects('set_cookie')
                .with_args(
                   "checked",
                   "444400ccc469e0019ccac74d45ea0c6d2d6a94bca2e9",
                   self.signed.max_age,
                   self.signed.expires,
                   self.signed.path,
                   self.signed.domain,
                   self.signed.secure))
self.signed.output(response)
fudge.verify()
"""    
    
class CookieTest(TestCase):
    
    client = Client(REMOTE_ADDR='127.0.0.1',HTTP_HOST="test.local")

    def setUp(self):
        self.checked_signer = CookieSigner("checked",constructor=SillyIdentity,get_secret=get_secret)
        self.extra_signer = CookieSigner("extra",constructor=SillyIdentity,get_secret=get_secret,message_envelope="%(key)s:%(value)s:%(tail)s")
        
    def test_blank_cookie(self):
        response = HttpResponse('')
        self.checked_signer.output(response,None)
        for cookie in str(response.cookies).splitlines():
            assert not cookie.startswith('Set-Cookie: checked=')
        
    def test_input_cookie(self):
        try:
            value = self.checked_signer.input({"checked" : "abcdef"})
        except SuspiciousOperation:
            pass
        else:
            assert False, "Unsigned cookie did not raise exception"
            
        try:
            value = self.checked_signer.input({"checked" : "01ccc469e0019ccac74d45ea0c6d2d6a94bca2e9:4444"})
        except SuspiciousOperation:
            pass
        else:
            assert False, "Mis-signed cookie did not raise exception"

        try:
            value = self.checked_signer.input({"checked" : ":4444"})
        except SuspiciousOperation:
            pass
        else:
            assert False, "Blank signed cookie did not raise exception"

        value = self.checked_signer.input({"checked" : "00ccc469e0019ccac74d45ea0c6d2d6a94bca2e9:4444"})
        assert value.encoded == "4444"

    def test_input_cookie_additional(self):
        value = self.checked_signer.input({"checked" : "00ccc469e0019ccac74d45ea0c6d2d6a94bca2e9:4444"}, additional=dict(extra1="extra1",extra2="extra2"))
        assert value.encoded == "4444"
        assert "extra1" in value.kwargs
        assert value.kwargs["extra1"] == "extra1"
        assert "extra2" in value.kwargs
        assert value.kwargs["extra2"] == "extra2"
        
    def test_new_cookie(self):
        value = SillyIdentity(encoded="4444")
        response = HttpResponse('')
        self.checked_signer.output(response,value)
        assert 'Set-Cookie: checked="00ccc469e0019ccac74d45ea0c6d2d6a94bca2e9:4444"; Path=/' in response.cookies.output().splitlines()

        value = SillyIdentity(encoded="4444")
        response = HttpResponse('')
        self.checked_signer.output(response,value, path="/nowhere")
        assert 'Set-Cookie: checked="00ccc469e0019ccac74d45ea0c6d2d6a94bca2e9:4444"; Path=/nowhere' in response.cookies.output().splitlines()

        value = SillyIdentity(encoded="4444")
        response = HttpResponse('')
        self.checked_signer.output(response,value, domain="www.test.local")
        assert 'Set-Cookie: checked="00ccc469e0019ccac74d45ea0c6d2d6a94bca2e9:4444"; Domain=www.test.local; Path=/' in response.cookies.output().splitlines(), response.cookies

    def test_new_cookie_tail(self):
        value = SillyIdentity(encoded="4444")
        response = HttpResponse('')
        self.extra_signer.output(response,value,additional=dict(tail="TAIL"))
        assert 'Set-Cookie: extra="7afbf24a1d54404e4001cc345a5ec6882f4eed96:4444"; Path=/' in response.cookies.output().splitlines()

        response = HttpResponse('')
        self.extra_signer.output(response,value,additional=dict(tail="ANOTHER_TAIL"))
        assert 'Set-Cookie: extra="d60ce623f1855e1903afea0a5a5d779894870e4a:4444"; Path=/' in response.cookies.output().splitlines()

    #TODO consider if special Error should be raised if message_envelope relies on non-existing additional value

    def test_delete_cookie(self):
        pass
        
    def no_test_client(self):
        c = Client(REMOTE_ADDR='127.0.0.2',HTTP_HOST="test.local")
        response = c.get("/")
        
        value = self.checked_signer.input(request.COOKIES)
