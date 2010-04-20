import collective.testcaselayer.ptc

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        pass
        # we don't have to install anything yet

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])