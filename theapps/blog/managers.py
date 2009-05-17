from django.db.models import Manager
from datetime import datetime

class AuthorManager(Manager):
    
    def create_from_user(self,user):
        author = self.model()
        author.id = user.id
        author.name = user.get_full_name() or 'no name'
        #TODO author.area = pick_area(request.geo)
        author.save()
        print 'creating new author for current user'
        return author
        
    def get_or_create_from_user(self,user):
        try:
            author = self.filter(id=user.id).get()
            print 'found current user as author'
        except self.model.DoesNotExist:
            author = self.create_from_user(user)
    

class PublishedManager(Manager):
    """Returns published posts that are not in the future."""
    def __init__(self, *args, **kwargs):
        self.filter_dict = dict(status__gte=2, publish__lte=datetime.now()) #TODO use callable?
        super(PublishedManager, self).__init__(*args, **kwargs)
    
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(**self.filter_dict)
    
    def published(self):
        return self.get_query_set().filter(**self.filter_dict)
        
    def tagged(self, tag_instance):
        """
        Returns a QuerySet for a tag
        """
        from theapps.tagging.models import TaggedItem
        return TaggedItem.objects.get_by_model(self.get_query_set(),tag_instance)