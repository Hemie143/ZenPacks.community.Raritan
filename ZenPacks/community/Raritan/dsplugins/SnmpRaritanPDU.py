
from twisted.internet.defer import inlineCallbacks, returnValue

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin

from pynetsnmp.twistedsnmp import AgentProxy

# Setup logging
import logging
log = logging.getLogger('zen.PythonRaritan')

measurementsInletSensorIsAvailable  = '1.3.6.1.4.1.13742.6.5.2.3.1.2'
measurementsInletSensorState        = '1.3.6.1.4.1.13742.6.5.2.3.1.3'
measurementsInletSensorValue        = '1.3.6.1.4.1.13742.6.5.2.3.1.4'

measurementsOutletSensorIsAvailable = '1.3.6.1.4.1.13742.6.5.4.3.1.2'
measurementsOutletSensorState       = '1.3.6.1.4.1.13742.6.5.4.3.1.3'
measurementsOutletSensorValue       = '1.3.6.1.4.1.13742.6.5.4.3.1.4'

measurementsOverCurrentProtectorSensorIsAvailable = '1.3.6.1.4.1.13742.6.5.3.3.1.2'
measurementsOverCurrentProtectorSensorState       = '1.3.6.1.4.1.13742.6.5.3.3.1.3'
measurementsOverCurrentProtectorSensorValue       = '1.3.6.1.4.1.13742.6.5.3.3.1.4'


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
    log.debug('snmpV3Args are %s ' % (snmpV3Args))
    snmp_proxy = AgentProxy(
        ip=ds0.manageIp,
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
    d = snmp_proxy.get(scalarOIDstrings)
    return d


def getTableStuff(snmp_proxy, OIDstrings):
    log.debug('In getTableStuff - snmp_proxy is %s and OIDstrings is %s \n' % (snmp_proxy, OIDstrings))
    d = snmp_proxy.getTable(OIDstrings)
    return d

   
class SnmpRaritanPDU(PythonDataSourcePlugin):
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

    sensorVars = ['units', 'digits']

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

        log.debug('In config_key context.device().id is %s datasource.getCycleTime(context) is %s \
            datasource.rrdTemplate().id is %s datasource.id is %s datasource.plugin_classname is %s'\
            % (context.device().id, datasource.getCycleTime(context), datasource.rrdTemplate().id, \
                datasource.id, datasource.plugin_classname))
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
        log.info('Starting SnmpRaritanPDU params')
        params = {}
        for sensorName in cls.sensorType:
            for var in cls.sensorVars:
                param_name = '{}_{}'.format(sensorName, var)
                params[param_name] = getattr(context, param_name, '')

        params['snmpindex'] = context.snmpindex
        log.info(' params is %s \n' % (params))
        return params

    @inlineCallbacks
    def collect(self, config):
        return NotImplementedError

    def onResult(self, result, config):
        """
        Called first for success and error.
 
        You can omit this method if you want the result of the collect method
        to be used without further processing.
        """
        log.debug('result is %s ' % (result))

        return result
 
    def onSuccess(self, result, config):
        return NotImplementedError
            
    def onError(self, result, config):
        """
        Called only on error. After onResult, before onComplete.
 
        You can omit this method if you want the error result of the collect
        method to be used without further processing. It recommended to
        implement this method to capture errors.
        """
        log.debug('In OnError - result is %s and config is %s ' % (result, config))
        return {
            'events': [{
                'summary': 'Error getting SnmpRaritanPDU component data with zenpython: %s' % result,
                'eventKey': 'SnmpRaritanPDU',
                'severity': 4,
                }],
            }
 
    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        log.debug('Starting SnmpRaritanPDU onComplete')
        self._snmp_proxy.close()
        return result


class SnmpRaritanInlet(SnmpRaritanPDU):

    sensorType = {
            'activeEnergy': [8, 'active_energy'],
            'activePower': [5, 'active_power'],
            'apparentPower': [6, 'apparent_power'],
            'frequency': [23, 'frequency'],
            'powerFactor': [7, 'power_factor'],
            'rmsCurrent': [1, 'rms_current'],
            'rmsVoltage': [4, 'rms_voltage'],
            'unbalancedCurrent': [3, 'unbalanced_current'],
            }

    @inlineCallbacks
    def collect(self, config):
        """
        This method really is run by zenpython daemon. Check zenpython.log
        for any log messages.
        """

        log.debug('Starting SnmpRaritanInlet collect')
        ds0 = config.datasources[0]
        # Open the Snmp AgentProxy connection
        self._snmp_proxy = get_snmp_proxy(ds0, config)

        d = yield getTableStuff(self._snmp_proxy, [measurementsInletSensorValue,
                                                  ])
        log.debug('SnmpRaritanInlet data:{}'.format(d))
        returnValue(d)

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        """

        log.debug('In success - result is %s and config is %s ' % (result, config))

        data = self.new_data()

        for ds in config.datasources:
            snmp_index = ds.params.get('snmpindex')
            for sensorName, sensorProp in self.sensorType.items():
                for var in self.sensorVars:
                    param_name = '{}_{}'.format(sensorName, var)
                    digits = int(ds.params.get(param_name))
                    sensor_type = sensorProp[0]
                    oid = '{}.{}.{}'.format(measurementsInletSensorValue, snmp_index, sensor_type)
                    if not oid.startswith('.'):
                        oid = '.'+oid
                    sensor_value = float(result[measurementsInletSensorValue][oid]) / (10 ** digits)
                    try:
                        data['values'][ds.component][sensorProp[1]] = sensor_value
                    except:
                        log.error('SnmpRaritanInlet onSuccess: Error while storing value')
        return data


class SnmpRaritanOutlet(SnmpRaritanPDU):

    sensorType = {
            'activeEnergy': [8, 'active_energy'],
            'activePower': [5, 'active_power'],
            'apparentPower': [6, 'apparent_power'],
            'frequency': [23, 'frequency'],
            'powerFactor': [7, 'power_factor'],
            'rmsCurrent': [1, 'rms_current'],
            'rmsVoltage': [4, 'rms_voltage'],
            }

    @inlineCallbacks
    def collect(self, config):
        """
        This method really is run by zenpython daemon. Check zenpython.log
        for any log messages.
        """

        log.debug('Starting SnmpRaritanOutlet collect')
        ds0 = config.datasources[0]
        # Open the Snmp AgentProxy connection
        self._snmp_proxy = get_snmp_proxy(ds0, config)

        d = yield getTableStuff(self._snmp_proxy, [measurementsOutletSensorValue,
                                                  ])
        log.debug('SnmpRaritanOutlet data:{}'.format(d))
        returnValue(d)

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        """

        log.debug('In success - result is %s and config is %s ' % (result, config))

        data = self.new_data()

        for ds in config.datasources:
            snmp_index = ds.params.get('snmpindex')
            for sensorName, sensorProp in self.sensorType.items():
                for var in self.sensorVars:
                    param_name = '{}_{}'.format(sensorName, var)
                    digits = int(ds.params.get(param_name))
                    sensor_type = sensorProp[0]
                    oid = '{}.{}.{}'.format(measurementsOutletSensorValue, snmp_index, sensor_type)
                    if not oid.startswith('.'):
                        oid = '.'+oid
                    sensor_value = float(result[measurementsOutletSensorValue][oid]) / (10 ** digits)
                    try:
                        data['values'][ds.component][sensorProp[1]] = sensor_value
                    except:
                        log.error('SnmpRaritanOutlet onSuccess: Error while storing value')
        return data
                                                                                                                                                                                     

class SnmpRaritanOCP(SnmpRaritanPDU):

    sensorType = {
            'rmsCurrent': [1, 'rms_current'],
            'trip': [15, 'trip'],
            }

    @inlineCallbacks
    def collect(self, config):
        """
        This method really is run by zenpython daemon. Check zenpython.log
        for any log messages.
        """

        log.debug('Starting SnmpRaritanOCP collect')
        ds0 = config.datasources[0]
        # Open the Snmp AgentProxy connection
        self._snmp_proxy = get_snmp_proxy(ds0, config)

        d = yield getTableStuff(self._snmp_proxy, [measurementsOverCurrentProtectorSensorValue,
                                                  ])
        log.debug('SnmpRaritanOCP data:{}'.format(d))
        returnValue(d)

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
        """

        log.debug('In success - result is %s and config is %s ' % (result, config))
        
        data = self.new_data()

        for ds in config.datasources:
            snmp_index = ds.params.get('snmpindex')
            for sensorName, sensorProp in self.sensorType.items():
                for var in self.sensorVars:
                    param_name = '{}_{}'.format(sensorName, var)
                    digits = int(ds.params.get(param_name))
                    sensor_type = sensorProp[0]
                    oid = '{}.{}.{}'.format(measurementsOverCurrentProtectorSensorValue, snmp_index, sensor_type)
                    if not oid.startswith('.'):
                        oid = '.'+oid
                    sensor_value = float(result[measurementsOverCurrentProtectorSensorValue][oid]) / (10 ** digits)
                    try:
                        data['values'][ds.component][sensorProp[1]] = sensor_value
                    except:
                        log.error('SnmpRaritanOCP onSuccess: Error while storing value')
        return data
