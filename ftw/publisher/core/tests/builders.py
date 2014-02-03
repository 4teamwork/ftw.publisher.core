from ftw.builder.archetypes import ArchetypesBuilder
from ftw.builder import builder_registry


DEFAULT_QUERY = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.is',
    'v': 'Collection Test Page',
}]


class CollectionBuilder(ArchetypesBuilder):
    portal_type = 'Collection'

    def with_default_query(self):
        self.arguments['query'] = DEFAULT_QUERY
        return self

builder_registry.register('collection', CollectionBuilder)
