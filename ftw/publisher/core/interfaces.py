from zope.component import Interface


class IDataCollector(Interface):
    """marker interface for datacollectors
    """

    def getData(self):
        """returns all data in dict
        """

    def setData(self):
        """sets data
        """
