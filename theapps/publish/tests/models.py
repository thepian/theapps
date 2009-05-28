from django.db import models

from theapps.publish.models import TagBase
from theapps.publish.fields import TagField

class LinkTag(TagBase):
    object = models.ForeignKey('tests.Link',related_name="tags2")

    class Meta(TagBase.Meta):
        db_table = 'tests_link_tag'


class Link(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class ArticleTag(TagBase):
    object = models.ForeignKey('tests.Article',related_name="tags2")

    class Meta(TagBase.Meta):
        db_table = 'tests_article_tag'


class Article(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Tag(TagBase):
    object = models.ForeignKey('tests.FormTest',related_name="tags2")
    
    class Meta(TagBase.Meta):
        db_table = 'tests_tag'

class FormTest(models.Model):
    tags = TagField(Tag=Tag)
