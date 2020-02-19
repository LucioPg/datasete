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


    def create_ospite(nome, cognome, telefono):
        ospite = Ospite(nome=nome, cognome=cognome, telefono=telefono)
        # ospite = Ospite(nome=nome, telefono=tel)
        # return Ospite(nome=nome, telefono=tel)  # it does not save for checking for dates during booking
        return ospite  # it does not save for checking for dates during booking

    def create_prenotazione_doc(identificativo):
        Prenotazione(ospite_id=queries_ospite(identificativo)).save()

    def queries_ospite(identificativo):
        return Ospite.objects.get(identificativo=identificativo)

    def queries_dates(ospite=None, identificativo=None):
        if not ospite and identificativo:
            ospite = queries_ospite(identificativo=identificativo)
        return DatePrenotazioni.objects.get(ospite=ospite)

    def update_ospite_dates(ospite, dates):
        ospite.giorni.append(dates)
        ospite.save()
        create_prenotazione_doc(ospite.identificativo)

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
                update_ospite_dates(ospite, date_document)
            except Exception as e:
                print(e)
                if not len(ospite.giorni):
                    delete_ospite()



        else:
            return print('dates are mandatory, if an instance of user was present it has been aborted')


    def un_book(ospite=None, identificativo=None, telefono=None, dates=None, _all=False):
        if ospite or identificativo:
            if not ospite and identificativo:
                ospite = queries_ospite(identificativo=identificativo)
            if _all:  # check if delete all the dates
                for date in DatePrenotazioni.objects(ospite=ospite):
                    ospite.giorni.remove(date)  # removing references in user document
                    date.delete()
                ospite.save()
            else:
                if dates:
                    for date_doc in DatePrenotazioni.objects(ospite=ospite):  # search for dates documents
                        for data in dates:
                            if data in date_doc.giorni:
                                date_doc.giorni.remove(data)  # remove the dates passed into the list
                                for user_date in ospite.giorni:  # removing references in user document
                                    if data in user_date.giorni:
                                        user_date.giorni.remove(data)
                        date_doc.save()
                    ospite.save()


                else:
                    return print('nothing to unbook')

    def delete_ospite(ospite=None, identificativo=None, telefono=None):
        if not ospite and identificativo:
            ospite = queries_ospite(identificativo=identificativo)
        for dates_doc in ospite.giorni:
            dates_doc.delete()
        ospite.delete()

    def update_booking(ospite=None, identificativo=None, dates_to_update=None):

        if ospite or identificativo:
            if not ospite and identificativo:
                ospite = queries_ospite(identificativo=identificativo)
            else:
                return print('An user is needed for to update booking')
        if dates_to_update:
            un_book(ospite=ospite, _all=True)
            book(ospite=ospite, dates=dates_to_update)
            # create_prenotazione_doc(ospite)
        else:
            print('date di prenotazione necessarie')
            # create_prenotazione_doc(ospite)

    book(nome='Pepped', cognome='sotto', identificativo='Peppedsotto111', telefono='111', dates=dateList)
    # delete_ospite(queries_ospite('Peppedsotto111'))
    for obj in Prenotazione.objects():
        print('#'*10)
        obj.pretty_print()

