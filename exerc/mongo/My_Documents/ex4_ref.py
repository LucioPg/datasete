from mongo.My_Documents.prova_ref_document import *
from datetime import datetime
from mongoengine import *
from pprint import pprint

connect('test_db', host='localhost', port=27017)
dateList = [datetime(2020,3,3), datetime(2020,3,4), datetime(2020,3,6)]


def create_user(nome):
    return User(nome=nome)  # it does not save for checking for dates during booking

def queries_user(username):
    return User.objects.get(nome=username)

def queries_dates(user):
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


book(username='Peppe', dates=dateList)


# def save(doc):
#     doc.save()

# user = User(
#     nome='Lucio'
# ).save()
#
# user = User.objects.get(nome='Lucio')
# date = Date.objects.get(user=user)
# user.giorni = date
# user.save()
# date = Date(
#     giorni=dateList,
#     user=user
# ).save()
for obj in User.objects():
    print('#'*10)
    obj.pretty_print()

for obj in Date.objects():
    print('#'*10)
    obj.pretty_print()