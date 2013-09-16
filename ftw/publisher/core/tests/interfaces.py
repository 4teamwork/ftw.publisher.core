from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedFile
from plone.namedfile.field import NamedImage


class IFoo(form.Schema):
    pass


class IFileSchema(form.Schema):

    form.primary('file')
    file = NamedFile(title=u'File')


class IImageSchema(form.Schema):

    form.primary('image')
    image = NamedImage(title=u'image')


class ITextSchema(form.Schema):

    form.primary('text')
    text = RichText(title=u'Text')
