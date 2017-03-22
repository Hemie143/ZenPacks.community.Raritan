
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap

class RaritanOutlet(SnmpPlugin):

    snmpGetTableMaps = (
            GetTableMap(
            'outletConfigurationTable', '.1.3.6.1.4.1.13742.6.3.5.3.1', {
                    '.2': 'outletLabel',
                    '.3': 'outletName',
                    }
                ),
            GetTableMap(
            'outletSensorConfigurationTable',  '.1.3.6.1.4.1.13742.6.3.5.4.1', {
                    '.6': 'outletSensorUnits',
                    '.7': 'outletSensorDecimalDigits'
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

        outletRelMap = RelationshipMap(
                relname='raritanOutlets',
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanOutlet')

        for snmpindex, row in tabledata.get('outletConfigurationTable', {}).items():
            outletData = {}
            snmpindex = snmpindex.strip('.')
            log.info('snmpindex:{}'.format(snmpindex))
            log.info('row:{}'.format(row))

            title = row.get('outletLabel')
            name = row.get('outletName')
            if name: 
                title = '{} ({})'.format(title, name)

            outletData['id'] = self.prepId(title)
            outletData['title'] = title
            outletData['snmpindex'] = snmpindex

            inletSensors = tabledata.get('outletSensorConfigurationTable', {})
            log.debug('sensors:{}'.format(inletSensors))
            for sensor, sensorNum in self.sensorType.items():
                sensorIndex = '{}.{}'.format(snmpindex, sensorNum)
                outletSensor = inletSensors[sensorIndex]
                outletData['{}_units'.format(sensor)]=outletSensor['outletSensorUnits']
                outletData['{}_digits'.format(sensor)]=outletSensor['outletSensorDecimalDigits']

            log.debug('sensorData:{}'.format(outletData))

            outletRelMap.append(ObjectMap(
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanOutlet',
                data=outletData,
                    ))
        maps.append(outletRelMap)

        maps.extend([
            outletRelMap,
            ])

        return maps


                                                                
