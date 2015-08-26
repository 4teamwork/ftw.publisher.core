from AccessControl.SecurityInfo import ClassSecurityInformation
from ftw.publisher.core import getLogger
from ftw.publisher.core.interfaces import IDataCollector
from zope.component import queryAdapter
from zope.interface import implements


class TopicCriteraData(object):
    """returns all properties data
    """

    implements(IDataCollector)
    logger = getLogger()
    security = ClassSecurityInformation()

    def __init__(self, object):
        self.object = object

    security.declarePrivate('getData')
    def getData(self):
        """returns all important data"""
        return self.getTopicCriterias()

    security.declarePrivate('getTopicCriterias')
    def getTopicCriterias(self):
        """
        extract data from topic criterions, like regular field adapter.
        but in a special way, because the topic criteras are no accessible
        by the catalog

        data = {'criteria_type':{field_data_adapter result}}

        """
        criterias = {}
        for criteria in self.object.objectValues():
            field_data_adapter = queryAdapter(criteria, IDataCollector,
                                              name="field_data_adapter")
            # this adapter must be available, otherwise we cannot go ahead
            if field_data_adapter is None:
                continue

            # dont add subcollections
            if isinstance(criteria, self.object.__class__):
                continue

            id = criteria.id
            data = field_data_adapter.getData()
            data['meta_type'] = criteria.meta_type
            criterias[id] = data

        return criterias

    security.declarePrivate('setData')
    def setData(self, topic_criteria_data, metadata):
        """
        creates criterias fro a topic from
        {'criteria_type':{field_data_adapter result}}
        """
        self.logger.info('Updating criterias for topic (UID %s)' %
                         (self.object.UID()))

        # easiest way - first delete all criterias
        self.object.manage_delObjects([i for i in self.object.objectIds()
                                       if i != 'syndication_information'])

        for criteria_id, data in topic_criteria_data.items():
            # create criteria

            # sortCriteria behave a bit special
            if 'ATSortCriterion' not in criteria_id:
                criteria = self.object.addCriterion(data['field'],
                                                    data['meta_type'])

            # add/change sort criteria
            if 'ATSortCriterion' in criteria_id:
                self.object.setSortCriterion(data['field'], data['reversed'])

            # we don't have to update data for for ATSortCriterion
            # check topic.py line 293
            if 'ATSortCriterion' not in criteria_id:
                field_data_adapter = queryAdapter(criteria, IDataCollector,
                                                  name="field_data_adapter")
                field_data_adapter.setData(data, metadata)
