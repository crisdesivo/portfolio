from .models import RecursiveList

class RecursiveListPY:
    def __init__(self, id):
        self.id = id
        self.title = RecursiveList.objects.get(id=id).title
        self.description = RecursiveList.objects.get(id=id).description
        self.parent = RecursiveList.objects.get(id=id).parent
        self.children = RecursiveList.objects.get(id=id).children.all()

        self.collapsed = True

    def generate_html(self):
        html = '<li>'
        html += self.title
        if self.children and not self.collapsed:
            html += '<ul>'
            for child in self.children:
                html += RecursiveListPY(child.id).generate_html()
            html += '</ul>'
            html += '</li>'
        return html