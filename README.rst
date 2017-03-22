====================================
ZenPack to monitor Raritan devices
====================================

Description
===========

This Zenoss ZenPack allows you to monitor Raritan devices of the following type:
     * Environmental sensors
     * PDUs (Power Distribution Units)

The ZenPack has been tested with the following models: 
     * EMX2-111
     * PX3-4528V

The ZenPack is using SNMP to connect to the devices. Make sure the SNMP zProperties are correctly filled in. 

zProperties
===========
Nihil

Templates
=========
    * RaritanHumiditySensor: monitors the humidity sensors on an EMX device
    * RaritanTemperatureSensor: monitors the temperature sensors on an EMX device
    * RaritanInlet: monitors the Inlet(s) of a PDU
    * RaritanOutlet: monitors the Outlet(s) of a PDU
    * RaritanOCP: monitors the OverCurrent Protector(s) of a PDU

Modeler Plugins
===============

    * community.snmp.RaritanDevice: models the Raritan device
    * community.snmp.RaritanDeviceEnv: models the environmental sensors (Temperature and Humidity)
    * community.snmp.RaritanInlet: models the PDU Inlets
    * community.snmp.RaritanOutlet: models the PDU Outlets
    * community.snmp.RaritanOCP: models the PDU Overcurrent Protectors

Requirements & Dependencies
===========================

    * Zenoss version: 4.2.x or higher
    * ZenPacks Dependencies: ZenPackLib ?, PythonCollector

Change History
==============
* 1.0.1
  * First public release

To Do
=====
    * Add status and availability for each sensor
    * Add device serial number (if possible)
    * Add thresholds in sensor templates
    * Replace Hardware Model with something readable
    * Device modeling: add condition function
    * Add PDU Pole monitoring
    * ...





