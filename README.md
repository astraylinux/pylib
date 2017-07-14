# simple package for python 2.x

`Dependces`: MySQLdb, python-redis, pymssql, python lxml

## centos
```bash
sudo yum -y install python-redis MySQL-python python-lxml python-pip freetds-devel
sudo easy_install-2.7 setuptools-git

sudo easy_install-2.7 pymssql #or
sudo pip install pymssql
```

## debain
```bash
sudo apt-get install python-redis python-mysqldb python-pymssql python-lxml
```

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

## 模块(Modules)
<<<<<<< HEAD
`util.py`: some simport function that used often, like get string md5, get the datetime now, so on.  
`sql.py`: depend on the MySQLdb,  package the cursor as a class.  
`thread.py`: quickly start threads with a datas queue.  
`net.py`: simple package of urllib and urllib2 to get(), post(), download_file(), proxy_get()...  
`spider.py`: some commom function the used by website spider.  
`expath.py`: depend on lxml.etree, use the xpath to pick content from html.  
=======
`util.py`: some simport function that used often, like get string md5, get the datetime now, so on.
`sql.py`: depend on the MySQLdb,  package the cursor as a class.
`thread.py`: quickly start threads with a datas queue.
`net.py`: simple package of urllib and urllib2 to get(), post(), download_file(), proxy_get()...
`spider.py`: some commom function the used by website spider.
`expath.py`: depend on lxml.etree, use the xpath to pick content from html.
>>>>>>> e6bc88289e7df8fdd24a5e1e146b9fe8b9ed98bb
