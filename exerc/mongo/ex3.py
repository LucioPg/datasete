from mongo.My_Documents.doc_erbavento import *
from mongoengine import *
from PyQt5.QtCore import QDate
if __name__ == '__main__':
    _connection = connect('test_db',
            host='localhost',
            port=27017
            )
    _connection['test_db'].authenticate(name='admin',
            password='admin')
    dateList = [QDate(2020,1,31), QDate(2020,2,1), QDate(2020,2,2)]  # changed from datetime.datetime
    dateList_2 = [QDate(2020,8,31), QDate(2020,9,1), QDate(2020,9,2)]  # changed from datetime.datetime
    dateList_3 = [QDate(2020,3,31), QDate(2020,4,1), QDate(2020,4,2)]  # changed from datetime.datetime


    def create_ospite(nome, cognome, telefono):
        ospite = Ospite(nome=nome, cognome=cognome, telefono=telefono)
        return ospite  # it does not save for checking for dates during booking

    def create_prenotazione_doc(ospite, date_document):

        return Prenotazione(ospite_id=ospite, giorni=date_document).save()

    def queries_ospite(identificativo):
        return Ospite.objects.get(identificativo=identificativo)

    def queries_dates_from_book(prenotazione):
        return DatePrenotazioni.objects.get(prenotazione=prenotazione)

    def queries_dates(dates=None):
        for date_doc in  DatePrenotazioni.objects:
            if dates == date_doc.giorni:
                return date_doc

    def queries_prenotazioni(dates=None):
        if dates:
            return Prenotazione.objects.get(giorni=dates)

    def create_prenotazione(ospite, dates):
        prenotazione = create_prenotazione_doc(ospite,dates)
        ospite.prenotazioni.append(prenotazione)
        dates.prenotazione = prenotazione
        dates.save()
        ospite.save()

    def book(ospite=None, identificativo=None, nome=None, cognome=None, telefono=None, dates=None):

        if dates:  # it checks if dates are present before confirm the creation of an useless user
            if not ospite:
                try:
                    ospite = create_ospite(nome=nome, cognome=cognome, telefono=telefono)
                    ospite.save()  # ospite needs to be saved before creating a referenced doc
                except Exception as e:
                    print(f'{e}\n going for updating')
                    if identificativo:
                        ospite = queries_ospite(identificativo=identificativo)
                    else:
                        return print('ospite or identificativo is needed')
            try:
                date_document = DatePrenotazioni(
                    giorni=dates,
                    ospite=ospite,
                    stagione='Alta'
                ).save()
                create_prenotazione(ospite, date_document)
            except Exception as e:
                print(e)
                if not len(ospite.prenotazioni):
                    delete_ospite()
        else:
            return print('dates are mandatory, if an instance of user was present it has been aborted')

    def un_book(prenotazione, preserve=True):
        ospite = prenotazione.ospite_id
        dates = prenotazione.giorni
        ospite.prenotazioni.remove(prenotazione)
        if not ospite.prenotazioni and not preserve:
            ospite.delete()
        else:
            ospite.save()
        dates.delete()
        prenotazione.delete()

    def delete_ospite(ospite=None, identificativo=None):
        if not ospite and identificativo:
            ospite = queries_ospite(identificativo=identificativo)
        if ospite:
            if hasattr(ospite, 'prenotazione'):
                for prenotazione_doc in ospite.prenotazione:
                    prenotazione_doc.giorni.delete()
                    prenotazione_doc.delete()
            ospite.delete()

    def update_booking(dates_to_update=None, prenotazione=None):

        if dates_to_update and prenotazione:
            un_book(prenotazione, preserve=True)
            book(ospite=prenotazione.ospite_id, dates=dates_to_update)
        else:
            print('date di prenotazione necessarie')
            # create_prenotazione_doc(ospite)

    # book(nome='Pepped', cognome='sotto', identificativo='Peppedsotto111', telefono='111', dates=dateList)
    prenotazione = queries_dates(dateList).prenotazione
    # un_book(prenotazione)
    update_booking(dates_to_update=dateList_3, prenotazione=prenotazione)
    # delete_ospite(queries_ospite('Peppedsotto111'))
    for obj in Prenotazione.objects():
        print('#'*10)
        obj.pretty_print()

