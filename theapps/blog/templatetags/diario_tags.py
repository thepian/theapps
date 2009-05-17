# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------------
#
#  Copyright (c) 2007, 2008 Guilherme Mesquita Gondim
#
#  This file is part of django-diario.
#
#  django-diario is free software under terms of the GNU General
#  Public License version 3 (GPLv3) as published by the Free Software
#  Foundation. See the file README for copying conditions.
#


"""
The ``diario.templatetags.diario_tags`` module defines a number of
template tags which may be used to work with entries and your
comments.

To access django-diario template tags in a template, use the {% load %}
tag::

    {% load django_tags %}
"""

from django import template
from django.conf import settings
from django.contrib.comments.models import FreeComment
from diario.models import Entry


register = template.Library()


class EntriesNode(template.Node):
    def __init__(self, start, stop, var_name):
        self.start, self.stop, self.var_name = int(start), int(stop), var_name

    def render(self, context):
        context[self.var_name] = list(Entry.published_on_site.all()[self.start-1:self.stop])
        return ''

def do_get_diario_entries(parser, token):
    """
    NOTE: This method is deprecated, use do_get_diario_entry_list instead.

    Fetch entries on a range and populates the template context with
    a variable containing that value, whose name is defined by the 'as'
    clause.

    Syntax::

        {% get_diario_entries [start] to [end] as [var_name] %}

    Example usage to get latest entries::

        {% get_diario_entries 1 to 10 as latest_entries %}

    To get old entries::

        {% get_diario_entries 11 to 20 as old_entries %}

    Note: The end point is not omitted like in python range().
    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError, "'%s' tag takes six arguments" % bits[0]
    if bits[2] != 'to':
        raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'to'" % bits[0]
    if bits[4] != 'as':
        raise template.TemplateSyntaxError, "Fourth argument to '%s' tag must be 'as'" % bits[0]
    import warnings
    warnings.warn("get_diario_entries template tag is deprecated. Use get_diario_entry_list instead.", DeprecationWarning)
    return EntriesNode(bits[1], bits[3], bits[5])


class MonthListNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = list(Entry.published_on_site.dates("pub_date", "month", order="DESC"))
        return ''

def do_get_diario_month_list(parser, token):
    """Gets month list that have entries and populates the template context
    with a variable containing that value, whose name is defined by the 'as'
    clause.

    Syntax::

        {% get_diario_month_list as [var_name] %}

    Example usage::

        {% get_diario_month_list as archive %}

        {% get_diario_month_list as blog_months %}
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError, "'%s' tag takes three arguments" % bits[0]
    if bits[1] != 'as':
        raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % bits[0]
    return MonthListNode(bits[2])


class EntryListNode(template.Node):
    def __init__(self, num, var_name, start=0):
        try:
            self.start = int(start)
        except ValueError:
            self.start =  template.Variable(start)
        self.num = int(num)
        self.var_name = var_name

    def render(self, context):
        if type(self.start) != int:
            try:
                self.start =  int(self.start.resolve(context))
            except template.VariableDoesNotExist:
                return ''
        context[self.var_name] = Entry.published_on_site.all()[self.start:][:self.num]
        return ''

def do_get_diario_entry_list(parser, token):
    """
    Gets entries list and populates the template context with a variable
    containing that value, whose name is defined by the 'as' clause.

    Syntax::

        {% get_diario_entry_list [num] (from the [start]) as [var_name] %}

    Example usage to get latest entries::

        {% get_diario_entry_list 10 as latest_entries %}

    To get old entries::

        {% get_diario_entry_list 10 from the 10 as old_entries %}

    To get previous entries from the last entry on page with ``last_on_page``
    context variable provided by ``object_list``, do::

        {% get_diario_entry_list 10 from the last_on_page as old_entries %}

    Note: The start point is omitted.
    """
    bits = token.contents.split()
    if len(bits) == 4:
        if bits[2] != 'as':
            raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'as'" % bits[0]
        return EntryListNode(bits[1], bits[3])
    if len(bits) == 7:
        if bits[2] != 'from' or bits[3] != 'the':
            raise template.TemplateSyntaxError, "Third and fourth arguments to '%s' tag must be 'from the'" % bits[0]
        if bits[5] != 'as':
            raise template.TemplateSyntaxError, "Fifth argument to '%s' tag must be 'as'" % bits[0]
        return EntryListNode(bits[1], bits[6], bits[4])
    else:
        raise template.TemplateSyntaxError, "'%s' tag takes three or seven arguments" % bits[0]


class CommentListNode(template.Node):
    def __init__(self, num, var_name, start=0, free=True):
        try:
            self.start = int(start)
        except ValueError:
            self.start =  template.Variable(start)
        self.num = int(num)
        self.var_name = var_name
        self.free = free

    def render(self, context):
        if type(self.start) != int:
            try:
                self.start =  int(self.start.resolve(context))
            except template.VariableDoesNotExist:
                return ''
        get_list_function = self.free and FreeComment.objects.filter
        kwargs = {
            'is_public': True,
            'site__pk': settings.SITE_ID,
            'content_type__app_label__exact': 'diario',
            'content_type__model__exact': 'entry',
        }
        comment_list = get_list_function(**kwargs).select_related()
        context[self.var_name] = comment_list[self.start:][:self.num]
        return ''

def do_get_diario_free_comment_list(parser, token):
    """
    Gets Diário's FreeComment list and populates the template context with a
    variable containing that value, whose name is defined by the 'as' clause.

    Syntax::

        {% get_diario_free_comment_list [num] (from the [start]) as [var_name] %}

    Example usage to get latest comments::

        {% get_diario_free_comment_list 10 as latest_diario_comments %}

    To get old comments::

        {% get_diario_free_comment_list 10 from the 10 as old_comments %}

    To get previous comments from the last comment on page with
    ``last_on_page`` context variable provided by ``object_list``, do::

        {% get_diario_free_comment_list 10 from the last_on_page as old_comments %}

    Note: The start point is omitted.
    """
    bits = token.contents.split()
    if len(bits) == 4:
        if bits[2] != 'as':
            raise template.TemplateSyntaxError, "Second argument to '%s' tag must be 'as'" % bits[0]
        return CommentListNode(bits[1], bits[3], free=True)
    if len(bits) == 7:
        if bits[2] != 'from' or bits[3] != 'the':
            raise template.TemplateSyntaxError, "Second and third arguments to '%s' tag must be 'from the'" % bits[0]
        if bits[5] != 'as':
            raise template.TemplateSyntaxError, "Fifth argument to '%s' tag must be 'as'" % bits[0]
        return CommentListNode(bits[1], bits[6], bits[4], free=True)
    else:
        raise template.TemplateSyntaxError, "'%s' tag takes three or six arguments" % bits[0]


register.tag('get_diario_entries', do_get_diario_entries) # deprecated
register.tag('get_diario_entry_list', do_get_diario_entry_list)
register.tag('get_diario_free_comment_list', do_get_diario_free_comment_list)
register.tag('get_diario_month_list', do_get_diario_month_list)
