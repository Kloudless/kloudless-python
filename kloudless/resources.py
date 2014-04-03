from .util import to_datetime

import copy

class BaseResource(object):
    def __init__(self, **attributes):
        for attr in attributes:
            if attr in fields:
                
        self.attributes = attributes
        self.id = self.attributes.get('id')
        self._cached = copy.deepcopy(attributes)

        self.deserialize_timestamps()

    def deserialize_timestamps(self):
        for k in ['modified', 'created']:
            if k in self.attributes:
                self.attributes[k] = to_datetime(self.attributes[k])

    def __dict__(self):
        return self.attributes

    #def __getattr__(self, name):
    #    if self.attributes.has_key(name):
    #        return self.attributes[name]
    #    return super(BaseResource, self).__getattr__(name)
        
    #def __setattr__(self, name, value):
    #    self.attributes[name] = value
    #    return super(BaseResource, self).__setattr__(name)

    #def __delattr__(self, name):
    #    if self.attributes.has_key(name):
    #        del self.attributes[name]
    #    else:
    #        return super(BaseResource, self).__delattr__(name)

class Account(BaseResource):
    pass
