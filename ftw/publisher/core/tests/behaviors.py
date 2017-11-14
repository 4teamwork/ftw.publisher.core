from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from ftw.referencewidget.sources import ReferenceObjSourceBinder
from ftw.referencewidget.widget import ReferenceWidgetFactory
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface


class IDataGridRow(model.Schema):
    label = schema.TextLine(
        title=u'Label',
        default=u'I am the default label',
    )

    directives.widget(link=ReferenceWidgetFactory)
    link = RelationChoice(
        title=u'Link',
        source=ReferenceObjSourceBinder(),
        required=False,
    )


class IDataGridFieldExample(Interface):
    """Demo behavior containing a DataGridField.
    """
    form.widget('the_data_grid', DataGridFieldFactory, allow_reorder=True)
    the_data_grid = schema.List(
        title=u'The Data Grid',
        value_type=DictRow(title=u'the_data_grid_row', schema=IDataGridRow),
        required=False,
        missing_value=[],
    )


alsoProvides(IDataGridFieldExample, IFormFieldProvider)
