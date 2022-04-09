# -*- coding: utf-8 -*-
"""
@Time ： 2022/4/1 18:02
@Auth ： ZhaoFan
@File ：check_diff_pickle.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
# import pandas as pd
#
# org_df = pd.read_pickle('cluster_20220325.pkl')
#
# for key, val in org_df.items():
#     a = key
#     b = val
import pandas as pd

target_port_industry_dict = {
    'a': 1,
    'b': 2,
    'c': 3,
}
similarity_port_industry_dict = {
    'a': 1,
    'd': 2,
    'e': 3,
}
all_ind_list = set(target_port_industry_dict.keys()) | set(similarity_port_industry_dict.keys())
print(all_ind_list)
result = []
for i in all_ind_list:
    result.append(
        {
            'key': i,
            'target_weight': target_port_industry_dict.get(i),
            'port_weight': similarity_port_industry_dict.get(i)
        }
    )
from pprint import pp

pp(result)


def foo(item):
    # if not item.get("target_weight"):
    #     print('item: ', item)
    #     return 0
    return item.get("target_weight", 0) or 0


print('#' * 50)
# result.sort(key=foo, reverse=True)
result.sort(key=lambda i: i.get('target_weight', 0) or 0, reverse=True)
pp(result)

data = [1, 2, 3]
print(f'{data} has no data')
"""
http://8.130.16.215:50002/api/v1/firp/fund_research/performance_analysis/similar_fund/gen_ports?fund_code=001384.OF&compute_date=2022-04-01&pool_size=5&white_list=all_fund
http://8.130.16.215:50002/api/v1/firp/fund_research/performance_analysis/similar_fund/gen_ports?fund_code=000828.OF&compute_date=2022-04-01&pool_size=5&white_list=all_fund

select fund, ind, weight from fund_industry_inspect prewhere fund in ('004925', '000884', '000793', '008084', '003853') and sw_type = 1 and date = '2022-04-01'

select fund, ind, weight from fund_industry_inspect prewhere fund in ('000828') and sw_type = 1 and date = '2022-04-01'

LTER TABLE `new_schema`.`users` 
CHANGE COLUMN `update_time` `update_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ;

"""

data = {
    'fund_code': ['001384.OF', '000828.OF', '001384.OF', '000828.OF', '001384.OF', '001856.OF', '001384.OF',
                  '001856.OF'],
    'fund_chg': [0.7, 0, 6, 0.2, 0.5, 0.3, 0.4, 0.2, 0.1],
    'trading_day': ['2022-03-04', '2022-03-04', '2022-03-03', '2022-03-03', '2022-03-02', '2022-03-02', '2022-03-01',
                    '2022-03-01']
}
df = pd.DataFrame(data)

a = 1
b = 2
