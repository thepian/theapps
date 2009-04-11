from thepian.tickets import Identity
#from django.db.models.Model import DoesNotExist

class UserData(object):
    def __init__(self,affinity=None,user=None,encoded=None):
        self.data = {}
        if encoded:
            self._decode(encoded)

        if user:
            if user.is_authenticated():
                if hasattr(user,'apply_userdata'):
                    user.apply_userdata(self.data)
                else:
                    self.data['username'] = user.username
                    self.data['name'] = user.get_full_name()
                try:
                    profile = user.get_profile()
                    if hasattr(profile,'apply_userdata'):
                        profile.apply_userdata(self.data)
                    else:
                        self.data['public_name'] = profile.name
                        self.data['nick'] = profile.nick
                        self.data['area'] = profile.area
                except:
                    self.data['public_name'] = user.get_full_name()
                    self.data['nick'] = user.username
                    self.data['area'] = '' #TODO default
                self.data['locale'] = ''
                self.data['timezone'] = ''
                self.data['last_change'] = 'millis'
                auth = Identity(encoded=user.id).encoded #TODO which secret?
                self.data['user_auth'] = auth
                self.data['any_auth'] = auth # user
            else:
                self.data['any_auth'] = affinity and affinity.encoded or '' # device
                
    def _decode(self,encoded):
        self.data = {}
        for entry in encoded.split('\x1E'):
            try:
                se = entry.split('\x1F')
                if len(se) == 2:
                    self.permissions[se[0]] = se[1]
            except:
                pass

    def _encode(self):
        r = []
        for key in self.data:
            r.append('\x1F'.join((key,self.data[key])))
        return '\x1E'.join(r)
    encoded = property(_encode)
    
    def as_dl(self):
        return u"".join([u"<dt>%s</dt><dd>%s</dd>" % (n,self.data[n]) for n in self.data])


    
                