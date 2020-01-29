from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zope.dottedname.resolve import resolve
import pkg_resources


"""List of candidate interface dottednames provided by objects which may belong to their parent.
The child belongs to its parent when it provides at least one of these interfaces and does not have
a workflow chain configured.

Belonging to its parent has impacts such as that it is published automatically along with the parent
and only removed when the parent is published again.
"""
BELONGS_TO_PARENT_CANDIDATES = [
    # ('pkg name', 'dottedname of interfaces'),
    ('ftw.simplelayout', 'ftw.simplelayout.interfaces.ISimplelayoutBlock'),
    ('ftw.file', 'ftw.file.interfaces.IFile'),
    ('plone.app.blob', 'plone.app.blob.interfaces.IATBlobFile'),
    ('plone.app.blob', 'plone.app.blob.interfaces.IATBlobImage'),
    ('plone.app.contenttypes', 'plone.app.contenttypes.interfaces.IFile'),
    ('plone.app.contenttypes', 'plone.app.contenttypes.interfaces.IImage'),
    ('ftw.slider', 'ftw.slider.interfaces.IPane'),
    ('Products.PloneFormGen', 'Products.PloneFormGen.interfaces.IPloneFormGenField'),
    ('Products.PloneFormGen', 'Products.PloneFormGen.interfaces.IPloneFormGenFieldset'),
    ('Products.PloneFormGen', 'Products.PloneFormGen.interfaces.IPloneFormGenActionAdapter'),
    ('Products.PloneFormGen', 'Products.PloneFormGen.interfaces.IPloneFormGenThanksPage'),
]


BELONGS_TO_PARENT_INTERFACES = []
for pkg_name, dottedname in BELONGS_TO_PARENT_CANDIDATES:
    try:
        pkg_resources.get_distribution(pkg_name)
    except pkg_resources.DistributionNotFound:
        continue
    BELONGS_TO_PARENT_INTERFACES.append(resolve(dottedname))


def belongs_to_parent(context):
    """This method returns True when the object is considered belonging to its parent.
    An object is considered belonging to its parent when it provides one of the known
    interfaces and does not have a workflow configured.
    The parent object is not checked; this is the job of the caller.
    """
    wftool = getToolByName(context, 'portal_workflow')
    if not filter(lambda iface, c=context: iface.providedBy(c), BELONGS_TO_PARENT_INTERFACES):
        # The object does not provide any of the configured interfaces.
        return False

    if wftool.getWorkflowsFor(context):
        # The object has a workflow and is therefore not considered sl
        # contentish, since it has its own publishing cycle.
        return False

    return True


def get_main_obj_belonging_to(obj):
    for obj_or_parent in aq_chain(aq_inner(obj)):
        if not belongs_to_parent(obj_or_parent):
            return obj_or_parent
