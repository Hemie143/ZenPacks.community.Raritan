
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap

class RaritanDeviceEnv(SnmpPlugin):

    snmpGetTableMaps = (
            GetTableMap(
                'externalSensor', '1.3.6.1.4.1.13742.8.1.2.1.1', {
                    '.2':  'externalSensorType',
                    '.3':  'externalSensorSerialNumber',
                    '.4':  'externalSensorName',
                    '.5':  'externalSensorDescription',
                    '.11': 'externalSensorUnits',
                    '.12': 'externalSensorDecimalDigits',
                    '.25': 'externalSensorPort',
                    }
                ),
            )


    def process(self, device, results, log):
        log.info("Processing %s for device %s", self.name(), device.id)
        getdata, tabledata = results
        maps = []

        tempRelMap = RelationshipMap(
                relname='raritanTemperatureSensors',
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanTemperatureSensor')
        humidRelMap = RelationshipMap(
                relname='raritanHumiditySensors',
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanHumiditySensor')
        onOffRelMap = RelationshipMap(
                relname='raritanOnOffSensors',
                compname=self.compname,
                modname='ZenPacks.community.Raritan.RaritanOnOffSensor')

        for snmpindex, row in tabledata.get('externalSensor', {}).items():
            sensor_type = row.get('externalSensorType')
            name = row.get('externalSensorName')

            log.info('index: {} - type: {} - name: {}'.format(snmpindex, sensor_type, name))

            description = row.get('externalSensorDescription')
            title = name
            if description:
                title = '{} ({})'.format(title, description)

            # Next two cases to merge into one ?
            # 
            if sensor_type == 10:      # Temperature sensor
                log.debug('Found temp sensor:{}'.format(name))
                tempRelMap.append(ObjectMap(
                    compname=self.compname,
                    modname='ZenPacks.community.Raritan.RaritanTemperatureSensor',
                    data={
                        'id': self.prepId(name),
                        'title': title,
                        'snmpindex': snmpindex.strip('.'),
                        'serial': row.get('externalSensorSerialNumber', ''),
                        'sensor_type': row.get('externalSensorType', ''),
                        'sensor_units': row.get('externalSensorUnits', ''),
                        'sensor_digits': row.get('externalSensorDecimalDigits', ''),
                        'port': row.get('externalSensorPort', ''),
                        }))
            elif sensor_type == 11:  # Humidity sensor
                log.debug('Found humid sensor:{}'.format(name))
                humidRelMap.append(ObjectMap(
                    compname=self.compname,
                    modname='ZenPacks.community.Raritan.RaritanHumiditySensor',
                    data={
                        'id': self.prepId(name),
                        'title': title,
                        'snmpindex': snmpindex.strip('.'),
                        'serial': row.get('externalSensorSerialNumber', ''),
                        'sensor_type': row.get('externalSensorType', ''),
                        'sensor_units': row.get('externalSensorUnits', ''),
                        'sensor_digits': row.get('externalSensorDecimalDigits', ''),
                        'port': row.get('externalSensorPort', ''),
                    }))
            elif sensor_type == 14:    # Humidity sensor
                log.debug('Found OnOff sensor:{}'.format(name))
                onOffRelMap.append(ObjectMap(
                    compname=self.compname,
                    modname='ZenPacks.community.Raritan.RaritanOnOffSensor',
                    data={
                        'id': self.prepId(name),
                        'title': title,
                        'snmpindex': snmpindex.strip('.'),
                        'serial': row.get('externalSensorSerialNumber', ''),
                        'sensor_type': row.get('externalSensorType', ''),
                        'sensor_units': row.get('externalSensorUnits', ''),
                        'sensor_digits': row.get('externalSensorDecimalDigits', ''),
                        'port': row.get('externalSensorPort', ''),
                        }))
        maps.extend([
            tempRelMap,
            humidRelMap,
            onOffRelMap
            ])

        return maps


                                                                
