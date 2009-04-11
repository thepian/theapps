from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from fields import IdentityField, UuidField

class AccessTicketManager(models.Manager):

    def grant_access(self,ticket_id,affinity,user,affinity_access,user_access):
        """
        scenarios:
        unknown ticket
        ticket not available yet
        ticket used up
        """
        try:
            ticket = self.get(pk=ticket_id)
        except AccessTicket.DoesNotExist:
            #TODO log failure & penalise device/user with future delays
            raise
        #TODO throttle requests from same ip
        if ticket.uses <= 0:
            raise AccessTicket.DoesNotExist
        if user_access and user_access.is_active() and ticket.apply_to_user:
            #TODO page vs tree access already enabled
            if user_access.check_access(ticket.level,ticket.type,ticket.domain,ticket.path):
                return
            granted = ticket.grant_affinity_access(affinity,user)
            #TODO only add to cookie if now >= granted.use_from
            user_access.grant_access(ticket.level,ticket.type,ticket.domain,ticket.path,granted.use_until,page=ticket.single_page)    
        elif ticket.apply_to_affinity:    
            if affinity_access.check_access(ticket.level,ticket.type,ticket.domain,ticket.path):
                return
            granted = ticket.grant_affinity_access(affinity,user)
            #TODO only add to cookie if now >= granted.use_from
            affinity_access.grant_access(ticket.level,ticket.type,ticket.domain,ticket.path,granted.use_until,page=ticket.single_page)    
            return ticket
        raise AccessTicket.DoesNotExist #TODO pick better exception

"""
access_list - client cookie - json list of urls and the use period
access_* - server cookie - page name and hash to prove access
"""

ACCESS_TYPES = (
    ("http","Web pages"),("db","Database")
    )
    
ACCESS_LEVEL = (
    ("regular","Regular"),
    ("alpha","Alpha Area"),
    ("confidential","Confidential Area"),
    ("super","Superuser"),
    )
    
class AccessTicket(models.Model):
    id = UuidField(_('accessid'), auto_generate=True, primary_key=True, 
        help_text=_("Base64 unique id"))
    type = models.CharField(choices=ACCESS_TYPES,default="http",max_length=10)
    level = models.CharField(choices=ACCESS_LEVEL,default="alpha",max_length=10)
    domain = models.CharField(max_length=50)
    path = models.CharField(max_length=200)
    single_page = models.BooleanField(default=False)
    apply_to_affinity = models.BooleanField(default=True)
    apply_to_user = models.BooleanField(default=True)
    enter_from = models.DateTimeField(default=datetime.min)
    enter_until = models.DateTimeField(default=datetime.max)
    use_before = models.DateTimeField(default=datetime.max, help_text="Use the ticket before this time")
    period = models.FloatField(null=True,blank=True,default=None,
        help_text="Number of seconds a used ticket remains valid. If None unlimited period")
    uses = models.IntegerField(default=1)
    entry_path = models.CharField(max_length=200,help_text=_("When entering redirect here"), default="/")
    
    objects = AccessTicketManager()
    
    def __unicode__(self):
        return u'%s %s: %s' % (self.type,self.level,self.path)
        
    def grant_affinity_access(self,affinity,user):
        assert self.uses > 0
        granted = UsedTicket()
        granted.ticket = self
        granted.device = affinity.without_checksum
        if user.id:
            granted.userid = user.id
        granted.use_from = max(datetime.now(),self.enter_from)
        if self.period:
            granted.use_until = max(self.enter_until,granted.use_from + self.period * 1000)
        else:
            granted.use_until = self.enter_until
        granted.save()
        self.uses -= 1
        self.save()
        
        return granted
    
class UsedTicket(models.Model):
    ticket = models.ForeignKey(AccessTicket)
    device = IdentityField(_('user device'),db_index=True)
    userid = IdentityField(_('user id'),db_index=True)
    use_from = models.DateTimeField()
    use_until = models.DateTimeField()
    