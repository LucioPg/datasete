from mongoengine import *
from pymongo import *
from mongo.My_Documents.versioning_tests import *
from PyQt5.QtCore import QDate

connect('test_db', host='localhost', port=27017)
for obj in VersionTesting.objects(author='p'):
    print('#'*10)
    obj.pretty_print()
