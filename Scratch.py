from RapidResponse.DataTable import DataTable
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Table import Table, Column
from RapidResponse.Worksheet import Workbook

if __name__ == '__main__':
    env = Environment(sample_configuration)

    print(env.get_table('Part', 'Mfg'))

    # print IndependentDemand fields
    Indy = env.get_table('IndependentDemand', 'Mfg')
    for f in Indy._table_fields:
        print(f)

    # print with subset of cols
    cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
    IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols)
    for i in IndependentDemand[0:5]:
        print(i)

    part = DataTable(env, 'Mfg::Part', scenario={'Name': 'Integration', 'Scope': 'Public'})
    part.RefreshData()
    print(len(part))
    print(part)

    row0 = ['GP1-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
            '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
            'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
            'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']

    if row0 in part:
        part.del_row(row0)
    row1 = ['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
            '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
            'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
            'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
    if row1 in part:
        del part[part.indexof(row1)]

    rows = [row0, row1]
    part.extend(rows)
    print(len(part))

    for r in rows:
        part.del_row(r)

    part.append(['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
                 '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
                 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
                 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0'])

    index = part.indexof(
        ['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
         '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
         'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
         'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0'])
    part[index][2] = 'C'

    part = Table('Part', 'Mfg', 'input', 'Y')
    col1 = Column('Column1', 'string', 'N')
    col2 = Column('Column2', 'string', 'N')
    part.add_fields(col1, col2)
    print(part.__str__())

    variable_values = {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All", "DataModel_IsIncludeDataTypeSet": "N",
                       "FilterType": "All"}

    wb = Workbook(environment=Environment(sample_configuration),
                  Scenario={"Name": 'Enterprise Data', "Scope": "Public"},
                  workbook={"Name": 'KXSHelperREST', "Scope": 'Public'},
                  SiteGroup="All Sites",
                  Filter={"Name": "All Parts", "Scope": "Public"},
                  VariableValues=variable_values,
                  WorksheetNames=["DataModel_Summary","DataModel_Fields"]
                  )
    wb.refresh()
    for x in wb.worksheets:
        print(x)
        xRows = x.fetch_data()
        print(xRows)

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


mea_configuration = {'url': 'https://na1.kinaxis.net/mrad02_dev01',
                        'data_model_bootstrap': 'KXSHelperREST',
                        'auth_type': 'basic',
                        'username': 'RestAPI',
                        'password': '1LoveR@pidResponse!'
                        }
mea_env = Environment(mea_configuration)
int_wb = {"Name": "[EU] Integration", "Scope": 'Public'}
integration_workbook = Workbook(environment=mea_env, Scenario={'Name': 'Enterprise Data', 'Scope': 'Public'}, workbook=int_wb, SiteGroup="All Sites", WorksheetNames=['RRSite'],Filter={"Name": "All Parts", "Scope": "Public"})
RRSite = integration_workbook.worksheets[0]


list_of_tables = ['Mfg::Part', 'Mfg::IndependentDemand', 'Mfg::Customer']
for t in list_of_tables:
    print(DataTable(env, t))
