
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap

class RaritanInlet(SnmpPlugin):

    snmpGetTableMaps = (
            GetTableMap(
            'inletConfigurationTable', '.1.3.6.1.4.1.13742.6.3.3.3.1', {
                    '.2': 'inletLabel',
                    '.3': 'inletName',
                    }
                ),
            GetTableMap(
            'inletSensorConfigurationTable',  '.1.3.6.1.4.1.13742.6.3.3.4.1', {
                    '.6': 'inletSensorUnits',
                    '.7': 'inletSensorDecimalDigits'
                    }
                ),
            )

    sensorType = {
            'rmsCurrent': 1,
            'unbalancedCurrent': 3,
            'rmsVoltage': 4,
            'activePower': 5,
            'apparentPower': 6,
            'powerFactor': 7,
            'activeEnergy': 8,
            'frequency': 23,
            }

    def process(self, device, results, log):
        log.info("Processing %s for device %s", self.name(), device.id)
        getdata, tabledata = results
        maps = []

        inletRelMap = RelationshipMap(
                relname='raritanInlets',
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanInlet')

        for snmpindex, row in tabledata.get('inletConfigurationTable', {}).items():
            inletData = {}
            snmpindex = snmpindex.strip('.')
            log.info('snmpindex:{}'.format(snmpindex))
            log.info('row:{}'.format(row))

            title = row.get('inletLabel')
            name = row.get('inletName')
            if name: 
                title = '{} ({})'.format(title, name)

            inletData['id'] = self.prepId(title)
            inletData['title'] = title
            inletData['snmpindex'] = snmpindex

            inletSensors = tabledata.get('inletSensorConfigurationTable', {})
            log.debug('sensors:{}'.format(inletSensors))
            for sensor, sensorNum in self.sensorType.items():
                sensorIndex = '{}.{}'.format(snmpindex, sensorNum)
                inletSensor = inletSensors[sensorIndex]
                inletData['{}_units'.format(sensor)]=inletSensor['inletSensorUnits']
                inletData['{}_digits'.format(sensor)]=inletSensor['inletSensorDecimalDigits']

            log.debug('sensorData:{}'.format(inletData))

            inletRelMap.append(ObjectMap(
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanInlet',
                data=inletData,
                    ))
        maps.append(inletRelMap)

        maps.extend([
            inletRelMap,
            ])

        return maps


                                                                
