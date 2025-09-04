<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
 <source media="(prefers-color-scheme: light)" srcset="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
 <img alt="Kinaxxxxxxxis Hell Yeah" src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
</picture>

# Rapid Response

the RapidPy library allows for interaction with RapidResponse from Python. This includes reviewing metadata about the
environment, extracting data from RR and pushing data back into RR.

## Prerequisites

Before using this library there is setup that would need to be performed in RapidResponse. This includes, but is not
limited to:

- creation of a webservices user (required),
- creation of oauth2 client details (optional),
- upload of the KXSHelperREST.wwb to target environment (optional).
- upload GP.GetWorkbook.Variables.spt
- upload GP.GetWorkbook.Worksheets.spt

It is also suggested that the RR documentation is reviewed https://help.kinaxis.com/20162/webservice/default.htm

## Quickstart

Import necessary classes (Environment & DataTable)

```python
from RapidResponse.Environment import Environment
from RapidResponse.DataTable import DataTable
```

create configuration for use with your environment

```python
sample_configuration = {'url': 'http://localhost/rapidresponse','auth_type': 'basic','username': 'gpinkney_ws','password': '1L0veR@pidResponse'}
print(sample_configuration)
{'url': 'http://localhost/rapidresponse', 'auth_type': 'basic', 'username': 'gpinkney_ws', 'password': '1L0veR@pidResponse'}
```

create an environment within which your work is scoped

```python
env = Environment(sample_configuration)
print(env)
Environment(url='http://localhost/rapidresponse')
```

initialise an individual DataTable, in this case Mfg::Part. This will provide a live view of the Part table, and can be
acted on directly.
Print the num of records & view some row data

```python
part = DataTable(env, 'Mfg::Part')
print(len(part))
8883

print(part)
DataTable(environment=Environment(url='http://localhost/rapidresponse', data model directory='C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel', auth_type='basic'),name='Mfg::Part', columns=[Column(name='Name', datatype='String', key='Y'), Column(name='Site', datatype='Reference', key='Y'), Column(name='ABCCode', datatype='Reference', key='N'), Column(name='AfterForecastInterval', datatype='Quantity', key='N'), Column(name='AllocationMultiple', datatype='Quantity', key='N'), Column(name='AvailableRule', datatype='Reference', key='N'), Column(name='AverageQty', datatype='Quantity', key='N'), Column(name='AverageSellingPrice', datatype='Money', key='N'), Column(name='BeforeForecastInterval', datatype='Quantity', key='N'), Column(name='BuyerCode', datatype='Reference', key='N'), Column(name='CarryingCost', datatype='Money', key='N'), Column(name='ConstraintShareFence', datatype='Integer', key='N'), Column(name='DaysSupplyPolicy', datatype='Reference', key='N'), Column(name='DDMRPRule', datatype='Reference', key='N'), Column(name='DemandTimeFence', datatype='Quantity', key='N'), Column(name='Description', datatype='String', key='N'), Column(name='DistributionPlanningRule', datatype='Reference', key='N'), Column(name='ExcessFence', datatype='Integer', key='N'), Column(name='ExpiryType', datatype='Reference', key='N'), Column(name='IncrementalRule', datatype='Reference', key='N'), Column(name='IntermediateSpreadForecastInterval', datatype='Integer', key='N'), Column(name='InventoryHoldingRate', datatype='Quantity', key='N'), Column(name='LeadTimeAdjust', datatype='Quantity', key='N'), Column(name='MaterialCost', datatype='Money', key='N'), Column(name='MinimumShelfLife', datatype='Integer', key='N'), Column(name='MinimumSpreadQuantity', datatype='Quantity', key='N'), Column(name='MUEPoolNettingType', datatype='Reference', key='N'), Column(name='MultiEchelonSafetyStockRule', datatype='Reference', key='N'), Column(name='MultiLevelSearchRule', datatype='Reference', key='N'), Column(name='NextUnit', datatype='Integer', key='N'), Column(name='NumberOfDaysSupply', datatype='Quantity', key='N'), Column(name='OptimizationConfiguration', datatype='Reference', key='N'), Column(name='OptimizationObjectiveWeightOverride', datatype='Reference', key='N'), Column(name='PercentSafetyIntervalCount', datatype='Integer', key='N'), Column(name='PercentSafetyPercent', datatype='Quantity', key='N'), Column(name='PickPackTime', datatype='Quantity', key='N'), Column(name='PlannerCode', datatype='Reference', key='N'), Column(name='PlanningCalendars', datatype='Reference', key='N'), Column(name='PrimarySubstitutionSequence', datatype='Integer', key='N'), Column(name='ProductFamily', datatype='Reference', key='N'), Column(name='ProductGroup1', datatype='String', key='N'), Column(name='ProductGroup2', datatype='String', key='N'), Column(name='RangeOfCoverageBuffer', datatype='Quantity', key='N'), Column(name='ReferencePart', datatype='Reference', key='N'), Column(name='SafetyLeadTime', datatype='Quantity', key='N'), Column(name='SafetyLeadTimeProfile', datatype='Reference', key='N'), Column(name='SafetyStockPolicy', datatype='Reference', key='N'), Column(name='SafetyStockQty', datatype='Quantity', key='N'), Column(name='SourceRule', datatype='Reference', key='N'), Column(name='SpreadForecastInterval', datatype='Integer', key='N'), Column(name='StdUnitCost', datatype='Money', key='N'), Column(name='SubstitutionTolerance', datatype='Integer', key='N'), Column(name='SupplyShareFence', datatype='Integer', key='N'), Column(name='Type', datatype='Reference', key='N'), Column(name='UnitOfMeasure', datatype='Reference', key='N'), Column(name='UnsatisfiedDemandTolerance', datatype='Integer', key='N')], filter=None, sync=True)
rownum: 0 ['0053H-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 1 ['0053H-8C3', 'Japan', 'B', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 2 ['0053H-8C3', 'Ohio', 'B', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 3 ['005T1034', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'Alternator', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '005T1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 4 ['005T1034', 'Japan', 'B', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Alternator', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '005T1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']

```

## Environment - Overview

this is the Python representation of your environment. It contains authentication details, data model data (tables,
fields, etc) and provides the scoping for working with RR.

**Parameters**

- _configuration_: Python dictionary containing environment info used. Required values are url, authentication details.

## Environment - Usage Instructions

Create dictionary to initialise your environment with. See 2 examples below for basic and oauth2

### config dict for basic authentication

```python
basic_conf = {'url': 'http://localhost/rapidresponse',
                'auth_type': 'basic',
                'username': 'gpiknney_ws',
                'password': '1L0veR@pidResponse',
                }
```

### config dict for oauth2 authentication

```python
oauth2_conf = {'url': 'http://localhost/rapidresponse',
                'auth_type': 'oauth2',
                'clientID' : 'cf394926f315b5ff99e34f24c0a5349d',
                'client_secret' : 'db71331ee1477a2e61ceedac7d786b39b1fd6fa29a124dd5339b7a481a4da71f',
                'log_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse'
             }
```

### config dict for local DM

```python
localDM_conf = {'url': 'http://localhost/rapidresponse',
                'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel',
                'auth_type': 'oauth2',
                'clientID' : 'cf394926f315b5ff99e34f24c0a5349d',
                'client_secret' : 'db71331ee1477a2e61ceedac7d786b39b1fd6fa29a124dd5339b7a481a4da71f'
                }
```

### config dict with helper workbook

```python
localDM_conf = {'url': 'http://localhost/rapidresponse',
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

**data_model_directory**: (Optional) directory that contains the data model files Fields.tab and Tables.tab to allow for
data model files to be provided if seeded DM is not adequate or helper wwb is not possible to import.

**data_model_bootstrap**: (Optional) name of helper workbook (KXSHelperREST.wwb is currently the only workbook
supported). Example can be found in /data/. If not provided, seeded data model is used.

**log_directory**: (Optional) where logging information is written to

**worksheet_script**: (Optional) Name of the helper script that pulls worksheet names from Maestreo. example, '
GP.GetWorkbook.Worksheets'

**variables_script**: (Optional) Name of the helper script that pulls variables from Maestreo. example, '
GP.GetWorkbook.Variables'

### Reviewing data model information on a table

```python
from RapidResponse.Environment import Environment
# create an environment within which your work is scoped

env = Environment(basic_conf)
print(env)
Environment(url='http://localhost/rapidresponse')

print(env.get_table('Part', 'Mfg'))
Table(name='Mfg::Part', fields=[Column(name='ABCCode.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ABCCode.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AfterForecastInterval', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AllocationMultiple', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AvailableRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AvailableRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AverageQty', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='AverageSellingPrice', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='BeforeForecastInterval', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='BuyerCode.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='BuyerCode.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='CarryingCost', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ConstraintShareFence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DaysSupplyPolicy.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DaysSupplyPolicy.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DDMRPRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DemandTimeFence', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Description', datatype='String', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DistributionPlanningRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='DistributionPlanningRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ExcessFence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ExpiryType.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ExpiryType.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='IncrementalRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='IncrementalRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='IntermediateSpreadForecastInterval', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='InventoryHoldingRate', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='LeadTimeAdjust', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MaterialCost', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MinimumShelfLife', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MinimumSpreadQuantity', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MUEPoolNettingType.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MUEPoolNettingType.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiEchelonSafetyStockRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiEchelonSafetyStockRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiLevelSearchRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='MultiLevelSearchRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Name', datatype='String', key='Y', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='NextUnit', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='NumberOfDaysSupply', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='OptimizationConfiguration.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='OptimizationObjectiveWeightOverride.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PartClass.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PercentSafetyIntervalCount', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PercentSafetyPercent', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PickPackTime', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlannerCode.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlannerCode.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlanningCalendars.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PlanningCalendars.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='PrimarySubstitutionSequence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ProductFamily.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ProductGroup1', datatype='String', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ProductGroup2', datatype='String', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='RangeOfCoverageBuffer', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='ReferencePart.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyLeadTime', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyLeadTimeProfile.Site', datatype='Reference', key='N', referencedTable='Site', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyLeadTimeProfile.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyStockPolicy.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyStockPolicy.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SafetyStockQty', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Site.Value', datatype='String', key='Y', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SourceRule.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SourceRule.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SpreadForecastInterval', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='StdUnitCost', datatype='Quantity', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SubstitutionTolerance', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='SupplyShareFence', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Type.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Type.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='UnitOfMeasure.ControlSet', datatype='Reference', key='N', referencedTable='ControlSet', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='UnitOfMeasure.Value', datatype='String', key='N', referencedTable='', referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='UnsatisfiedDemandTolerance', datatype='Integer', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None)], type='Input', keyed='Y', identification fields='')

```

review fields that a table has available

```python
Indy = env.get_table('IndependentDemand', 'Mfg')
for f in Indy.fields:
   print(f)
   
Column(name='Line', datatype='String', key='Y', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)
Column(name='Order', datatype='Reference', key='Y', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)
Column(name='AllotmentOverride', datatype='Reference', key='N', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)

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
- _columns_: list of column names ['Name', 'Site', ] that the table will return.
- _table_filter_: string representation of any filter condition applied to the table
- _sync_: boolean value. controls whether updates performed within Python are pushed back to RR.
- _refresh_: boolean value. refresh row data on initialisation.
- _scenario_: dictionary. contains the name and scope of the scenario within which this will handle data {"Name": "
  Integration", "Scope": "Public"}

## Data Table - Usage Instructions

initialise a data table
This will be initialised with all columns of the table, and any key columns on referenced tables.

```python
from RapidResponse.DataTable import DataTable
env = Environment(sample_configuration)
part = DataTable(env,'Mfg::Part')
```

print table to see the environment information, columns and first few rows of data

```python
part
DataTable(environment=Environment(url='http://localhost/rapidresponse', data_model_directory='C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\data', auth_type='basic'),name='Mfg'::'Part',columns=['Name', 'Site.Value', 'AfterForecastInterval', 'AllocationMultiple', 'AverageQty', 'AverageSellingPrice', 'BeforeForecastInterval', 'CarryingCost', 'ConstraintShareFence', 'DemandTimeFence', 'Description', 'ExcessFence', 'IntermediateSpreadForecastInterval', 'InventoryHoldingRate', 'LeadTimeAdjust', 'MaterialCost', 'MinimumShelfLife', 'MinimumSpreadQuantity', 'NextUnit', 'NumberOfDaysSupply', 'PercentSafetyIntervalCount', 'PercentSafetyPercent', 'PickPackTime', 'PrimarySubstitutionSequence', 'ProductGroup1', 'ProductGroup2', 'RangeOfCoverageBuffer', 'SafetyLeadTime', 'SafetyStockQty', 'SpreadForecastInterval', 'StdUnitCost', 'SubstitutionTolerance', 'SupplyShareFence', 'UnsatisfiedDemandTolerance'], filter=None, sync=True) 
# or if you want to see data in a specific scenario
part = DataTable(env,'Mfg::Part', scenario={"Name": "Integration", "Scope": "Public"})
# view all rows in the table
for p in part:
    print(p)

['XATFT1034', 'Japan', 'C', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Bumper  Round Head', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XATFT1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XATFT1034', 'Ohio', 'C', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'Bumper  Round Head', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XATFT1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XBTFT5334', 'Europe', 'C', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'Pin  Push Nylon', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XBTFT5334', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XBTFT5334', 'Japan', 'C', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Pin  Push Nylon', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XBTFT5334', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
['XBTFT5334', 'Ohio', 'C', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'Pin  Push Nylon', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', 'XBTFT5334', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']

```

extend rows to the table & have this be pushed to RR

```python
row0 = ['GP1-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
row1 = ['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rows = [row0, row1]
part.extend(rows)
print(len(part)
8885

part.RefreshData()
if row0 in part:
    print('it worked!')
else:
    print('quick, raise a bug')


```

delete the new row0 from the part table

```python
part.del_row(row1)
part.RefreshData()
if row1 in part:
    print('it failed!')
else:
    print('it worked!')
```

or use the del command

```python
part.indexof(rec)
8882

del part[8882]
```

view IndependentDemand table, with a subset of columns

```
cols = ['Order.Id', 'Order.Site.Value', 'Order.Customer', 'Order.Type', 'Line', 'Part.Name', 'Part.Site', 'DueDate', 'Quantity']
IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols)
print(IndependentDemand)
```

Use slicing to only view a subset of records

```python
print(IndependentDemand[0:11])
#show rec
```

Attribute access for data tables can be done either via the column index, or via the column name, however in the case of
reference fields (i.e. columns that refer to an attribute that is on another table) its is necessary to use the
underscore '_' instead of dot '.' delimiter

```python
# view the columns for IndependentDemand
print(IndependentDemand[0].columns)
#show rec
# here are all the values for this record
print(IndependentDemand[0])
#show rec
# here is the order site value accessed dynamically with underscore notation
print(IndependentDemand[0].Order_Site_Value)
#show rec
# here is the order site value accessed via the column index
print(IndependentDemand[0][1]])
#show rec
```

for those who love pandas, you may want this

```python
df = pd.DataFrame([p for p in part])
df.columns = [c.name for c in part.columns]
df
```

## Workbook - Overivew

Container for worksheets
https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?\n

**Parameters**

- :param environment: Required. contains the env details for worksheet.
- :param workbook dict: Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": '
  Public'}
- :param Scenario dict: Optional {"Name": "Integration", "Scope": "Public"}
- :param SiteGroup str: Optional, the site or site filter to use with the workbook Example, "All Sites"
- :param WorksheetNames list: Optional, the worksheets you want to retrieve data
  from ["worksheet name1", "worksheet name2"]
- :param Filter str: Optional,the filter to apply to the workbook, defined as an object that contains the filter name
  and scope {"Name": "All Parts", "Scope": "Public"}
- :param VariableValues dict: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "
  DataModel_IsReadOnly": "All"}

## Workbook - Usage Instructions

create a workbook and print the worksheets contained within

```python
# setuo environment with worksheet and variables scripts
sample_configuration = {'url': 'http://localhost/rapidresponse',
                        'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\data',
                        'auth_type': 'basic',
                        'username': 'gpinkney_ws',
                        'password': '1L0veR@pidResponse',
                        'worksheet_script': 'GP.GetWorkbook.Worksheets',
                        'variables_script': 'GP.GetWorkbook.Variables'}

# initialise environment
env = Environment(sample_configuration)
wb_dict = {"Name": 'GP Data Validation', "Scope": 'Public'}

# setup workbook 
wb = Workbook(environment=env, workbook=wb_dict)

# print the worksheets in the workbook
for ws in wb:
    print(ws)

Worksheet: 'Summary By Site', Scope: 'Public'
Worksheet: 'Summary By Part Type', Scope: 'Public'
Worksheet: 'Allocation', Scope: 'Public'
Worksheet: 'BillOfMaterial', Scope: 'Public'
Worksheet: 'BOMAlternate', Scope: 'Public'
Worksheet: 'Batch', Scope: 'Public'
Worksheet: 'Calendar', Scope: 'Public'
Worksheet: 'CalendarDate', Scope: 'Public'
Worksheet: 'Constraint', Scope: 'Public'
Worksheet: 'Constraint Available', Scope: 'Public'
Worksheet: 'CurrencyConversionActuals', Scope: 'Public'
Worksheet: 'CurrencyConversionForecast', Scope: 'Public'
Worksheet: 'Customer', Scope: 'Public'
Worksheet: 'DemandOrder', Scope: 'Public'
Worksheet: 'ForecastDetail', Scope: 'Public'
Worksheet: 'Historical Demand Actual', Scope: 'Public'
Worksheet: 'Historical Supply Actual', Scope: 'Public'
Worksheet: 'IndependentDemand', Scope: 'Public'
Worksheet: 'OnHand', Scope: 'Public'
Worksheet: 'Part', Scope: 'Public'
Worksheet: 'Part Source', Scope: 'Public'
Worksheet: 'PartSolution', Scope: 'Public'
Worksheet: 'Part UOM Conversion', Scope: 'Public'
Worksheet: 'ScheduledReceipt', Scope: 'Public'
Worksheet: 'Site', Scope: 'Public'
Worksheet: 'Source', Scope: 'Public'
Worksheet: 'SourceConstraint', Scope: 'Public'
Worksheet: 'SupplyOrder', Scope: 'Public'
Worksheet: 'Supplier', Scope: 'Public'
Worksheet: 'PartCustomer', Scope: 'Public'
Worksheet: 'ReferencePart', Scope: 'Public'
Worksheet: 'Region', Scope: 'Public'
Worksheet: 'RegionGroup', Scope: 'Public'
Worksheet: 'Part Validation', Scope: 'Public'
Worksheet: 'Part Validation - Details', Scope: 'Public'
Worksheet: 'PartSource Validation', Scope: 'Public'
Worksheet: 'PartSource Validation - Details', Scope: 'Public'
Worksheet: 'Source Validation', Scope: 'Public'
Worksheet: 'Bill Of Material Validation', Scope: 'Public'
Worksheet: 'Calendar Validation', Scope: 'Public'
Worksheet: 'CCF Validation', Scope: 'Public'
Worksheet: 'CCA Validation', Scope: 'Public'
Worksheet: 'UnitOfMeasure Validation', Scope: 'Public'
Worksheet: 'IndependentDemand Validation', Scope: 'Public'
Worksheet: 'ScheduledReceipt Validation', Scope: 'Public'
Worksheet: 'OnHand Validation', Scope: 'Public'
Worksheet: 'Constraints', Scope: 'Public'
Worksheet: 'ConstraintsMDM', Scope: 'Public'
Worksheet: 'ConstraintAvailable', Scope: 'Public'
Worksheet: 'Part Sources', Scope: 'Public'

# refresh all worksheets
wb.
```

## Worksheet - Overview

Subclass of Table that contains row data & can be used to push updates to RR.
When initialised it takes a deep copy of the Table from the data model and then enriches with data.

**Parameters**

- _scenario_: dictionary. contains the name and scope of the scenario within which this will handle data {"Name": "
  Integration", "Scope": "Public"}
- _environment_: Environment RapidResponse environment for which the table is scoped.
- _worksheet_: Required, the worksheets you want to retrieve data from. Example, DataModel_Summary
- _workbook_: Required, The workbook the required data is in. Example, {'Name': 'KXSHelperREST', "Scope": 'Public'}
- _SiteGroup_: Required, the site or site filter to use with the workbook Example, "All Sites"
- _Filter_: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and
  scope {"Name": "All Parts", "Scope": "Public"}
- _VariableValues_: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
- _sync_: boolean value. controls whether updates performed within Python are pushed back to RR.
- _refresh_: boolean value. refresh row data on initialisation.

## Worksheet - Usage Instructions

Create a worksheet and print records

```python
ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",Filter={"Name": "All Parts", "Scope": "Public"}, refresh=True)
print(ws)
"Worksheet(environment=Environment(url='http://localhost/rapidresponse', data_model_directory='C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\data', auth_type='basic'),worksheet='OnHand',workbook={'Name': '.Input Tables', 'Scope': 'Public'},SiteGroup='All Sites',Filter={'Name': 'All Parts', 'Scope': 'Public'},VariableValues=None)"
for x in ws:
    print(x)
 
['521-HOAcA', 'SAProd', '', '', 'SA_Bins1', 'Prod', 'None', 'Unpooled', 'Unrestricted', 'Undefined', '', '0', '2017-03-02', 'Undefined', '2500', '-1', '0']
['521-HOAcA', 'SAProd', '', '', 'SA_Bins2', 'Prod', 'None', 'Unpooled', 'Unrestricted', 'Undefined', '', '0', '2017-03-02', 'Undefined', '500', '-1', '0']
['521-HOAcE', 'SAProd', '', '', 'SA_Bins1', 'Prod', 'None', 'Unpooled', 'Unrestricted', 'Undefined', '', '20000', '2016-11-03', 'Undefined', '20000', '-1', '0']
['521-HOAcE', 'SAProd', '', '', 'SA_Bins2', 'Prod', 'None', 'Unpooled', 'Unrestricted', 'Undefined', '', '20000', '2017-02-02', 'Undefined', '20000', '-1', '0']
```

Create workbook and upload to that workbook

```python
ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",workbook={'Name': 'Orders by Customer', "Scope": 'Public'},scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
# and be aware of whether a column is editable
print([col['IsEditable'] for col in ws.columns])
[True, True, True, True, True, True, True, True, True, True, True, False, True, True, True, True, True]
ws.append(['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual','DC-NorthAmerica'])
# Or use upload
ws.upload(["ordnum0", "1", "Kanata", "KNX", "7000vE", "", "130", "Default", "Kanata"],["ordnum1", "1", "Kanata", "KNX", "7000vE", "", "130", "Default", "Kanata"])
```

## Script

```python
# create a script
Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters={"newScenario": "Good2Great08062024_2","userGroup": "Sales"} )
# print string representation
print(Ignite_Create_Scenario)
"Script(name=Ignite_Create_Scenario, scope=Public, parameters={'newScenario': 'Good2Great08062024_2', 'userGroup': 'Sales'})"

# show its initial status
print(Ignite_Create_Scenario.status)
"Not Run"

# execute the script, as you are happy with the parameters initialised
Ignite_Create_Scenario.execute()
print(Ignite_Create_Scenario.status)
"Success"

# print the result
print(Ignite_Create_Scenario.console)
"Success: Good2Great08062024_2"

# execute it again without updating the parameters. The script executes, but returns an error. This is important. You will need to check the status to see details. 
Ignite_Create_Scenario.execute()
print(Ignite_Create_Scenario.status)
"Error: errorcode JavascriptException message Uncaught Error: Shared Scenario already exists - Good2Great08062024_2 See log for details"

# view the console output
print(Ignite_Create_Scenario.console)
"Error: Shared Scenario already exists - Good2Great08062024_2"

# update a parameter & re-execute
Ignite_Create_Scenario.parameters.update({'newScenario': 'Good2GreatZZZ'})
Ignite_Create_Scenario.execute()
print(Ignite_Create_Scenario.status)
"Success"

```

## Aaaand now the caveats

watch out for date formatting when uploading via workbook.

Keep in mind that when using DataTable for upload/delete use cases you're circumventing lots of the controls built into
RR.
Be aware of the implicit logic built in for tolerances for datatable, and table upload ordering.
When using DataTable for upload, make sure you're only loading the data you want. remove references.

Also, currently no support built in for creating scenario, transacting, then rolling back or committing based on result.
If you want to do this I would suggest creating scripts to manage the scenario (create, delete, commit), and add
decorators.
I did not do this myself as I wanted this to work without adding any resources (like additional scripts) to client
environment. 