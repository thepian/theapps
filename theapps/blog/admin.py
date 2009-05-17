from django import forms
from django.contrib import admin
from models import Category, Post, Author

from theapps.media.widgets import MediaAssetInput

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('title',)}

admin.site.register(Category, CategoryAdmin)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name','id')
    
admin.site.register(Author, AuthorAdmin)


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        
    def __init__(self, *args, **kwargs):
        super(PostModelForm, self).__init__(*args, **kwargs)
        #self.fields['ext_image_url'].widget = MediaAssetInput(attrs={'extra':'1'})
        
class PostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'get_mini_tease', 'publish', 'author', 'status')
    list_filter   = ('publish', 'category', 'author', 'status')
    search_fields = ('title', 'body')
    prepopulated_fields = { 'slug': ('title',)}
    radio_fields = { 'status' : admin.HORIZONTAL, 'markup': admin.HORIZONTAL } # ? = admin.VERTICAL
    form = PostModelForm
    
    def save_model(self, request, obj, form, change):
        if not hasattr(obj,'author') or  not obj.author:
            obj.author = Author.objects.get_or_create_from_user(request.user)
        super(PostAdmin,self).save_model(request,obj,form,change)
            
admin.site.register(Post, PostAdmin)

