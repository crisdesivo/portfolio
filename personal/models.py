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

class RecursiveList(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    collapsed = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.title
    
    def get_children(self):
        return self.children.all()
    
    def create_child(self, title, description):
        return RecursiveList.objects.create(title=title, description=description, parent=self)