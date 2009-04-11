from django.db import models
from thepian.tickets import Identity

def generate_identity():
    return Identity(ip4="127.0.0.1").without_checksum
    
class IdentityField(models.CharField):
    """
    optional parameters:
    auto_generate - Generate when adding, or otherwise blank
    TODO:
    auto_user_add - Sets to value to the current user identity on add. (if using formfield logic)
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 100
        kwargs['editable'] = False
        if 'auto_generate' in kwargs:
            self.auto_generate = kwargs['auto_generate']
            kwargs['default'] = generate_identity
            del kwargs['auto_generate']
        super(IdentityField, self).__init__(*args, **kwargs)
        
#    def pre_save(self, model_instance, add):
#        if self.auto_generate or not hasattr(model_instance,self.attname) or not getattr(model_instance,self.attname):
#            return Identity(ip4="127.0.0.1").without_checksum
#        else:
#           return getattr(model_instance, self.attname)


def generate_uuid4():
    import uuid,base64
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).strip('=')

# TODO http://www.davidcramer.net/code/420/improved-uuidfield-in-django.html#comment-20729
   
class UuidField(models.CharField):
    def __init__(self,*args,**kwargs):
        kwargs['max_length'] = 30
        if 'auto_generate' in kwargs:
            self.auto_generate = kwargs['auto_generate']
            kwargs['default'] = generate_uuid4
            del kwargs['auto_generate']
        super(UuidField, self).__init__(*args, **kwargs)

class UUIDField(models.CharField):
    """
        A field which stores a UUID value in hex format. This may also have
        the Boolean attribute 'auto' which will set the value on initial save to a
        new UUID value (calculated using the UUID1 method). Note that while all
        UUIDs are expected to be unique we enforce this with a DB constraint.
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, version=4, node=None, clock_seq=None, namespace=None, auto=False, name=None, *args, **kwargs):
        assert(version in (1, 3, 4, 5), "UUID version %s is not supported." % (version,))
        self.auto = auto
        self.version = version
        # Set this as a fixed value, we store UUIDs in text.
        kwargs['max_length'] = 32
        if auto:
            # Do not let the user edit UUIDs if they are auto-assigned.
            kwargs['editable'] = False
            kwargs['blank'] = True
            kwargs['unique'] = True
        if version == 1:
            self.node, self.clock_seq = node, clock_seq
        elif version in (3, 5):
            self.namespace, self.name = namespace, name
        super(UUIDField, self).__init__(*args, **kwargs)

    def _create_uuid(self):
        if self.version == 1:
            args = (self.node, self.clock_seq)
        elif self.version in (3, 5):
            args = (self.namespace, self.name)
        else:
            args = ()
        return getattr(uuid, 'uuid%s' % (self.version,))(*args)

    def db_type(self):
        return 'char'

    def pre_save(self, model_instance, add):
        """ see CharField.pre_save
        This is used to ensure that we auto-set values if required.
        """
        value = getattr(model_instance, self.attname, None)
        if not value and self.auto:
            # Assign a new value for this attribute if required.
            value = self._create_uuid()
            setattr(model_instance, self.attname, value)
        return value

    def to_python(self, value):
        if not value: return
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value

    def get_db_prep_save(self, value):
        if not value: return
        assert(isinstance(value, uuid.UUID))
        return value.hex

