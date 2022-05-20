
# from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap, GetMap

class RaritanDevice(SnmpPlugin):

    snmpGetMap = GetMap({
        '.1.3.6.1.4.1.13742.8.1.1.1.1.0': 'deviceName',
        '.1.3.6.1.4.1.13742.8.1.1.1.14.0': 'model',
        })

    def process(self, device, results, log):
        log.info("Processing %s for device %s", self.name(), device.id)
        getdata, tabledata = results
        maps = []

        om = self.objectMap(getdata)
        maps.append(om)

        return maps



