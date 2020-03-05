from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedFile
from plone.namedfile.field import NamedImage
from zope import schema


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


class IDateAndTimeSchema(form.Schema):

    form.primary('datetime')
    zope_datetime = schema.Datetime(title=u'Zope Datetime')
    datetime = schema.Datetime(title=u'Datetime')
    date = schema.Date(title=u'Date')
    time = schema.Time(title=u'Time')
