import uuid
import string
from django.db import models


class Url (models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=200)
    shortened_url = models.CharField(max_length=10, unique=True, db_index=True, default='')
    visits = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    last_access_date = models.DateTimeField(null=True)
    reset_date = models.DateTimeField(null=True)
    enabled = models.BooleanField(default=True)
    disabled_date = models.DateTimeField(null=True)

    def generate_short_url(self, id=None):
        if id is None:
            id = self.id.node
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        length = len(chars)
        encode = ""
        while id > 0:
            encode = chars[id % length] + encode
            id = id // length
        return encode

    @classmethod
    def create(cls, url):
        u = cls(url=url)
        u.shortened_url = u.generate_short_url()
        return u
