from plone.directives import form
from plone.namedfile.field import NamedFile


class IFoo(form.Schema):
    pass


class IFileSchema(form.Schema):

    form.primary('file')
    file = NamedFile(title=u'File')
