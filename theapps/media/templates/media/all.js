var Entity, Asset;

(function(_Entity,_Asset){
    
function Entity(raw) {
    for(var n in raw) this[n] = raw[n];
}

Entity.prototype.get_absolute_path = function() {
    return "http://%s%s" % (this.domain,this.path);
};

Entity.prototype.objects = Entity.objects = {
    'all' : {},
    'update' : function(all) {
        self.all = all;
    },
    'get' : function(path) {
        return Entity(this.all[path]);
    }
};

function Asset(raw) {
    for(var n in raw) this[n] = raw[n];
}

Asset.prototype.get_absolute_path = function() {
    return "http://%s%s" % (this.domain,this.path);
};

Asset.prototype.objects = Asset.objects = {
    'all': {},
    'update' : function(all) {
        self.all = all;
    },
    'get' : function(path) {
        return Asset(this.all[path]);
    }
};

if (!_Entity) _Entity = Entity;
if (!_Asset) _Asset = Asset;
if (!window.Entity) window.Entity = Entity;
if (!window.Asset) window.Asset = Asset;
})(Entity,Asset);

Entity.objects.update({{ entities }});

Asset.objects.update({{ paths }});