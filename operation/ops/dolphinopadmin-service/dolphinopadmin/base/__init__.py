from django.db import models


class DefaultManager(models.Manager):

    def get_query_set(self):
#        query_set = super(DefaultManager, self).get_query_set().filter(hided=False)
        query_set = super(DefaultManager, self).get_query_set().all()
        return query_set


class CustomManager(DefaultManager):

    """             
    Custom manager. 
    options: queryset filter options
    """

    def __init__(self, options={}):
        self.options = options
        super(CustomManager, self).__init__()

    def get_query_set(self):
        query_set = super(CustomManager,
                          self).get_query_set().filter(**self.options)
        return query_set
