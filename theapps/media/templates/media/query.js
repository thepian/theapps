{% load media_assets %}

var entities;
if (entities == undefined) entities = {};
entities["{{ entity }}"] = {
    'id': "{{ entity }}",
    'base_url': "http://aj.idolyzed.local/download",
	'assets': [
	    {% for asset in assets %}'{{asset.path}}',{% endfor %}
	]
};

var assets;
if (assets == undefined) assets = {};
(function(){ 
{% for asset in assets %}
	assets['{{asset.path}}'] = { 
	            'path':'{{asset.path}}',
	            'entity':'{{asset.parent.path}}', 'name':'{{asset.caption}}', 
	            'original_category':'{{ asset.original_category }}',
	            'status':'{{asset.status}}', 'thumb_url':'{% thumbnail_url asset 75x75 %}', 
	            'still_url':'{% still_url asset 0 %}', 
	            'video_url':'{% video_url asset 320 %}' 
	        };
{% endfor %}
})();

var runs;
if (runs === undefined) runs = 0; else ++runs;

