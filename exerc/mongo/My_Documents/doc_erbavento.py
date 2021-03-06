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
        if not isinstance(value, QDate):
            qdate = QDate(value.year, value.month, value.day)
            return qdate
        else:
            return value

    def prepare_query_value(self, op, value):
        """ maybe useless"""
        return super(QDateField, self).prepare_query_value(op, self.to_mongo(value))


class Prenotazione(Document):
    """ central class joining dates and users"""
    # ospite_id = StringField(required=True)  # needs to be referenced
    ospite_id = ReferenceField('Ospite', required=True)
    giorni = ReferenceField('DatePrenotazioni',required=True)
    totale_notti = IntField(default=1)
    totale_ospiti = IntField(default=1)
    totale_bambini = IntField(default=0)
    colazione = BooleanField(default=False)
    spese = FloatField(default=0.0)
    importo = FloatField(default=50.0)
    tasse = FloatField(default=0.0)
    lordo = FloatField(default=0.0)
    netto = FloatField(default=0.0)
    note = StringField(max_length=200)
    arrivo = QDateField(required=True)  # needs to be computed
    ultimo_giorno = QDateField(required=True)  # needs to be computed
    giorno_pulizie = QDateField(required=True)  # needs to be computed


    def clean(self):
        self.check_max_ospiti()
        self.check_max_bambini()
        self._compute_giorni()
        self._compute_arrivo()
        self._compute_ultimo_giorno()
        self._compute_giorno_pulizie()
        self._compute_totale_notti()
        self._compute_netto()
        self._compute_tasse()
        self._compute_lordo()



    ##### CHECKS #####

    def check_max_ospiti(self):
        if self.totale_ospiti >= 5:
            self.totale_ospiti = 5

    def check_max_bambini(self):
        if self.totale_bambini and not self.totale_ospiti:
            raise ValidationError('Non ci possono essere solo bambini')


    #### COMPUTED #####
    def _compute_giorni(self):
        self._giorni = self.giorni.giorni

    def _compute_arrivo(self):
        self.arrivo = min(self._giorni)

    def _compute_ultimo_giorno(self):
        self.ultimo_giorno = max(self._giorni)

    def _compute_giorno_pulizie(self):
        self.giorno_pulizie = self.ultimo_giorno.addDays(1)

    def _compute_totale_notti(self):
        self.totale_notti = self.arrivo.daysTo(self.ultimo_giorno) + 1

    def _compute_lordo(self):
        self.lordo = self.netto + self.tasse + self.spese

    def _compute_netto(self):
        self.netto = (self.importo * (self.totale_ospiti - self.totale_bambini))

    def _compute_tasse(self):
        tasse = 0
        contatore = 1
        permanenza = self.arrivo.daysTo(self.ultimo_giorno) + 1
        print('confronta permanenza con tot_notti ', permanenza == self.totale_notti)
        print(f'permanenza {permanenza}')
        mese = self.arrivo.month()
        data = self.arrivo
        for giorno in range(permanenza):
            data = data.addDays(1)
            if data.month() != mese:
                contatore = 0
                mese = data.month()
            if contatore < 3:
                tasse += 2
                print(f'tasse: {tasse} data: {data}')
                contatore += 1

        self.tasse = tasse * abs(self.totale_ospiti - self.totale_bambini)

    def pretty_print(self):
        user_dict = self.ospite_id.identificativo
        doc = {
            'user': user_dict,
            'giorni': self.giorni.giorni
        }
        return pprint(doc)


class Ospite(Document):
    """ doc for Hosts"""
    nome = StringField(required=True)
    cognome = StringField(required=True)
    telefono = StringField(required=1)
    identificativo = StringField(required=True, unique=True)  #needs to be computed
    email = EmailField()
    prenotazioni = ListField(ReferenceField('Prenotazione'), reverse_delete_rule=CASCADE)
    arrivo = QDateField(required=False, unique=1)  # needs to be referenced
    partenza = QDateField(required=False)  # needs to be  referenced
    cliente = BooleanField(default=False)

    def clean(self):
        self.validate_phonenumber()
        self._compute_identificativo()


    #### CHECKS #####

    def validate_phonenumber(self):
        """ checks the number provided is valid by searching for special chars, '+' excluded, and for alpha"""
        special_chars = set(string.punctuation.replace('+', ''))
        for number in self.telefono:
            if number.isalpha() or number in special_chars:
                raise ValidationError('Il campo numero di telefono non è valido')

    #### COMPUTE ####
    def _compute_identificativo(self):
        self.identificativo = self.nome + self.cognome + self.telefono


class DatePrenotazioni(Document):
    """ doc for dates info"""

    stagioni = [
        'Alta',
        'Media',
        'Bassa'
    ]
    ospite = ReferenceField('Ospite')
    prenotazione = ReferenceField('Prenotazione')
    giorni = ListField(QDateField(), unique=True)
    totale_ospiti = IntField(default=1)
    totale_bambini = IntField(default=0)
    colazione = BooleanField(default=False)
    spese = FloatField(default=0.0)
    stagione = StringField(choices=stagioni, default='Alta')   # needs to be referenced
    # is_arrivo = BooleanField()
    # is_partenza = BooleanField()
    # is_booked = BooleanField()

    def clean(self):
        self.check_sequence_for_days()

    #### CHECKS ####

    def check_sequence_for_days(self):
        """ checking if dates are in sequence"""
        # delta = (max(self.giorni) - min(self.giorni)).days + 1  # the difference returns a timedelta
        try:
            delta = abs(max(self.giorni).daysTo(min(self.giorni))) + 1
            if delta != len(self.giorni):
                raise ValidationError('dates need to be in sequence')
        except ValueError as e:
            return print(e)
    #### COMPUTE ####



