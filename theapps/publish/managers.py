from django.conf import settings
from django.db import models
from tagging import parse_tag_input

class ModelTagManager(models.Manager):

    def update_tags(self, obj, tag_names):
        """
        Update tags associated with an object.
        """
        current_tags = list(self.filter(object=obj))
        updated_tag_names = parse_tag_input(tag_names)
        if settings.FORCE_LOWERCASE_TAGS:
            updated_tag_names = [t.lower() for t in updated_tag_names]

        # Remove tags which no longer apply
        tags_for_removal = [tag.name for tag in current_tags if tag.name not in updated_tag_names]
        if len(tags_for_removal):
            self.filter(object=obj, name__in=tags_for_removal).delete()
            
        # Add new tags
        current_tag_names = [tag.name for tag in current_tags]
        for tag_name in updated_tag_names:
            if tag_name not in current_tag_names:
                tag, created = self.create(name=tag_name, object=obj)

