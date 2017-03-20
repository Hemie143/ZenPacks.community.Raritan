Ext.onReady(function() {
        var DEVICE_OVERVIEW_ID = 'deviceoverviewpanel_summary';
        Ext.ComponentMgr.onAvailable(DEVICE_OVERVIEW_ID, function(){
            var overview = Ext.getCmp(DEVICE_OVERVIEW_ID);
            overview.removeField('memory');

            overview.addField({
                name: 'model',
                fieldLabel: _t('# Model')
            });
        });
});
