from django.db import models

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    markdown = models.TextField(blank=True)
    link = models.URLField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    