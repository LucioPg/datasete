from mongoengine import *
from pprint import pprint
from PyQt5.QtCore import QDate
from datetime import datetime
import string




class User(Document):
    """ un utente può possedere molte date"""

    # giorni = ReferenceField('Date')
    giorni = ListField(ReferenceField('Date'))
    nome = StringField(required=True, unique=True)

    def pretty_print(self):
        doc = {
            'nome': self.nome,
            'giorni': self.giorni
        }
        return pprint(doc)

class Date(Document):
    """ molte date possono appartenere ad un utente"""
    # user = ReferenceField('User')
    user = ReferenceField('User')
    # user = ReferenceField(User, dbref=False, reverse_delete_rule=CASCADE)
    giorni = ListField(DateField())

    def pretty_print(self):
        user_dict = self.user.nome
        doc = {
            'user': user_dict,
            'giorni': self.giorni
        }
        return pprint(doc)