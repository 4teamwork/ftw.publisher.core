# ftw.publisher.core imports
from ftw.publisher.core.interfaces import IDataCollector
from ftw.publisher.core import getLogger

# zope imports
from zope.interface import implements
from zope.component import queryAdapter

# plone imports
from Products.CMFPlone.utils import _createObjectByType 

class TopicCriteraData(object):
    """returns all properties data
    """
    implements(IDataCollector)
    logger= getLogger()
    
    def __init__(self,object):
        self.object = object
        
    @property
    def on_root(self):
        return False


    def getData(self):
        """returns all important data"""
        return self.getTopicCriterias()


    def getTopicCriterias(self):
        """
        extract data from topic criterions, like regular field adapter. 
        but in a special way, because the topic criteras are no accessible
        by the catalog
        
        data = {'criteria_type':{field_data_adapter result}}
        
        """
        criterias = {}
        for criteria in self.object.objectValues():
            field_data_adapter = queryAdapter(criteria, IDataCollector, name="field_data_adapter")
            # this adapter must be available, otherwise we cannot go ahead
            if field_data_adapter is None:
                continue
            id = criteria.id
            data = field_data_adapter.getData()
            data['meta_type'] = criteria.meta_type
            criterias[id] = data
        
        return criterias


    def setData(self, topic_criteria_data, metadata):
        """
        creates criterias fro a topic from 
        {'criteria_type':{field_data_adapter result}}
        """
        self.logger.info('Updating criterias for topic (UID %s)' %
                (self.object.UID())
        )

        current_criterias = [o.id for o in self.object.objectValues()]
        request = self.object.REQUEST
        for criteria_id,data in topic_criteria_data.items():
            #create criteria
            if criteria_id not in current_criterias:
                
                #sortCriteria behave a bit special
                if 'ATSortCriterion' not in criteria_id:
                    criteria = self.object.addCriterion(data['field'],data['meta_type'])
            else:
                criteria = self.object[criteria_id]

            #add sort criteria
            if 'ATSortCriterion' in criteria_id:
                self.object.setSortCriterion(data['field'], data['reversed'])

            # we don't have to update data for for ATSortCriterion
            # because it was readded by setSortCriterion
            # check topic.py line 293
            if 'ATSortCriterion' not in criteria_id:
                field_data_adapter = queryAdapter(criteria,IDataCollector,name="field_data_adapter")
                field_data_adapter.setData(data,metadata)

