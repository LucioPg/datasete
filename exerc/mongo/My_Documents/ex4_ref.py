from mongo.My_Documents.prova_ref_document import *
# from datetime import datetime
import datetime
from mongoengine import *
from pprint import pprint

connect('test_db', host='localhost', port=27017)
dateList = [datetime.date(2020,1,3), datetime.date(2020,1,4), datetime.date(2020,1,6)]  # changed from datetime.datetime


def create_user(nome):
    return User(nome=nome)  # it does not save for checking for dates during booking

def queries_user(username):
    return User.objects.get(nome=username)

def queries_dates(user=None, username=None):
    if not user and username:
        user = queries_user(username=username)
    return Date.objects.get(user=user)

def update_user_dates(user, dates):
    user.giorni.append(dates)
    user.save()

def book(user=None, username=None, dates=None):

    if dates:  # it checks if dates are present before confirm the creation of an useless user
        if not user:
            if username:
                try:
                    user = create_user(nome=username)
                    user.save()  # user needs to be saved before creating a referenced doc
                except Exception as e:
                    user = queries_user(username)
                    print(f'{e}\n going for updating')
            else:
                return print('user or username is needed')
        date_document = Date(
            giorni=dates,
            user=user
        ).save()
        update_user_dates(user, date_document)
    else:
        return print('dates are mandatory, if an instance of user was present it has been aborted')


def un_book(user=None, username=None, dates=None, _all=False):
    if user or username:
        if not user and username:
            user = queries_user(username=username)
        if _all:  # check if delete all the dates
            for date in Date.objects(user=user):
                user.giorni.remove(date)  # removing references in user document
                date.delete()
            user.save()
        else:
            if dates:
                for date_doc in Date.objects(user=user):  # search for dates documents
                    for data in dates:
                        if data in date_doc.giorni:
                            date_doc.giorni.remove(data)  # remove the dates passed into the list
                            for user_date in user.giorni:  # removing references in user document
                                if data in user_date.giorni:
                                    user_date.giorni.remove(data)
                    date_doc.save()
                user.save()


            else:
                return print('nothing to unbook')

def delete_user(user=None, username=None):
    if not user and username:
        user = queries_user(username=username)
    for dates_doc in user.giorni:
        dates_doc.delete()
    user.delete()

book(username='Peppe', dates=dateList)
# un_book(username='Peppe', _all=True)
# un_book(username='Peppe', dates=[datetime.date(2020,1,6)])
user = queries_user(username='Peppe')
for date in user.giorni:
    print(date.giorni)
delete_user(user=user)
# dates = queries_dates(username='Lucio')
# dates = queries_dates(user=user)
# pprint(dates.giorni)
# for obj in User.objects():
#     print('#'*10)
#     obj.pretty_print()
#
# for obj in Date.objects():
#     print('#'*10)
#     obj.pretty_print()