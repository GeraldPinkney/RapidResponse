from RapidResponse.RapidResponse.DataTable import DataTable
from RapidResponse.RapidResponse.Environment import Environment
from RapidResponse.RapidResponse.Environment import sample_configuration

if __name__ == '__main__':
    env = Environment(sample_configuration)
    cols = ['Name', 'Site', 'BuyerCode', 'PlannerCode']
    part = DataTable(env, 'Mfg::Part', columns=cols)
    part.RefreshData()
    print(len(part))
    print(part)

    for i in part:
      print(i)

    single_part = part[0]
    another_part = part[1]
    parts = [single_part, another_part]
    part.extend(parts)

    indycols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
