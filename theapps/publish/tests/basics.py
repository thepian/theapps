# -*- coding: utf-8 -*-
tests = r"""
>>> import os
>>> from django import forms
>>> from django.conf import settings
>>> from theapps.publish.forms import TagField
>>> from theapps.publish.tests.models import Article, Link, Perch, Parrot, Tag, FormTest
>>> from theapps.publish.tagging import parse_tag_input 

#############
# Utilities #
#############

# Tag input ###################################################################

# Simple space-delimited tags
>>> parse_tag_input('one')
[u'one']
>>> parse_tag_input('one two')
[u'one', u'two']
>>> parse_tag_input('one two three')
[u'one', u'three', u'two']
>>> parse_tag_input('one one two two')
[u'one', u'two']

# Comma-delimited multiple words - an unquoted comma in the input will trigger
# this.
>>> parse_tag_input(',one')
[u'one']
>>> parse_tag_input(',one two')
[u'one two']
>>> parse_tag_input(',one two three')
[u'one two three']
>>> parse_tag_input('a-one, a-two and a-three')
[u'a-one', u'a-two and a-three']

# Double-quoted multiple words - a completed quote will trigger this.
# Unclosed quotes are ignored.
>>> parse_tag_input('"one')
[u'one']
>>> parse_tag_input('"one two')
[u'one', u'two']
>>> parse_tag_input('"one two three')
[u'one', u'three', u'two']
>>> parse_tag_input('"one two"')
[u'one two']
>>> parse_tag_input('a-one "a-two and a-three"')
[u'a-one', u'a-two and a-three']

# No loose commas - split on spaces
>>> parse_tag_input('one two "thr,ee"')
[u'one', u'thr,ee', u'two']

# Loose commas - split on commas
>>> parse_tag_input('"one", two three')
[u'one', u'two three']

# Double quotes can contain commas
>>> parse_tag_input('a-one "a-two, and a-three"')
[u'a-one', u'a-two, and a-three']
>>> parse_tag_input('"two", one, one, two, "one"')
[u'one', u'two']

# Bad users! Naughty users!
>>> parse_tag_input(None)
[]
>>> parse_tag_input('')
[]
>>> parse_tag_input('"')
[]
>>> parse_tag_input('""')
[]
>>> parse_tag_input('"' * 7)
[]
>>> parse_tag_input(',,,,,,')
[]
>>> parse_tag_input('",",",",",",","')
[u',']
>>> parse_tag_input('a-one "a-two" and "a-three')
[u'a-one', u'a-three', u'a-two', u'and']



###########
# Tagging #
###########

# Basic tagging ###############################################################

>>> dead = Parrot.objects.create(state='dead')
>>> Tag.objects.update_tags(dead, 'foo,bar,"ter"')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: foo>, <Tag: ter>]
>>> Tag.objects.update_tags(dead, '"foo" bar "baz"')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'foo')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'zip')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>, <Tag: zip>]
>>> Tag.objects.add_tag(dead, '    ')
Traceback (most recent call last):
    ...
AttributeError: No tags were given: "    ".
>>> Tag.objects.add_tag(dead, 'one two')
Traceback (most recent call last):
    ...
AttributeError: Multiple tags were given: "one two".

# Note that doctest in Python 2.4 (and maybe 2.5?) doesn't support non-ascii
# characters in output, so we're displaying the repr() here.
>>> Tag.objects.update_tags(dead, 'ŠĐĆŽćžšđ')
>>> repr(Tag.objects.get_for_object(dead))
'[<Tag: \xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe\xc5\xa1\xc4\x91>]'

>>> Tag.objects.update_tags(dead, None)
>>> Tag.objects.get_for_object(dead)
[]

# Using a model's TagField
>>> f1 = FormTest.objects.create(tags=u'test3 test2 test1')
>>> Tag.objects.get_for_object(f1)
[<Tag: test1>, <Tag: test2>, <Tag: test3>]
>>> f1.tags = u'test4'
>>> f1.save()
>>> Tag.objects.get_for_object(f1)
[<Tag: test4>]
>>> f1.tags = ''
>>> f1.save()
>>> Tag.objects.get_for_object(f1)
[]

# Forcing tags to lowercase
>>> settings.FORCE_LOWERCASE_TAGS = True
>>> Tag.objects.update_tags(dead, 'foO bAr Ter')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: foo>, <Tag: ter>]
>>> Tag.objects.update_tags(dead, 'foO bAr baZ')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'FOO')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>]
>>> Tag.objects.add_tag(dead, 'Zip')
>>> Tag.objects.get_for_object(dead)
[<Tag: bar>, <Tag: baz>, <Tag: foo>, <Tag: zip>]
>>> Tag.objects.update_tags(dead, None)
>>> f1.tags = u'TEST5'
>>> f1.save()
>>> Tag.objects.get_for_object(f1)
[<Tag: test5>]
>>> f1.tags
u'test5'


"""