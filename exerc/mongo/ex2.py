from mongoengine import *
from pymongo import *
from mongo.My_Documents.versioning_tests import *
from PyQt5.QtCore import QDate

c = connect('2test_db2',
            host='localhost',
            port=27017,
            name='admin',
            password='admin')

print(c)
# for obj in VersionTesting.objects(author='p'):
#     print('#'*10)
#     obj.pretty_print()
