from django.conf import settings
        
class RuleList(object):
    def __init__(self,*values):
        self.data = []
        self.concat(values)
        
    def concat(self,values):
        self.data.extend(values)
    
    def append(self,value):
        self.data.append(value)
        
    def count(self):
        return len(self.data)
    __len__ = count
    
    def __getitem__(self, key):
        return self.data[key]
        
class RobotRuleManager(object):
    
    rules = RuleList()
    
    def filter(self,sites):
        print "getting rules"
        rl = RuleList()
        for rule in self.rules.data:
            #TODO support sites as a tuple of strings
            print repr(rule)
            print repr(sites)
            if len(rule.sites) == 0 or sites in rule.sites:
                rl.append(rule)
        return rl
        
    def queue(self,rule):
        self.rules.append(rule)
        
    def iscompatible(self,rule):
        if hasattr(rule,"sites") and hasattr(rule,"robot") and hasattr(rule,"pattern"):
            return True
        # consider more requirements
        return False
        
    
class RobotRule(object):
    objects = RobotRuleManager()
    
    def __init__(self,robot,sites,pattern=None,allow=False,disallow=False):
        self.pattern = pattern
        self.allow = allow
        self.disallow = disallow
        self.robot = robot
        self.sites = sites or ()
        
    def __repr__(self):
        return ' '.join(
            ((self.allow and "Allow: " or "")+(self.disallow and "Disallow: " or "")+ (self.pattern or "-undefined-"),
            'User-agent: '+repr(self.robot),
            repr(self.sites))
            )
            
    def get_expanded(self,pattern):
        """
        Make a list of rules one per robot
        pattern is a regex!!!!!!!!!!! not a robots type pattern
        """
        from thepian.utils.urls import regex2robots

        if isinstance(self.robot,basestring):
            return (RobotRule(self.robot, self.sites, pattern="/"+regex2robots(pattern), allow=self.allow, disallow=self.disallow),)
        else:
            return [RobotRule(robot, self.sites, pattern="/"+regex2robots(pattern), allow=self.allow, disallow=self.disallow) for robot in self.robot]
