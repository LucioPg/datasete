from mongoengine import *
from datetime import datetime
import string
from pprint import pprint
from PyQt5.QtCore import QDate

class QDateField(DateTimeField):
    """ Custom field to manage PyQt5.QtCore.QDate object"""
    def validate(self, value):
        new_value = self.to_mongo(value)
        if not isinstance(new_value, datetime):
            self.error('cannot parse date "%s"' % value)

    def to_mongo(self, value):
        """ the QDate needs to be converted into datetime before sending to mongo"""
        pyValue = value.toPyDate()
        return datetime(pyValue.year, pyValue.month, pyValue.day)

    def to_python(self, value):
        qdate = QDate(value.year, value.month, value.day)
        return qdate


    def prepare_query_value(self, op, value):
        return super(QDateField, self).prepare_query_value(op, self.to_mongo(value))

class VersionTesting(Document):
    """this has the solely purpose to test the mongoengine"""

    title = StringField(required=True, max_length=200, unique=True)
    content = StringField(required=True)
    author = StringField(required=True, max_length=50)
    published = QDateField(default=QDate().currentDate())
    end = QDateField()
    version = StringField(default='0.0.1')
    phone = StringField(required=1)
    first = IntField()
    second = IntField()
    sum = IntField()


    def pretty_print(self):
        doc = {
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'published': self.published,
            'end': self.end,
            'version': self.version,
            'phone': self.phone,
            'sum': self.sum
        }
        return pprint(doc)
    meta = {
        'indexes': ['author', 'title'],
        'ordering': ['-published', '-version']
    }

    def clean(self):
        self.validate_phonenumber()
        self.compute_sum()
        self.compute_end()


    def validate_phonenumber(self):
        """ checks the number provided is valid by searching for special chars, '+' excluded, and for alpha"""
        special_chars = set(string.punctuation.replace('+', ''))
        for number in self.phone:
            if number.isalpha() or number in special_chars:
                raise ValidationError('Il campo numero di telefono non è valido')

    def compute_sum(self):
        self.sum = self.first + self.second

    def compute_end(self):
        """ tests the QDate object"""
        self.end = self.published.addMonths(1)

