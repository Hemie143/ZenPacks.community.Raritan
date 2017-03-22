
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap

class RaritanOCP(SnmpPlugin):

    snmpGetTableMaps = (
            GetTableMap(
            'overCurrentProtectorConfigurationTable', '.1.3.6.1.4.1.13742.6.3.4.3.1', {
                    '.2': 'overCurrentProtectorLabel',
                    '.3': 'overCurrentProtectorName',
                    }
                ),
            GetTableMap(
            'overCurrentProtectorSensorConfigurationTable',  '.1.3.6.1.4.1.13742.6.3.4.4.1', {
                    '.6': 'overCurrentProtectorSensorUnits',
                    '.7': 'overCurrentProtectorSensorDecimalDigits'
                    }
                ),
            )

    sensorType = {
            'rmsCurrent': 1,
            'trip': 15,
            }

    def process(self, device, results, log):
        log.info("Processing %s for device %s", self.name(), device.id)
        getdata, tabledata = results
        maps = []

        ocpRelMap = RelationshipMap(
                relname='raritanOCPs',
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanOCP')

        for snmpindex, row in tabledata.get('overCurrentProtectorConfigurationTable', {}).items():
            ocpData = {}
            snmpindex = snmpindex.strip('.')
            log.info('snmpindex:{}'.format(snmpindex))
            log.info('row:{}'.format(row))

            title = row.get('overCurrentProtectorLabel')
            name = row.get('overCurrentProtectorName')
            if name: 
                title = '{} ({})'.format(title, name)

            ocpData['id'] = self.prepId(title)
            ocpData['title'] = title
            ocpData['snmpindex'] = snmpindex

            ocpSensors = tabledata.get('overCurrentProtectorSensorConfigurationTable', {})
            log.debug('sensors:{}'.format(ocpSensors))
            for sensor, sensorNum in self.sensorType.items():
                sensorIndex = '{}.{}'.format(snmpindex, sensorNum)
                ocpSensor = ocpSensors[sensorIndex]
                ocpData['{}_units'.format(sensor)]=ocpSensor['overCurrentProtectorSensorUnits']
                ocpData['{}_digits'.format(sensor)]=ocpSensor['overCurrentProtectorSensorDecimalDigits']

            log.debug('sensorData:{}'.format(ocpData))

            ocpRelMap.append(ObjectMap(
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanOCP',
                data=ocpData,
                    ))
        maps.append(ocpRelMap)

        maps.extend([
            ocpRelMap,
            ])

        return maps


                                                                
