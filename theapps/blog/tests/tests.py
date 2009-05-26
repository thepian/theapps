"""
>>> import datetime, calendar
>>> from django.conf import settings
>>> settings.ROOT_URLCONF
'urls'
>>> from django.core.urlresolvers import reverse
>>> reverse('blog_detail',args=('2009','jan','slug'))
'/blog/2009/jan/slug/'

>>> from django.test import Client
>>> from theapps.blog.models import Post, Category, Author
>>> import datetime

>>> client = Client()

>>> response = client.get('/blog/')
>>> response.status_code
200

>>> response = client.get('/blog/categories/')
>>> response.status_code
200

>>> category = Category(title='Django', slug='django')
>>> category.save()
>>> category.get_absolute_url()
'/blog/categories/django/'
>>> response = client.get(category.get_absolute_url())
>>> response.status_code
200

>>> author = Author(id="dummy_id",name="Peter Pan")
>>> author.save()


>>> post = Post(title='My post', slug='my-post', tease_source='Lorem ipsum dolor', body_source='Lorem ipsum dolor sit amet', status=2, publish=datetime.datetime.now(), author=author, category=category)
>>> post.save()
>>> post.get_absolute_url()
'/blog/2009/may/my-post/'
>>> Post.objects.published()[:1]
[<Post: My post>]
>>> Post.objects.published().filter(slug__exact='my-post')
[<Post: My post>]

>>> now = datetime.datetime.now()
>>> date = datetime.date(now.year,now.month,now.day)
>>> date_to = datetime.date(now.year,now.month,calendar.monthrange(now.year,now.month)[1])
>>> Post.objects.published().filter(slug__exact='my-post', publish__range=(datetime.datetime.combine(date, datetime.time.min), datetime.datetime.combine(date_to, datetime.time.max)))
[<Post: My post>]

>>> response = client.get(post.get_absolute_url())
>>> response.status_code
200

>>> published = Post.objects.published()
>>> was_len = len(published)
>>> post = Post(title='My post', slug='my-post', tease_source='Lorem ipsum', body_source='Lorem ipsum dolor', status=2, publish=datetime.datetime.now(), author=author, category=category)
>>> post.save()
>>> len(published.filter()) - was_len
0

The call above should return 1

>>> response = client.get('/blog/2009/')
>>> response.status_code
200

>>> response = client.get('/blog/2009/may/')
>>> response.status_code
200

"""