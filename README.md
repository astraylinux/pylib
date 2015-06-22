#常用的python代码封装
#simple package of python 2.x

`Dependces`: MySQLdb, python-redis, pymssql, python lxml  
Clone this project, and add the upper directory to .bashrc
```bash
PYTHONPATH=$PYTHONPATH:local_dir
export PYTHONPATH
```
Then, `source .bashrc`, import package in you code like that.
```bash
import pylib

test_string = "md5 test"
md5_str = pylib.util.md5(test_string)
```
More examples are in test directory.

##模块(Modules)
`util.py`: some simport function that used often, like get string md5, get the datetime now, so on.  
`sql.py`: depend on the MySQLdb,  package the cursor as a class.  
`thread.py`: quickly start threads with a datas queue.  
`net.py`: simple package of urllib and urllib2 to get(), post(), download_file(), proxy_get()...  
`spider.py`: some commom function the used by website spider.  
`expath.py`: depend on lxml.etree, use the xpath to pick content from html.  
