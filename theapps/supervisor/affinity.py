import uuid
from django.conf import settings

def get_secret(key,identity,context):
    return settings.SECRET_KEY

class Affinity(object):
    """ Object to hold encoded and decoded forms of a User / Device Affinity. It contains original remote addr, first time, shard name, affinity number 
    """
    generated = False
    changed = False
    
    def __init__(self,meta=None,encoded=None,**kwargs):
        """
        meta - META dictionary from the request object
        encoded - Affinity as an encoded string
        """
        if encoded:
            self.uuid = uuid.UUID(encoded)
        else:
            self.generated = True
            self.changed = True
            self.uuid = uuid.uuid1()
            
    def __repr__(self):
        return self._encoded()
            
    def _encoded(self):
        return hasattr(self,'uuid') and str(self.uuid) or ''
    encoded = property(_encoded)
        
class AffinityAccess(object):
    def __init__(self,meta=None,encoded=None,**kwargs):
        if encoded:
            self.__encoded = encoded
        else:
            self.generated = True
            self.changed = True
            self.__encoded = ''

    def __repr__(self):
        return self._encoded()

    def _encoded(self):
        return self.__encoded
    encoded = property(_encoded)
