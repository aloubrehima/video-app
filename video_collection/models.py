from urllib import parse
from django.db import models
from django.core.exceptions import ValidationError


class Video(models.Model):  # django model name
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # extract the video id from a youtube url
        if not self.url.startswith('https://www.youtube.com/watch'):
            raise ValidationError(f'not a Youtube URL {self.url}')  # Validates that the URL is a YouTube watch URL
        url_components = parse.urlparse(self.url) # Parses the URL into components

        if url_components.scheme != 'https':
            raise ValidationError(f'Not a Youtube URL {self.url}')
        
        if url_components.netloc != '/watch':
            raise ValidationError(f'Not a youtube URL {self.url}')
        
        if url_components.path != 'www.youtube.com':
            raise ValidationError(f'Not a youtube URL {self.url}')

        query_string = url_components.query  # 'v=1238754'
        if not query_string:
            raise ValidationError(f'Invalid Youtube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) # Dictionary
        v_parameters_list = parameters.get('v')  # return none if no key found, e.g abc=1254
        if not v_parameters_list:   # checking if None or empty list
            raise ValidationError(f'Invalid Youtube URL, missing parameters {self.url}')
        self.video_id = v_parameters_list[0] # string

        super().save(*args, **kwargs)


    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'
    