# python3 -m pip install PyYAML>=5.4.1
# https://www.cnblogs.com/lisa2016/p/11764808.html
import os

from yaml import load, Loader

try_load = lambda i: [load(open(i[0] + '/' + j), Loader=Loader) for j in i[2]]

print([try_load(i) for i in os.walk('$YOUR_API_DIR')])
