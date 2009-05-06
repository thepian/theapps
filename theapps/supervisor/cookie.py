import re
from hashlib import sha1
import hmac

from django.core.exceptions import SuspiciousOperation

class CookieSigner(object):
    """
    Used to store
     * Device affinity
     * Last user
     * Authenticated user
     
    You can set 'value' explicitly before calling output
    """
    
    max_age = None
    expires = None
    path = '/'
    domain = None
    default_domain = None
    secure = None

    split_regex = re.compile(r'(?:([0-9a-f]+):)?(.*)')
    join_template = "%s:%s"

    def __init__(self,name,constructor,get_secret,message_envelope="%(key)s:%(value)s"):
        """
        constructor - Constructor function for value I.E. Identity(**kwargs)
        get_secret - Method to be provide the hash secret I.E. get_secret(key,value)
        """
        self.name = name
        self.constructor = constructor
        self.get_secret = get_secret
        self.message_envelope = message_envelope
        
    def _get_digest(self, key, value, secret,additional):
        d = dict(additional,key=key,value=value)
        return hmac.new(secret, self.message_envelope % d, sha1).hexdigest()
        
    def input(self,cookies,additional={}):
        """Fetch value from a cookies dictionary, and additional contructor/digest parameters
        
        @returns Value made with constructor otherwise None
        """
        cookie = cookies.get(self.name)
        if cookie:
            bits = self.split_regex.match(cookie).groups()
            bits = cookie.split(":")
            if len(bits) is not 2 or not bits[0]:
                raise SuspiciousOperation("Cookie '%s' is not signed" % self.name)
            signature, unsigned_value = bits
            value = self.constructor(encoded=unsigned_value,**additional)
            secret = self.get_secret(self.name,value)
            if self._get_digest(self.name, unsigned_value, secret, additional) != signature:
                raise SuspiciousOperation("Cookie '%s' is incorrectly signed" % self.name)
            return value
        return None
        
    def output(self,response,value, max_age=None, expires=None, path=None, domain=None, secure=None,additional={}):
        if value:
            value_part = value.encoded
            get_secret = self.get_secret
            #SignedCookie.get_secret(1,2)
            secret = get_secret(self.name,value)                        
            encoded = self.join_template % (self._get_digest(self.name,value_part,secret,additional),value_part) 
            response.set_cookie(self.name, value=encoded, 
                max_age=max_age or self.max_age, 
                expires=expires or self.expires, 
                path=path or self.path, 
                domain=domain or self.domain, 
                secure=secure or self.secure)
            