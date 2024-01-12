<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
 <source media="(prefers-color-scheme: light)" srcset="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
 <img alt="Kinaxxxxxxxis Hell Yeah" src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
</picture>

# Rapid Response


the RapidPy library allows for interaction with RapidResponse from Python. This includes reviewing metadata about the environment, extracting data from RR and pushing data back into RR.  

## Prerequisites
Before using this library there is setup that would need to be performed in RapidResponse. This includes, but is not limited to:
 - creation of a webservices user (required), 
 - creation of oauth2 client details (optional),
 - upload of the KXSHelperREST.wwb to target environment (optional). 

It is also suggested that the RR documentation is reviewed https://help.kinaxis.com/20162/webservice/default.htm

## Quickstart
Import necessary classes (Environment & DataTable)
```
>>> from RapidResponse.Environment import Environment
>>> from RapidResponse.DataTable import DataTable
```
create configuration for use with your environment
```
>>> sample_configuration = {'url': 'http://localhost/rapidresponse','auth_type': 'basic','username': 'gpinkney_ws','password': '1L0veR@pidResponse'}
>>> print(sample_configuration)
{'url': 'http://localhost/rapidresponse', 'auth_type': 'basic', 'username': 'gpinkney_ws', 'password': '1L0veR@pidResponse'}
```
create an environment within which your work is scoped
```
>>> env = Environment(sample_configuration)
>>> print(env)
Environment(url='http://localhost/rapidresponse')
```
initialise an individual DataTable, in this case Mfg::Part. This will provide a live view of the Part table, and can be acted on directly.
Print the num of records & view some row data
```
>>> part = DataTable(env, 'Mfg::Part')
>>> print(len(part))
8883
...
>>> print(part)
DataTable(environment=Environment(url='http://localhost/rapidresponse', data model directory='C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel', auth_type='basic'),name='Mfg::Part', columns=[Column(name='Name', datatype='String', key='Y'), Column(name='Site', datatype='Reference', key='Y'), Column(name='ABCCode', datatype='Reference', key='N'), Column(name='AfterForecastInterval', datatype='Quantity', key='N'), Column(name='AllocationMultiple', datatype='Quantity', key='N'), Column(name='AvailableRule', datatype='Reference', key='N'), Column(name='AverageQty', datatype='Quantity', key='N'), Column(name='AverageSellingPrice', datatype='Money', key='N'), Column(name='BeforeForecastInterval', datatype='Quantity', key='N'), Column(name='BuyerCode', datatype='Reference', key='N'), Column(name='CarryingCost', datatype='Money', key='N'), Column(name='ConstraintShareFence', datatype='Integer', key='N'), Column(name='DaysSupplyPolicy', datatype='Reference', key='N'), Column(name='DDMRPRule', datatype='Reference', key='N'), Column(name='DemandTimeFence', datatype='Quantity', key='N'), Column(name='Description', datatype='String', key='N'), Column(name='DistributionPlanningRule', datatype='Reference', key='N'), Column(name='ExcessFence', datatype='Integer', key='N'), Column(name='ExpiryType', datatype='Reference', key='N'), Column(name='IncrementalRule', datatype='Reference', key='N'), Column(name='IntermediateSpreadForecastInterval', datatype='Integer', key='N'), Column(name='InventoryHoldingRate', datatype='Quantity', key='N'), Column(name='LeadTimeAdjust', datatype='Quantity', key='N'), Column(name='MaterialCost', datatype='Money', key='N'), Column(name='MinimumShelfLife', datatype='Integer', key='N'), Column(name='MinimumSpreadQuantity', datatype='Quantity', key='N'), Column(name='MUEPoolNettingType', datatype='Reference', key='N'), Column(name='MultiEchelonSafetyStockRule', datatype='Reference', key='N'), Column(name='MultiLevelSearchRule', datatype='Reference', key='N'), Column(name='NextUnit', datatype='Integer', key='N'), Column(name='NumberOfDaysSupply', datatype='Quantity', key='N'), Column(name='OptimizationConfiguration', datatype='Reference', key='N'), Column(name='OptimizationObjectiveWeightOverride', datatype='Reference', key='N'), Column(name='PercentSafetyIntervalCount', datatype='Integer', key='N'), Column(name='PercentSafetyPercent', datatype='Quantity', key='N'), Column(name='PickPackTime', datatype='Quantity', key='N'), Column(name='PlannerCode', datatype='Reference', key='N'), Column(name='PlanningCalendars', datatype='Reference', key='N'), Column(name='PrimarySubstitutionSequence', datatype='Integer', key='N'), Column(name='ProductFamily', datatype='Reference', key='N'), Column(name='ProductGroup1', datatype='String', key='N'), Column(name='ProductGroup2', datatype='String', key='N'), Column(name='RangeOfCoverageBuffer', datatype='Quantity', key='N'), Column(name='ReferencePart', datatype='Reference', key='N'), Column(name='SafetyLeadTime', datatype='Quantity', key='N'), Column(name='SafetyLeadTimeProfile', datatype='Reference', key='N'), Column(name='SafetyStockPolicy', datatype='Reference', key='N'), Column(name='SafetyStockQty', datatype='Quantity', key='N'), Column(name='SourceRule', datatype='Reference', key='N'), Column(name='SpreadForecastInterval', datatype='Integer', key='N'), Column(name='StdUnitCost', datatype='Money', key='N'), Column(name='SubstitutionTolerance', datatype='Integer', key='N'), Column(name='SupplyShareFence', datatype='Integer', key='N'), Column(name='Type', datatype='Reference', key='N'), Column(name='UnitOfMeasure', datatype='Reference', key='N'), Column(name='UnsatisfiedDemandTolerance', datatype='Integer', key='N')], filter=None, sync=True)
rownum: 0 ['0053H-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 1 ['0053H-8C3', 'Japan', 'B', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 2 ['0053H-8C3', 'Ohio', 'B', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 3 ['005T1034', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'Alternator', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '005T1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 4 ['005T1034', 'Japan', 'B', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Alternator', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '005T1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']

```


## Environment - Overview
this is the Python representation of your environment. It contains authentication details, data model data (tables, fields, etc) and provides the scoping for working with RR.

**Parameters**
- _configuration_: Python dictionary containing environment info used. Required values are url, authentication details.
## Environment - Usage Instructions
Create dictionary to initialise your environment with. See 2 examples below for basic and oauth2
### config dict for basic authentication
```
>>> basic_conf = {'url': 'http://localhost/rapidresponse',
                'auth_type': 'basic',
                'username': 'gpiknney_ws',
                'password': '1L0veR@pidResponse',
                }
```
### config dict for oauth2 authentication
```
>>> oauth2_conf = {'url': 'http://localhost/rapidresponse',
                'auth_type': 'oauth2',
                'clientID' : 'cf394926f315b5ff99e34f24c0a5349d',
                'client_secret' : 'db71331ee1477a2e61ceedac7d786b39b1fd6fa29a124dd5339b7a481a4da71f',
                'log_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse'
             }
```
### config dict for local DM
```
>>> localDM_conf = {'url': 'http://localhost/rapidresponse',
                'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel',
                'auth_type': 'oauth2',
                'clientID' : 'cf394926f315b5ff99e34f24c0a5349d',
                'client_secret' : 'db71331ee1477a2e61ceedac7d786b39b1fd6fa29a124dd5339b7a481a4da71f'
                }
```
### config dict with helper workbook
```
>>> localDM_conf = {'url': 'http://localhost/rapidresponse',
                'data_model_bootstrap': 'KXSHelperREST',
                'auth_type': 'oauth2',
                'clientID' : 'cf394926f315b5ff99e34f24c0a5349d',
                'client_secret' : 'db71331ee1477a2e61ceedac7d786b39b1fd6fa29a124dd5339b7a481a4da71f'
                }
```
### contents of the configuration dict

**url**: (Mandatory) This is the instance url, i.e. http://na1.kinaxis.net/XXX if you are on demand

**authentication**: (Mandatory) acceptable values are basic or oauth2

**username/password**: (Mandatory if basic authentication) ensure the user is setup per guidelines
in https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/web%2520services/web_service_users.htm

**clientID/client_secret**: (Mandatory if oauth2) as configured in your RR instance if you are using oAuth2

**data_model_directory**: (Optional) directory that contains the data model files Fields.tab and Tables.tab to allow for data model files to be provided if seeded DM is not adequate or helper wwb is not possible to import.

**data_model_bootstrap**: (Optional) name of helper workbook (KXSHelperREST.wwb is currently the only workbook supported). Example can be found in /data/. If not provided, seeded data model is used.

**log_directory**: (Optional) where logging information is written to


### Reviewing data model information on a table
```
>>> from RapidResponse.Environment import Environment
# create an environment within which your work is scoped

>>> env = Environment(basic_conf)
>>> print(env)
Environment(url='http://localhost/rapidresponse')

>>> print(env.get_table('Part', 'Mfg'))
Table(name='Mfg::Part', fields=[Column(name='ABCCode.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ABCCode.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AfterForecastInterval', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AllocationMultiple', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AvailableRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AvailableRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AverageQty', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AverageSellingPrice', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='BeforeForecastInterval', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='BuyerCode.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='BuyerCode.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='CarryingCost', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ConstraintShareFence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DaysSupplyPolicy.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DaysSupplyPolicy.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DDMRPRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DemandTimeFence', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Description', datatype='String', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DistributionPlanningRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DistributionPlanningRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ExcessFence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ExpiryType.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ExpiryType.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='IncrementalRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='IncrementalRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='IntermediateSpreadForecastInterval', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='InventoryHoldingRate', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='LeadTimeAdjust', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MaterialCost', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MinimumShelfLife', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MinimumSpreadQuantity', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MUEPoolNettingType.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MUEPoolNettingType.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiEchelonSafetyStockRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiEchelonSafetyStockRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiLevelSearchRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiLevelSearchRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Name', datatype='String', key='Y', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='NextUnit', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='NumberOfDaysSupply', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='OptimizationConfiguration.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='OptimizationObjectiveWeightOverride.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PartClass.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PercentSafetyIntervalCount', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PercentSafetyPercent', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PickPackTime', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlannerCode.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlannerCode.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlanningCalendars.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlanningCalendars.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PrimarySubstitutionSequence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ProductFamily.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ProductGroup1', datatype='String', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ProductGroup2', datatype='String', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='RangeOfCoverageBuffer', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ReferencePart.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyLeadTime', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyLeadTimeProfile.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyLeadTimeProfile.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyStockPolicy.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyStockPolicy.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyStockQty', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Site.Value', datatype='String', key='Y', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SourceRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SourceRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SpreadForecastInterval', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='StdUnitCost', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SubstitutionTolerance', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SupplyShareFence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Type.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Type.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='UnitOfMeasure.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='UnitOfMeasure.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='UnsatisfiedDemandTolerance', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None)], type='Input', keyed='Y', identification fields='')

```
review fields that a table has available
```
>>> Indy = env.get_table('IndependentDemand', 'Mfg')
>>> for f in Indy.fields:
...    print(f)
...    
Column(name='Line', datatype='String', key='Y', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)
Column(name='Order', datatype='Reference', key='Y', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)
Column(name='AllotmentOverride', datatype='Reference', key='N', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)
...
```
## Data Model - Overview

**Parameters**
- _data_model_directory_: (Optional) local directory containing field and table data. 
- _url_: (Optional) This is the instance url, i.e. http://na1.kinaxis.net/XXX if you are on demand
- _headers_: (Optional)  
- _workbook_: (Optional) helper workbook containing workbook name 

## Data Table - Overview

Subclass of Table that contains row data & can be used to push updates to RR. 
When initialised it takes a deep copy of the Table from the data model and then enriches with data.

**Parameters**
- _environment_: Environment RapidResponse environment for which the table is scoped. 
- _tablename_: Table that contains the data. Format 'Mfg::Part' 
- _columns_: list of column names ['Name', 'Site', ...] that the table will return.
- _table_filter_: string representation of any filter condition applied to the table
- _sync_: boolean value. controls whether updates performed within Python are pushed back to RR. 
- _refresh_: boolean value. refresh row data on initialisation. 
- _scenario_: dictionary. contains the name and scope of the scenario within which this will handle data {"Name": "Integration", "Scope": "Public"}

## Data Table - Usage Instructions

view all rows in the table
```
>>> for p in part:
...     print(p)
... 
['XATFT1034', 'Japan', 'C', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Bumper  Round Head', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XATFT1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XATFT1034', 'Ohio', 'C', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'Bumper  Round Head', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XATFT1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XBTFT5334', 'Europe', 'C', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'Pin  Push Nylon', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XBTFT5334', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XBTFT5334', 'Japan', 'C', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Pin  Push Nylon', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XBTFT5334', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XBTFT5334', 'Ohio', 'C', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'Pin  Push Nylon', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XBTFT5334', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
...
```
extend rows to the table & have this be pushed to RR
```
>>> row0 = ['GP1-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
>>> row1 = ['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
>>> rows = [row0, row1]
>>> part.extend(rows)
>>> print(len(part)
8885

>>> part.RefreshData()
>>> if row0 in part:
...     print('it worked!')
>>> else:
...     print('quick, raise a bug')
...
>>> 
```
delete the new row0 from the part table
```
>>> part.del_row(row1)
>>> part.RefreshData()
>>> if row1 in part:
...     print('it failed!')
>>> else:
...     print('it worked!')
...
```
or use the del command 
```
>>> part.indexof(rec)
8882

>>> del part[8882]
```
view IndependentDemand table, with a subset of columns
```
>>> cols = ['Order','Line','Part','DueDate','Quantity']
>>> IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols)
>>> print(IndependentDemand)
```
use slicing to only view a subset of records
```
print(IndependentDemand[0:11])
```
## Worksheet - Overview

Subclass of Table that contains row data & can be used to push updates to RR. 
When initialised it takes a deep copy of the Table from the data model and then enriches with data.

**Parameters**
- _scenario_: dictionary. contains the name and scope of the scenario within which this will handle data {"Name": "Integration", "Scope": "Public"} 
- _environment_: Environment RapidResponse environment for which the table is scoped. 
- _worksheet_: Required, the worksheets you want to retrieve data from. Example, DataModel_Summary
- _workbook_: Required, The workbook the required data is in. Example, {'Name': 'KXSHelperREST', "Scope": 'Public'}
- _SiteGroup_: Required, the site or site filter to use with the workbook Example, "All Sites" 
- _Filter_: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"} 
- _VariableValues_: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}

## Worksheet - Usage Instructions

Create a worksheet and print records
```
variable_values = {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All", "DataModel_IsIncludeDataTypeSet": "N","FilterType": "All"}

wb = Workbook(environment=Environment(sample_configuration),
              Scenario={"Name": 'Enterprise Data', "Scope": "Public"},
              workbook={"Name": 'KXSHelperREST', "Scope": 'Public'},
              SiteGroup="All Sites",
              Filter={"Name": "All Parts", "Scope": "Public"},
              VariableValues=variable_values,
              WorksheetNames=["DataModel_Summary"]
              )
wb.refresh()
for x in wb.worksheets:
    print(x)
    xRows = x.RefreshData()
    print(xRows)
```
Create workbook and upload to that workbook
```
wb_ords = Workbook(environment=Environment(sample_configuration),
                   Scenario={"Name": "Integration", "Scope": "Public"},
                   workbook={"Name": 'Orders by Customer', "Scope": 'Public'},
                   SiteGroup="All Sites",
                   Filter={"Name": "All Parts", "Scope": "Public"},
                   VariableValues={"customer": "PCW"},
                   WorksheetNames=["Actual Orders"]
                   )
ws = wb_ords.worksheets[0]
ws.upload(["ordnum0", "1", "Kanata", "KNX", "7000vE", "", "130", "Default", "Kanata"],
          ["ordnum1", "1", "Kanata", "KNX", "7000vE", "", "130", "Default", "Kanata"])
```
## Aaaand now the caveats

