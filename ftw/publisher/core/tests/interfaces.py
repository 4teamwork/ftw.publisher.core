from plone.directives import form
from plone.namedfile.field import NamedBlobFile


class IFoo(form.Schema):
    pass


class IFileSchema(form.Schema):

    form.primary('file')
    file = NamedBlobFile(title=u'File')
