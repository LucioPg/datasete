from mongoengine import *
from pprint import pprint
from PyQt5.QtCore import QDate
from datetime import datetime
import string




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

    # def clean(self):
    #     self.nome_telefono = self.nome + self.telefono

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
    giorni = ListField(DateField(), unique=True)

    def clean(self):
        """ checking if dates are in sequence"""
        delta = (max(self.giorni) - min(self.giorni)).days + 1  # the difference returns a timedelta
        if delta != len(self.giorni):
            raise ValidationError('dates need to be in sequence')

    def pretty_print(self):
        user_dict = self.user.nome
        doc = {
            'user': user_dict,
            'giorni': self.giorni
        }
        return pprint(doc)