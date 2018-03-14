import transaction
from plone import api


def add_behaviors(type_to_configure, *additional_behaviors):
    fti = api.portal.get().portal_types.get(type_to_configure)
    behaviors = list(fti.behaviors)
    behaviors += list(additional_behaviors)
    fti.behaviors = tuple(set(behaviors))
    transaction.commit()
