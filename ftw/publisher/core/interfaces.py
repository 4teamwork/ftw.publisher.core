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
    #@property
    def on_root(self):
        """
        indicated if this adapter should be available
        on plonr root
        
        usualy only the portlet_data adapter and
        properties_data adapter are used
        
        returns bool (True/False)
        """