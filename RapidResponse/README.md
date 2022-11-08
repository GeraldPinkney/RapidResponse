<picture>
 <source media="(prefers-color-scheme: dark)" srcset="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
 <source media="(prefers-color-scheme: light)" srcset="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
 <img alt="Kinaxxxxxxxis Hell Yeah" src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Kinaxis-Logo.svg/512px-Kinaxis-Logo.svg.png">
</picture>

# Rapid Response


the rapidresponse python library allows for interaction with RapidResponse from python. This includes reviewing metadata about the environment, extracting data from RR and pushing data back into RR.  

## Prerequisites
Before using this library there is setup that would need to be performed in RapidResponse. This includes, but is not limited to:
 - creation of a webservices user, 
 - creation of oauth2 client details if required
 - refresh of data model. 

It is also suggested that the RR documentation is reviewed https://help.kinaxis.com/20162/webservice/default.htm

## Quickstart

import necessary classes (Environment & DataTable)
```
>>> from RapidResponse.RapidResponse.Environment import Environment
>>> from RapidResponse.RapidResponse.DataTable import DataTable
```
to use an example configuraton import that too
```
>>> from RapidResponse.RapidResponse.Environment import sample_configuration
>>> print(sample_configuration)
{'url': 'http://localhost/rapidresponse', 'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel', 'auth_type': 'basic', 'username': 'gpiknney_ws', 'password': '1L0veR@pidResponse', 'log_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse'}
```
create an environment within which your work is scoped
```
>>> env = Environment(sample_configuration)
>>> print(env)
Environment(url='http://localhost/rapidresponse')
```
initialise an individual table, in this case Mfg::Part. Then refresh the data, view the num of records & view some row data
```
>>> part = DataTable(env, 'Mfg::Part')
>>> part.RefreshData()
>>> print(len(part))
8883

>>> print(part)
DataTable(environment=Environment(url='http://localhost/rapidresponse', data model directory='C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel', auth_type='basic'),name='Mfg::Part', columns=[Column(name='Name', datatype='String', key='Y'), Column(name='Site', datatype='Reference', key='Y'), Column(name='ABCCode', datatype='Reference', key='N'), Column(name='AfterForecastInterval', datatype='Quantity', key='N'), Column(name='AllocationMultiple', datatype='Quantity', key='N'), Column(name='AvailableRule', datatype='Reference', key='N'), Column(name='AverageQty', datatype='Quantity', key='N'), Column(name='AverageSellingPrice', datatype='Money', key='N'), Column(name='BeforeForecastInterval', datatype='Quantity', key='N'), Column(name='BuyerCode', datatype='Reference', key='N'), Column(name='CarryingCost', datatype='Money', key='N'), Column(name='ConstraintShareFence', datatype='Integer', key='N'), Column(name='DaysSupplyPolicy', datatype='Reference', key='N'), Column(name='DDMRPRule', datatype='Reference', key='N'), Column(name='DemandTimeFence', datatype='Quantity', key='N'), Column(name='Description', datatype='String', key='N'), Column(name='DistributionPlanningRule', datatype='Reference', key='N'), Column(name='ExcessFence', datatype='Integer', key='N'), Column(name='ExpiryType', datatype='Reference', key='N'), Column(name='IncrementalRule', datatype='Reference', key='N'), Column(name='IntermediateSpreadForecastInterval', datatype='Integer', key='N'), Column(name='InventoryHoldingRate', datatype='Quantity', key='N'), Column(name='LeadTimeAdjust', datatype='Quantity', key='N'), Column(name='MaterialCost', datatype='Money', key='N'), Column(name='MinimumShelfLife', datatype='Integer', key='N'), Column(name='MinimumSpreadQuantity', datatype='Quantity', key='N'), Column(name='MUEPoolNettingType', datatype='Reference', key='N'), Column(name='MultiEchelonSafetyStockRule', datatype='Reference', key='N'), Column(name='MultiLevelSearchRule', datatype='Reference', key='N'), Column(name='NextUnit', datatype='Integer', key='N'), Column(name='NumberOfDaysSupply', datatype='Quantity', key='N'), Column(name='OptimizationConfiguration', datatype='Reference', key='N'), Column(name='OptimizationObjectiveWeightOverride', datatype='Reference', key='N'), Column(name='PercentSafetyIntervalCount', datatype='Integer', key='N'), Column(name='PercentSafetyPercent', datatype='Quantity', key='N'), Column(name='PickPackTime', datatype='Quantity', key='N'), Column(name='PlannerCode', datatype='Reference', key='N'), Column(name='PlanningCalendars', datatype='Reference', key='N'), Column(name='PrimarySubstitutionSequence', datatype='Integer', key='N'), Column(name='ProductFamily', datatype='Reference', key='N'), Column(name='ProductGroup1', datatype='String', key='N'), Column(name='ProductGroup2', datatype='String', key='N'), Column(name='RangeOfCoverageBuffer', datatype='Quantity', key='N'), Column(name='ReferencePart', datatype='Reference', key='N'), Column(name='SafetyLeadTime', datatype='Quantity', key='N'), Column(name='SafetyLeadTimeProfile', datatype='Reference', key='N'), Column(name='SafetyStockPolicy', datatype='Reference', key='N'), Column(name='SafetyStockQty', datatype='Quantity', key='N'), Column(name='SourceRule', datatype='Reference', key='N'), Column(name='SpreadForecastInterval', datatype='Integer', key='N'), Column(name='StdUnitCost', datatype='Money', key='N'), Column(name='SubstitutionTolerance', datatype='Integer', key='N'), Column(name='SupplyShareFence', datatype='Integer', key='N'), Column(name='Type', datatype='Reference', key='N'), Column(name='UnitOfMeasure', datatype='Reference', key='N'), Column(name='UnsatisfiedDemandTolerance', datatype='Integer', key='N')], filter=None, sync=True)
rownum: 0 ['0053H-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 1 ['0053H-8C3', 'Japan', 'B', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 2 ['0053H-8C3', 'Ohio', 'B', '0', '1', '', '0', '0', '0', 'OH', '0', '-1', '', '', '0', 'AC Compressor', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'OH', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 3 ['005T1034', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'Alternator', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '005T1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
rownum: 4 ['005T1034', 'Japan', 'B', '0', '1', '', '0', '0', '0', 'JA', '0', '-1', '', '', '0', 'Alternator', '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1', 'JA', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '005T1034', '0', '', 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']

```


## Environment - Overview
this is the python representation of your enviornment. It contains authentication details, data model data (tables, fields, etc) and provides the scoping for working with RR.

**Parameters**
- _configuration_: python dictionary containing environment info used.
## Environment - Usage Instructions
Create dictionary to initialise your environment with. See 2 examples below for basic and oauth2
### config dict for basic authentication
```
>>> basic_conf = {'url': 'http://localhost/rapidresponse',
                'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel',
                'auth_type': 'basic',
                'username': 'gpiknney_ws',
                'password': '1L0veR@pidResponse',
                'log_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse'
             }
```
### config dict for oauth2 authentication
```
>>> oauth2_conf = {'url': 'http://localhost/rapidresponse',
                'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel',
                'auth_type': 'oauth2',
                'clientID' : 'cf394926f315b5ff99e34f24c0a5349d'
                'client_secret' : 'db71331ee1477a2e61ceedac7d786b39b1fd6fa29a124dd5339b7a481a4da71f'
                'log_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse'
             }
```
### contents of the configuration dict

**url**: This is the instance url, i.e. http://na1.kinaxis.net/XXX/ if you are on demand

**authentication**: acceptable values are basic or oauth2

**username/password**: ensure the user is setup per guidelines
in https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/web%2520services/web_service_users.htm

**clientID/client_secret**: as configured in your RR instance if you are using oAuth2

**data_model_directory**: directory that contains the data model files Fields.tab and Tables.tab

**log_directory**: where logging information is written to


### Reviewing data model information on a table
```
>>> from RapidResponse.RapidResponse.Environment import Environment
# create an environment within which your work is scoped

>>> env = Environment(basic_conf)
>>> print(env)
Environment(url='http://localhost/rapidresponse')

>>> print(env.get_table('Part', 'Mfg'))
Table(name='Mfg::Part', fields=[Column(name='Name', datatype='String', key='Y'), Column(name='Site', datatype='Reference', key='Y'), Column(name='ABCCode', datatype='Reference', key='N'), Column(name='AfterForecastInterval', datatype='Quantity', key='N'), Column(name='AllocationMultiple', datatype='Quantity', key='N'), Column(name='AvailableRule', datatype='Reference', key='N'), Column(name='AverageQty', datatype='Quantity', key='N'), Column(name='AverageSellingPrice', datatype='Money', key='N'), Column(name='BeforeForecastInterval', datatype='Quantity', key='N'), Column(name='BuyerCode', datatype='Reference', key='N'), Column(name='CarryingCost', datatype='Money', key='N'), Column(name='ConstraintShareFence', datatype='Integer', key='N'), Column(name='DaysSupplyPolicy', datatype='Reference', key='N'), Column(name='DDMRPRule', datatype='Reference', key='N'), Column(name='DemandTimeFence', datatype='Quantity', key='N'), Column(name='Description', datatype='String', key='N'), Column(name='DistributionPlanningRule', datatype='Reference', key='N'), Column(name='ExcessFence', datatype='Integer', key='N'), Column(name='ExpiryType', datatype='Reference', key='N'), Column(name='IncrementalRule', datatype='Reference', key='N'), Column(name='IntermediateSpreadForecastInterval', datatype='Integer', key='N'), Column(name='InventoryHoldingRate', datatype='Quantity', key='N'), Column(name='LeadTimeAdjust', datatype='Quantity', key='N'), Column(name='MaterialCost', datatype='Money', key='N'), Column(name='MinimumShelfLife', datatype='Integer', key='N'), Column(name='MinimumSpreadQuantity', datatype='Quantity', key='N'), Column(name='MUEPoolNettingType', datatype='Reference', key='N'), Column(name='MultiEchelonSafetyStockRule', datatype='Reference', key='N'), Column(name='MultiLevelSearchRule', datatype='Reference', key='N'), Column(name='NextUnit', datatype='Integer', key='N'), Column(name='NumberOfDaysSupply', datatype='Quantity', key='N'), Column(name='OptimizationConfiguration', datatype='Reference', key='N'), Column(name='OptimizationObjectiveWeightOverride', datatype='Reference', key='N'), Column(name='PercentSafetyIntervalCount', datatype='Integer', key='N'), Column(name='PercentSafetyPercent', datatype='Quantity', key='N'), Column(name='PickPackTime', datatype='Quantity', key='N'), Column(name='PlannerCode', datatype='Reference', key='N'), Column(name='PlanningCalendars', datatype='Reference', key='N'), Column(name='PrimarySubstitutionSequence', datatype='Integer', key='N'), Column(name='ProductFamily', datatype='Reference', key='N'), Column(name='ProductGroup1', datatype='String', key='N'), Column(name='ProductGroup2', datatype='String', key='N'), Column(name='RangeOfCoverageBuffer', datatype='Quantity', key='N'), Column(name='ReferencePart', datatype='Reference', key='N'), Column(name='SafetyLeadTime', datatype='Quantity', key='N'), Column(name='SafetyLeadTimeProfile', datatype='Reference', key='N'), Column(name='SafetyStockPolicy', datatype='Reference', key='N'), Column(name='SafetyStockQty', datatype='Quantity', key='N'), Column(name='SourceRule', datatype='Reference', key='N'), Column(name='SpreadForecastInterval', datatype='Integer', key='N'), Column(name='StdUnitCost', datatype='Money', key='N'), Column(name='SubstitutionTolerance', datatype='Integer', key='N'), Column(name='SupplyShareFence', datatype='Integer', key='N'), Column(name='Type', datatype='Reference', key='N'), Column(name='UnitOfMeasure', datatype='Reference', key='N'), Column(name='UnsatisfiedDemandTolerance', datatype='Integer', key='N')], type='Input', keyed='Y', identification fields='')

```
review fields that a table has available
```
>>> Indy = env.get_table('IndependentDemand', 'Mfg')
>>> for f in Indy._table_fields:
...    print(f)

```
## Data Table - Overview

subclass of Table that contains row data & can be used to push updates to RR. When initialised it takes a deep copy of the Table from the data model and then enriches with data.

**Parameters**
- _environment_: Environment RapidResponse environment for which the table is scoped. 
- _tablename_: Table that contains the data. Format 'Mfg::Part' 
- _columns_: list of column names ['Name', 'Site', ...] that the table will return.
- _table_filter_: string representation of any filter condition applied to the table
- _sync_: boolean value. controls whether updates performed within python are pushed back to RR. 
- _refresh_: boolean value. refresh row data on initialisation. 

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
append rows to the table & have this be pushed to RR
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


## Aaaand now the caveats
offline data model currently
