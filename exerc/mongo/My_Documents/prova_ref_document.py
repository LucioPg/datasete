from mongoengine import *
from pprint import pprint
from PyQt5.QtCore import QDate
from datetime import datetime
import string


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
        print(value)
        if not isinstance(value, QDate):
            qdate = QDate(value.year, value.month, value.day)
            return qdate
        else:
            return value

    def prepare_query_value(self, op, value):
        """ maybe useless"""
        return super(QDateField, self).prepare_query_value(op, self.to_mongo(value))


class User(Document):
    """ un utente può possedere molte date"""

    # giorni = ReferenceField('Date')
    giorni = ListField(ReferenceField('Date'), reverse_delete_rule=CASCADE)
    # nome = StringField(required=True, unique=True)
    nome = StringField(required=True)
    # telefono = StringField(required=True, unique_with=['nome'])
    telefono = StringField(required=True)
    # nome_telefono = StringField(default='', unique=True)
    nome_telefono = StringField(required=True, unique=True)

    def clean(self):
        self.nome_telefono = self.nome + self.telefono

    def pretty_print(self):
        doc = {
            'nome': self.nome,
            'giorni': self.giorni
        }
        return pprint(doc)

    # meta = {
    #     'indexes': [
    #         'nome_telefono'
    #     ]
    # }
class Date(Document):
    """ molte date possono appartenere ad un utente"""
    # user = ReferenceField('User')
    user = ReferenceField('User')
    # user = ReferenceField(User, dbref=False, reverse_delete_rule=CASCADE)
    # giorni = ListField(DateField(), unique_with=['user'])
    giorni = ListField(QDateField(), unique=True)

    def clean(self):
        """ checking if dates are in sequence"""
        # delta = (max(self.giorni) - min(self.giorni)).days + 1  # the difference returns a timedelta
        delta = abs(max(self.giorni).daysTo(min(self.giorni))) + 1
        print(delta)
        if delta != len(self.giorni):
            raise ValidationError('dates need to be in sequence')

    def pretty_print(self):
        user_dict = self.user.nome
        doc = {
            'user': user_dict,
            'giorni': self.giorni
        }
        return pprint(doc)