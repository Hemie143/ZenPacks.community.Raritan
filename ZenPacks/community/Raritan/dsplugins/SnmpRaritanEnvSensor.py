
from twisted.internet.defer import inlineCallbacks, returnValue

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin

from pynetsnmp.twistedsnmp import AgentProxy

# Setup logging
import logging
log = logging.getLogger('zen.PythonRaritan')

measurementsExternalSensorIsAvailable = '1.3.6.1.4.1.13742.8.2.1.1.1.1'
measurementsExternalSensorState       = '1.3.6.1.4.1.13742.8.2.1.1.1.2'
measurementsExternalSensorValue       = '1.3.6.1.4.1.13742.8.2.1.1.1.3'

def getSnmpV3Args(ds0):
    snmpv3Args = []
    if '3' in ds0.zSnmpVer:
        if ds0.zSnmpPrivType:
            snmpv3Args += ['-l', 'authPriv']
            snmpv3Args += ['-x', ds0.zSnmpPrivType]
            snmpv3Args += ['-X', ds0.zSnmpPrivPassword]
        elif ds0.zSnmpAuthType:
            snmpv3Args += ['-l', 'authNoPriv']
        else:
            snmpv3Args += ['-l', 'noAuthNoPriv']
        if ds0.zSnmpAuthType:
            snmpv3Args += ['-a', ds0.zSnmpAuthType]
            snmpv3Args += ['-A', ds0.zSnmpAuthPassword]
            snmpv3Args += ['-u', ds0.zSnmpSecurityName]
    return snmpv3Args

def get_snmp_proxy(ds0, config):
    snmpV3Args = getSnmpV3Args(ds0)
    log.debug( 'snmpV3Args are %s ' % (snmpV3Args))
    snmp_proxy = AgentProxy(
        ip = ds0.manageIp,
        port=int(ds0.zSnmpPort),
        timeout=ds0.zSnmpTimeout,
        snmpVersion=ds0.zSnmpVer,
        community=ds0.zSnmpCommunity,
        cmdLineArgs=snmpV3Args,
        protocol=None,
        allowCache=False
        )
    snmp_proxy.open()
    return snmp_proxy


def getScalarStuff(snmp_proxy, scalarOIDstrings):
    # scalarOIDstring must be a list
    # NB scalarOIDstrings MUST all come from the same SNMP table or you get no data returned
    # NB Windows net-snmp agent 5.5.0-1 return null dictionary if
    #     input list is > 1 oid - maybe ?????
    # Agent Proxy get returns dict of {oid_str : <value>}
    log.debug('In getScalarStuff - snmp_proxy is %s and scalarOIDstrings is %s \n' % (snmp_proxy, scalarOIDstrings))
    d=snmp_proxy.get(scalarOIDstrings)
    return d

def getTableStuff(snmp_proxy, OIDstrings):
    log.debug('In getTableStuff - snmp_proxy is %s and OIDstrings is %s \n' % (snmp_proxy, OIDstrings))
    d=snmp_proxy.getTable(OIDstrings)
    return d

class SnmpRaritanEnvSensor(PythonDataSourcePlugin):
    # List of device attributes you might need to do collection.
    proxy_attributes = (
        'zSnmpVer',
        'zSnmpCommunity',
        'zSnmpPort',
        'zSnmpMonitorIgnore',
        'zSnmpAuthPassword',
        'zSnmpAuthType',
        'zSnmpPrivPassword',
        'zSnmpPrivType',
        'zSnmpSecurityName',
        'zSnmpTimeout',
        'zSnmpTries',
        'zMaxOIDPerRequest',
        )

    @classmethod
    def config_key(cls, datasource, context):
        """
        Return a tuple defining collection uniqueness.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.
 
        This example implementation is the default. Split configurations by
        device, cycle time, template id, datasource id and the Python data
        source's plugin class name.
 
        You can omit this method from your implementation entirely if this
        default uniqueness behavior fits your needs. In many cases it will.
        """
        # Logging in this method will be to zenhub.log

        log.debug( 'In config_key context.device().id is %s datasource.getCycleTime(context) is %s datasource.rrdTemplate().id is %s datasource.id is %s datasource.plugin_classname is %s  ' % (context.device().id, datasource.getCycleTime(context), datasource.rrdTemplate().id, datasource.id, datasource.plugin_classname))
        return (
            context.device().id,
            datasource.getCycleTime(context),
            datasource.rrdTemplate().id,
            datasource.id,
            datasource.plugin_classname,
            )
 
    @classmethod
    def params(cls, datasource, context):
        """
        Return params dictionary needed for this plugin.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.

        You have access to the dmd object database here and any attributes
        and methods for the context (either device or component).
 
        You can omit this method from your implementation if you don't require
        any additional information on each of the datasources of the config
        parameter to the collect method below. If you only need extra
        information at the device level it is easier to just use
        proxy_attributes as mentioned above.
        """
        log.debug('Starting SnmpRaritanTempSensor params')
        params = {}
        params['sensor_units'] = context.sensor_units
        params['sensor_digits'] = context.sensor_digits
        params['snmpindex'] = context.snmpindex
        log.debug(' params is %s \n' % (params))
        return params

    @inlineCallbacks
    def collect(self, config):
        """
        No default collect behavior. You must implement this method.
 
        This method must return a Twisted deferred. The deferred results will
        be sent to the onResult then either onSuccess or onError callbacks
        below.

        This method really is run by zenpython daemon. Check zenpython.log
        for any log messages.
        """

        log.debug('Starting SnmpRaritanTempSensor collect')
        log.debug('config:{}'.format(config))
        ds0 = config.datasources[0]
        # Open the Snmp AgentProxy connection
        self._snmp_proxy = get_snmp_proxy(ds0, config)

        # NB NB NB - When getting scalars, they must all come from the SAME snmp table

        # Now get data - 1 scalar OIDs
        d = yield getTableStuff(self._snmp_proxy, [ measurementsExternalSensorIsAvailable,
                measurementsExternalSensorState,
                measurementsExternalSensorValue,
                ])
        log.debug('SnmpRaritanTempSensor data:{}'.format(d))
        returnValue(d)

    def onResult(self, result, config):
        """
        Called first for success and error.
 
        You can omit this method if you want the result of the collect method
        to be used without further processing.
        """
        log.debug( 'result is %s ' % (result))

        return result
 
    def onSuccess(self, result, config):
        return result

    def onError(self, result, config):
        """
        Called only on error. After onResult, before onComplete.
 
        You can omit this method if you want the error result of the collect
        method to be used without further processing. It recommended to
        implement this method to capture errors.
        """
        log.debug( 'In OnError - result is %s and config is %s ' % (result, config))
        return {
            'events': [{
                'summary': 'Error getting Snmp component services data with zenpython: %s' % result,
                'eventKey': 'PythonSnmpWinServComponent',
                'severity': 4,
                }],
            }
 
    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        log.debug('Starting SnmpRaritanTempSensor onComplete')
        self._snmp_proxy.close()
        return result


class SnmpRaritanTempSensor(SnmpRaritanEnvSensor):

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        You should return a data structure with zero or more events, values
        and maps.
        Note that values is a dictionary and events and maps are lists.
        """

        log.debug( 'In success - result is %s and config is %s ' % (result, config))
        # Next line creates a dictionary like
        #          {'values': defaultdict(<type 'dict'>, {}), 'events': [], 'maps':[]}
        # the new_data method is defined in PythonDataSource.py in the Python Collector
        #     ZenPack, datasources directory

        data = self.new_data()

        # To do:
        # 1. Handle different units (Fahrenheit?)
        # 2. Add availability
        # 3. Add state
        # 4. Refactor for all sensors (temperature and humidity)
        for ds in config.datasources:
            snmp_index = ds.params.get('snmpindex')
            sensor_digits = int(ds.params.get('sensor_digits'))
            oid = measurementsExternalSensorValue+'.'+snmp_index
            if not oid.startswith('.'):
                oid = '.'+oid
            sensor_value = float(result[measurementsExternalSensorValue][oid]) / (10 ** sensor_digits)
            try:
                data['values'][ds.component]['temperature'] = sensor_value
            except:
                pass

        data['events'] = []
        data['maps'] = []
        log.debug('data is %s ' % (data))
        return data


class SnmpRaritanHumidSensor(SnmpRaritanEnvSensor):

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        You should return a data structure with zero or more events, values
        and maps.
        """

        log.debug( 'In success - result is %s and config is %s ' % (result, config))
        # Next line creates a dictionary like
        #          {'values': defaultdict(<type 'dict'>, {}), 'events': [], 'maps':[]}
        # the new_data method is defined in PythonDataSource.py in the Python Collector
        #     ZenPack, datasources directory

        data = self.new_data()

        # To do:
        # 1. Handle different units (Fahrenheit?)
        # 2. Add availability
        # 3. Add state
        # 4. Refactor for all sensors (temperature and humidity)
        # 5. Test
        # 6. Test2
        for ds in config.datasources:
            snmp_index = ds.params.get('snmpindex')
            sensor_digits = int(ds.params.get('sensor_digits'))
            oid = measurementsExternalSensorValue+'.'+snmp_index
            if not oid.startswith('.'):
                oid = '.'+oid
            sensor_value = float(result[measurementsExternalSensorValue][oid]) / (10 ** sensor_digits)
            try:
                data['values'][ds.component]['humidity'] = sensor_value
            except:
                pass

        data['events'] = []
        data['maps'] = []
        log.debug( 'data is %s ' % (data))
        return data


class SnmpRaritanOnOffSensor(SnmpRaritanEnvSensor):

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        You should return a data structure with zero or more events, values
        and maps.
        """

        log.debug('In success - result is %s and config is %s ' % (result, config))
        data = self.new_data()

        for ds in config.datasources:
            snmp_index = ds.params.get('snmpindex')
            oid = measurementsExternalSensorState + '.' + snmp_index
            if not oid.startswith('.'):
                oid = '.' + oid
            sensor_state = float(result[measurementsExternalSensorState][oid])
            try:
                data['values'][ds.component]['onoff'] = sensor_state
            except:
                pass

        data['events'] = []
        data['maps'] = []
        log.debug('OnOff data is %s ' % (data))
        return data


