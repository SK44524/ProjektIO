import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
import pymongo
import requests
from io import BytesIO
from PIL import ImageTk, Image
from functools import partial
import datetime
import numpy as np
import dateutil.relativedelta




client = pymongo.MongoClient("brak")
mydb = client['Serwis_komputerowy']
mycol = mydb["Przedmioty"]
col_zlecenia = mydb["Zamowienia"]
col_klient = mydb["Klient"]
col_admin = mydb["Admin"]
col_pracownicy = mydb["Pracownik"]

def find_elements(mycol, query):
    lista = [];
    mydoc = mycol.find(query);
    for x in mydoc:
        lista.append(x);
    return lista;

myquery = {"Typ": "CPU"}
myquery2 = {"Typ" : "MOBO"}
myquery3 = {"Typ" : "GPU"}
myquery4 = {"Typ" : "RAM"}
myquery5 = {"Typ" : "Obudowa"}
myquery6 = {"Typ" : "Zasilacz"}
myquery7 = {"Typ" : "Chlodzenie"}
myquery8 = {"$or":[ {"Typ": "HDD"}, {"Typ": "SSD"}]}


#pprint(find_elements(mycol, myquery8))



class Klient:
    def __init__(self):
        self.id = col_klient.find_one()["_id"]
        self.imie = col_klient.find_one()["Imie"]
        self.nazwisko = col_klient.find_one()["Nazwisko"]
        self.koszyk_dict = {"CPU" : None, "MOBO" : None, "GPU" : None, "RAM" : None, "Obudowa" : None, "Zasilacz" : None, "Chlodzenie" : None, "Dysk" : None}
        self.suma = 0
        self.query = {"_id_klienta" : self.id}
        self.__numer_telefonu = None
        self.__email = None

    def zamow(self, items):
        mycol = mydb["Zamowienia"]
        mycol1 = mydb["Przedmioty"]
        new_id = 0
        for x in mycol.find({}, {"_id": 1}):
            new_id = x['_id']
        new_id = new_id + 1
        time = datetime.datetime.now()
        mylist = []
        suma = 0
        for i in items:
            mylist.append({'_id_przedmiotu': i})
            myquery = {"_id": i}
            rekord = mycol1.find(myquery)
            for x in rekord:
                suma = suma + x['cena-brutto']
        zamowienie = {"_id": new_id, "_id_klienta": self.id, "data": time, "status": "Nowe", "Przypisany pracownik": False,
                      "Numer_pracownika": 0, "Zamowione_przedmioty": mylist, "Cena_koncowa": suma}
        mycol.insert_one(zamowienie)
        for i in items:
            myquery = {"_id": i}
            rekord = mycol1.find(myquery)
            for x in rekord:
                il_sztuk = x['Il_sztuk']
            il_sztuk = il_sztuk - 1
            new_values = {"$set": {"Il_sztuk": il_sztuk}}
            mycol1.update_one(myquery, new_values)

    def licz_sume(self, items):
        mylist = []
        mycol1 = mydb["Przedmioty"]
        suma = 0
        for i in items:
            mylist.append({'_id_przedmiotu': i})
            myquery = {"_id": i}
            rekord = mycol1.find(myquery)
            for x in rekord:
                suma = suma + x['cena-brutto']
        self.suma = suma
    def wyloguj(self):
        pass
    def zaloguj_sie(self):
        pass


class Admin:
    def __init__(self):
        self.id = col_admin.find_one()["_id"]
        self.imie = col_admin.find_one()["Imie"]
        self.nazwisko = col_admin.find_one()["Nazwisko"]
        self.__numer_telefonu = None
        self.__email = None
        self.stopien = None

    def przypisz(self, id, worker_id):
        mycol = mydb["Zamowienia"]
        new_values = {"$set": {"Przypisany pracownik": True, "Numer_pracownika": worker_id,
                      "status": "Przypisany pracownik"}}
        myquery = {"_id": id};
        mycol.update_one(myquery, new_values)
    def wyloguj(self):
        pass
    def zaloguj_sie(self):
        pass


class Pracownik:
    def __init__(self):
        self.id = col_pracownicy.find_one()["_id"]
        self.imie = col_pracownicy.find_one()["Imie"]
        self.nazwisko = col_pracownicy.find_one()["Nazwisko"]
        self.__numer_telefonu = None
        self.__email = None
        self.numer_stanowiska = None
        self.specjalizacja = None

    def zmien_status(self, id, status):
        mycol = mydb["Zamowienia"]
        myquery = {"_id": id};
        new_values = {"$set": {"status": status}}
        mycol.update_one(myquery, new_values)
    def nawiaz_kontakt(self):
        pass
    def zaakceptuj_zlecenie(self):
        pass

# ADMIN SEKCJA: ______________________________________________________________________

def admin():

    admin1 = Admin()

    def przejdz_do_przypisz():
        okno.destroy()
        przypisz_zamowienia(admin1)

    def przejdz_do_wszystkie():
        okno.destroy()
        zamowienia_wszystkie('nie')

    okno = tk.Toplevel(root)
    tlo2 = tk.Canvas(okno, height = 1000, width = 1600, bg = 'white')
    tlo2.pack()
    powitanie = tk.Label(okno, text = 'Interfejs Admina:', bg = 'blue', fg = 'yellow', font = myFont)
    powitanie.place(relx = 0.25, rely = 0.1, relwidth = 0.5, relheight = 0.1)

    button1 = tk.Button(okno, text='PRZYPISZ ZAMÓWIENIE', font=myFont, fg='blue', activebackground='blue', bg='white',
                        height=150, width=150, relief='solid', command = przejdz_do_przypisz)
    button1.place(relx=0.05, rely=0.4, relwidth=0.25, relheight=0.3)

    button2 = tk.Button(okno, text='ZAMÓWIENIA', font=myFont, fg='blue', activebackground='blue', bg='white', height=150,
                        width=150, relief='solid', command = przejdz_do_wszystkie)
    button2.place(relx=0.375, rely=0.4, relwidth=0.25, relheight=0.3)

    button2 = tk.Button(okno, text='Wyloguj', font=myFont, fg='blue', activebackground='blue', bg='white', height=150,
                        width=150, relief='solid', command = okno.destroy)
    button2.place(relx=0.7, rely=0.4, relwidth=0.25, relheight=0.3)

def przypisz_zamowienia(admin1):

    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    def przejdz_do_przypisanych():
        okno_k.destroy()
        zmien_przypisania(admin1)

    def cofnij():
        okno_k.destroy()
        admin()


    but_powrot = tk.Button(okno_k, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)

    powitanie = tk.Label(okno_k, text='ZLECENIA W SYSTEMIE:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.1)

    but_przypisane = tk.Button(okno_k, text='Zmien przypisane', font=myFont, bg='blue', fg='yellow', command = przejdz_do_przypisanych)
    but_przypisane.place(relx=0.75, rely=0.05, relwidth=0.2, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def przejdz_do_okna_przypisania(id):
        okno_k.destroy()
        okno_przypisania(admin1, id)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    queryLOL = {"Przypisany pracownik" : False}

    row_nr = 1
    for i in find_elements(col_zlecenia, queryLOL):
        frame1 = tk.Frame(scrollable_frame, height=250, width=1600)
        but2 = tk.Button(frame1, text=("ID: ", i["_id"], "Cena: ", i["Cena_koncowa"], "Status: ", i["status"]),
                         bg='white', fg='blue', font=myFont, command=partial(przejdz_do_okna_przypisania, i["_id"]))
        but2.pack(fill='both', expand=1)
        frame1.pack_propagate(0)
        frame1.grid(column=1, row=row_nr)
        row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def zmien_przypisania(admin1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    def cofnij():
        okno_k.destroy()
        przypisz_zamowienia(admin1)

    powitanie = tk.Label(okno_k, text='ZLECENIA PRZYPISANE:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.1)

    but_powrot = tk.Button(okno_k, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def przejdz_do_okna_przypisania(id):
        okno_k.destroy()
        okno_przypisania(admin1, id)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    queryLOL = {"Przypisany pracownik": True}

    row_nr = 1
    for i in find_elements(col_zlecenia, queryLOL):
        if (i["status"] != 'Zakonczone'):
            frame1 = tk.Frame(scrollable_frame, height=250, width=1600)
            but2 = tk.Button(frame1, text=("ID: ", i["_id"], "Cena: ", i["Cena_koncowa"], "Status: ", i["status"]),
                             bg='white', fg='blue', font=myFont, command=partial(przejdz_do_okna_przypisania, i["_id"]))
            but2.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def okno_przypisania(admin1, id):


    def order_details(id):
        mycol = mydb["Zamowienia"]
        mycol1 = mydb["Przedmioty"]
        myquery = {"_id": id}
        el = find_elements(mycol, myquery)
        items_id = []
        for i in el[0]['Zamowione_przedmioty']:
            items_id.append(i['_id_przedmiotu'])
        item_list = []
        item_list.append({"Numer_zamowienia": id})
        for i in items_id:
            myquery = {"_id": i}
            item_list.append(find_elements(mycol1, myquery)[0])
        return item_list

    def pop_przypisz(id_w):

        def add():
            print(id)
            print(id_w)
            admin1.przypisz(id, id_w)
            okienko.destroy()
            okno_k.destroy()
            przypisz_zamowienia(admin1)

        okienko = tk.Toplevel(okno_k, bd = 100)
        warning = tk.Label(okienko, text = 'Czy chcesz przypisać zamowienie?')
        warning.pack(side = 'top')
        tak = tk.Button(okienko, text = 'TAK', width = 10, command = add)
        tak.pack(side = 'left')
        nie = tk.Button(okienko, text='NIE', width = 10, command = okienko.destroy)
        nie.pack(side='right')

    lista = order_details(id)

    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    queryXD = {"_id": id}

    powitanie = tk.Label(okno_k, text=('Numer zamowienia: ' , lista[0]["Numer_zamowienia"], "Status: ", find_elements(col_zlecenia , queryXD)[0]["status"]), font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0, rely=0.05, relwidth=1, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1


    for i in col_pracownicy.find():
        frame1 = tk.Frame(scrollable_frame, height=250, width=1200)
        frame2 = tk.Frame(scrollable_frame, height=250, width=400)
        but2 = tk.Button(frame1, text = ("Imie:", i["Imie"] ,"Nazwisko:", i["Nazwisko"],"ID:", i["_id"]), bg='white', fg='blue', font=myFont2)
        but2.pack(fill='both', expand=1)
        frame1.pack_propagate(0)
        frame1.grid(column=1, row=row_nr)
        but3 = tk.Button(frame2, text="Przypisz zamowienie", bg='white',fg='blue', font=myFont2, command = partial(pop_przypisz, i["_id"]))
        but3.pack(fill='both', expand=1)
        frame2.pack_propagate(0)
        frame2.grid(column=2, row=row_nr)
        row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def zamowienia_wszystkie(czymiesiac):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    def cofnij():
        okno_k.destroy()
        admin()

    def przejdz_do_miesiac(switch):
        okno_k.destroy()
        zamowienia_wszystkie(switch)

    powitanie = tk.Label(okno_k, text='ZLECENIA W SYSTEMIE:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.1)

    but_powrot = tk.Button(okno_k, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)

    if (czymiesiac == 'nie'):
        but_ostatnie = tk.Button(okno_k, text='Ostatni miesiąc', font=myFont, bg='blue', fg='yellow', command=partial(przejdz_do_miesiac, 'tak'))
        but_ostatnie.place(relx=0.75, rely=0.05, relwidth=0.2, relheight=0.1)
    else:
        but_ostatnie = tk.Button(okno_k, text='Wszystkie', font=myFont, bg='blue', fg='yellow', command=partial(przejdz_do_miesiac, 'nie'))
        but_ostatnie.place(relx=0.75, rely=0.05, relwidth=0.2, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in col_zlecenia.find():
        if (czymiesiac == 'tak' and i["data"] >= datetime.datetime.today() - dateutil.relativedelta.relativedelta(months=1)) or czymiesiac == 'nie':
            frame1 = tk.Frame(scrollable_frame, height=250, width=1600)
            but2 = tk.Button(frame1, text=("ID: ", i["_id"], "Cena: ", i["Cena_koncowa"], "Status: ", i["status"], "Data i czas wpłynięcia: ", i["data"]), bg='white', fg='blue', font=myFont, command = partial(szczegoly_zlecen, i["_id"]))
            but2.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

#  ____________________________________________________________________________________

# PRACOWNIK SEKCJA: ___________________________________________________________________

def pracownik():

    pracownik1 = Pracownik()

    def przejdz_do_przypisanych():
        okno.destroy()
        przypisane_do_ciebie(pracownik1)

    okno = tk.Toplevel(root)
    tlo2 = tk.Canvas(okno, height = 1000, width = 1600, bg = 'white')
    tlo2.pack()
    powitanie = tk.Label(okno, text = 'Interfejs Pracownika:', bg = 'blue', fg = 'yellow', font = myFont)
    powitanie.place(relx = 0.25, rely = 0.1, relwidth = 0.5, relheight = 0.1)

    button2 = tk.Button(okno, text='PRZYPISANE', font=myFont, fg='blue', activebackground='blue', bg='white',height=150,width=150, relief='solid', command = przejdz_do_przypisanych)
    button2.place(relx=0.2, rely=0.4, relwidth=0.25, relheight=0.3)

    button2 = tk.Button(okno, text='Wyloguj', font=myFont, fg='blue', activebackground='blue', bg='white', height=150,width=150, relief='solid', command = okno.destroy)
    button2.place(relx=0.55, rely=0.4, relwidth=0.25, relheight=0.3)

def przypisane_do_ciebie(pracownik1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    def cofnij():
        okno_k.destroy()
        pracownik()


    powitanie = tk.Label(okno_k, text='ZLECENIA PRZYPISANE:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.1)

    but_powrot = tk.Button(okno_k, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def przejdz_do_szczegolow(id):
        okno_k.destroy()
        pracownik_zlecenie_szczegoly(pracownik1, id)



    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    queryLOL = {"Numer_pracownika": pracownik1.id}

    row_nr = 1
    for i in find_elements(col_zlecenia, queryLOL):
        if (i["status"] != 'Zakonczone'):
            frame1 = tk.Frame(scrollable_frame, height=250, width=1600)
            but2 = tk.Button(frame1, text=("ID: ", i["_id"], "Status: ", i["status"]), bg='white', fg='blue', font=myFont, command = partial(przejdz_do_szczegolow, i["_id"]))
            but2.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def pracownik_zlecenie_szczegoly(pracownik1, id):
    def order_details(id):
        mycol = mydb["Zamowienia"]
        mycol1 = mydb["Przedmioty"]
        myquery = {"_id": id}
        el = find_elements(mycol, myquery)
        items_id = []
        for i in el[0]['Zamowione_przedmioty']:
            items_id.append(i['_id_przedmiotu'])
        item_list = []
        item_list.append({"Numer_zamowienia": id})
        for i in items_id:
            myquery = {"_id": i}
            item_list.append(find_elements(mycol1, myquery)[0])
        return item_list

    lista = order_details(id)

    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    queryXD = {"_id": id}

    def opcje_zmiany():

        def zmien(opcja):
            okienko.destroy()
            pracownik1.zmien_status(id, opcja)
            okno_k.destroy()
            przypisane_do_ciebie(pracownik1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Zmien status na :')
        warning.pack(side='top')
        opcja1 = tk.Button(okienko, text='Przypisany pracownik', width=15, command = partial(zmien, 'Przypisany pracownik'))
        opcja1.pack(side='left')
        opcja2 = tk.Button(okienko, text='Kompletowanie', width=15, command = partial(zmien, 'Kompletowanie'))
        opcja2.pack(side='left')
        opcja3 = tk.Button(okienko, text='Składanie', width=15, command = partial(zmien, 'Składanie'))
        opcja3.pack(side='left')
        opcja4 = tk.Button(okienko, text='Zakonczone', width=15, command = partial(zmien, 'Zakonczone'))
        opcja4.pack(side='left')

    def cofnij():
        okno_k.destroy()
        przypisane_do_ciebie(pracownik1)

    powitanie = tk.Label(okno_k, text=('Numer zamowienia: ' , lista[0]["Numer_zamowienia"], "Status: ", find_elements(col_zlecenia , queryXD)[0]["status"]), font=myFont2, bg='blue', fg='yellow')
    powitanie.place(relx=0.2, rely=0.05, relwidth=0.6, relheight=0.1)

    but_zmien_status = tk.Button(okno_k, text= 'Zmien status', font=myFont2, bg='blue', fg='yellow', command = opcje_zmiany)
    but_zmien_status.place(relx=0.85, rely=0.05, relwidth=0.1, relheight=0.1)

    but_powrot = tk.Button(okno_k, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1


    for i in range(1,len(lista)):
        frame1 = tk.Frame(scrollable_frame, height=250, width=1200)
        response = requests.get(lista[i]['IMG'])
        obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
        but = tk.Label(scrollable_frame, image=obrazek)
        but.photo = obrazek
        but.grid(column=2, row=row_nr)
        but2 = tk.Label(frame1, text = ("Typ:", lista[i]["Typ"] ,"Model:", lista[i]["name"]), bg='white', fg='blue', font=myFont2)
        but2.pack(fill='both', expand=1)
        frame1.pack_propagate(0)
        frame1.grid(column=1, row=row_nr)
        row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)



# _____________________________________________________________________________________

# KLIENT SEKCJA _______________________________________________________________________

def klient_wejscie():
    klient1 = Klient()

    okno = tk.Toplevel(root)

    def listacat():
        klient_listacat(klient1)
        okno.destroy()

    def zamknij():
        okno.destroy()

    def przejdz_do_zlecenie():
        okno.destroy()
        klient_zlecenie(klient1)

    canvas= tk.Canvas(okno, height = 1000, width = 1600, bg='white')
    canvas.pack()

    powitanie = tk.Label(okno, text='Interfejs Klienta:',font = myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    button1 = tk.Button(okno,text = 'ZAMÓW CZĘŚCI',font = myFont, fg = 'blue', activebackground='blue', bg='white', height=150, width=150, command=listacat, relief = 'solid')
    button1.place(relx=0.05, rely=0.4, relwidth=0.25, relheight=0.3)

    button2 = tk.Button(okno, text='ZLECENIE',font = myFont, fg='blue', activebackground='blue', bg='white', height=150, width=150, command=przejdz_do_zlecenie, relief = 'solid')
    button2.place(relx=0.375, rely=0.4, relwidth=0.25, relheight=0.3)

    button2 = tk.Button(okno, text='Wyloguj',font = myFont, fg='blue', activebackground='blue', bg='white', height=150, width=150, command=zamknij, relief='solid')
    button2.place(relx=0.7, rely=0.4, relwidth=0.25, relheight=0.3)

def szczegoly_zlecen(id):

    def order_details(id):
        mycol = mydb["Zamowienia"]
        mycol1 = mydb["Przedmioty"]
        myquery = {"_id": id}
        el = find_elements(mycol, myquery)
        items_id = []
        for i in el[0]['Zamowione_przedmioty']:
            items_id.append(i['_id_przedmiotu'])
        item_list = []
        item_list.append({"Numer_zamowienia": id})
        for i in items_id:
            myquery = {"_id": i}
            item_list.append(find_elements(mycol1, myquery)[0])
        return item_list

    lista = order_details(id)

    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    queryXD = {"_id": id}

    powitanie = tk.Label(okno_k, text=('Numer zamowienia: ' , lista[0]["Numer_zamowienia"], "Suma: ", find_elements(col_zlecenia , queryXD)[0]["Cena_koncowa"], "Status: ", find_elements(col_zlecenia , queryXD)[0]["status"]), font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0, rely=0.05, relwidth=1, relheight=0.1)


    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1


    for i in range(1,len(lista)):
        frame1 = tk.Frame(scrollable_frame, height=250, width=1200)
        response = requests.get(lista[i]['IMG'])
        obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
        but = tk.Label(scrollable_frame, image=obrazek)
        but.photo = obrazek
        but.grid(column=2, row=row_nr)
        but2 = tk.Label(frame1, text = ("Typ:", lista[i]["Typ"] ,"Model:", lista[i]["name"],"Cena:", lista[i]["cena-brutto"]), bg='white', fg='blue', font=myFont2)
        but2.pack(fill='both', expand=1)
        frame1.pack_propagate(0)
        frame1.grid(column=1, row=row_nr)
        row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_zlecenie(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    def cofnij():
        okno_k.destroy()
        klient_wejscie()


    but_powrot = tk.Button(okno_k, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)

    powitanie = tk.Label(okno_k, text='TWOJE ZLECENIA:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def przejdz_do_szczegoly(id):
        szczegoly_zlecen(id)
        okno_k.destroy()

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(col_zlecenia, klient1.query):
        frame1 = tk.Frame(scrollable_frame, height=250, width=700)
        but2 = tk.Button(frame1, text=("ID: ",i["_id"], "Cena: " , i["Cena_koncowa"]), bg='white', fg='blue',font=myFont, command = partial(przejdz_do_szczegoly, i["_id"]))
        but2.pack(fill='both', expand=1)
        frame1.pack_propagate(0)
        frame1.grid(column=1, row=row_nr)
        row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def koszyk(klient1):

    def przelicz():
        lista = []
        for key, value in klient1.koszyk_dict.items():
            if value != None:
                lista.append(value)
        klient1.licz_sume(lista)

    przelicz()
    print(klient1.suma)

    def zamow():
        if (klient1.suma > 0):
            lista = []
            for key, value in klient1.koszyk_dict.items():
                if value != None:
                    lista.append(value)
            klient1.zamow(lista)
            for i in klient1.koszyk_dict.keys():
                klient1.koszyk_dict[i] = None
            okno.destroy()
            koszyk(klient1)

    okno = tk.Toplevel(root)

    canvas = tk.Canvas(okno, height=1000, width=1600, bg='white')
    canvas.pack()

    def cofnij():
        okno.destroy()
        klient_listacat(klient1)

    but_powrot = tk.Button(okno, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)

    powitanie = tk.Label(okno, text=('KOSZYK:', np.round(klient1.suma, 2), 'zł'), font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    zaplac = tk.Button(okno, text = 'ZAMÓW', font = myFont, bg = 'blue', fg = 'white', command = zamow)
    zaplac.place(relx=0.25, rely=0.25, relwidth=0.5, relheight=0.1)

    container = ttk.Frame(okno)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    def przejdz_do_listy_proc():
        klient_lista_proc(klient1)
        okno.destroy()

    def przejdz_do_listy_mobo():
        klient_lista_plyt(klient1)
        okno.destroy()

    def przejdz_do_listy_dysk():
        klient_lista_dysk(klient1)
        okno.destroy()

    def przejdz_do_listy_ram():
        klient_lista_pamiec(klient1)
        okno.destroy()

    def przejdz_do_listy_power():
        klient_lista_zasilacz(klient1)
        okno.destroy()

    def przejdz_do_listy_obudowa():
        klient_lista_obud(klient1)
        okno.destroy()

    def przejdz_do_listy_cool():
        klient_lista_chlod(klient1)
        okno.destroy()

    def przejdz_do_listy_gpu():
        klient_lista_karta(klient1)
        okno.destroy()

    def usun_element(arg):
        klient1.koszyk_dict[arg] = None
        okno.destroy()
        koszyk(klient1)



    # procesory:

    frame1_proc = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_proc = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_proc = tk.Frame(scrollable_frame, height=250, width=400)

    label1_proc = tk.Label(frame1_proc, text = 'procesor: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["CPU"] == None:
        but2_proc = tk.Button(frame2_proc, text = '(dodaj)', bg='white', fg='blue', font=myFont, command = przejdz_do_listy_proc)
    else:
        but2_proc = tk.Button(frame2_proc, text= find_elements(mycol,{"_id" : klient1.koszyk_dict["CPU"]})[0]["name"], bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_proc)
    but3_proc = tk.Button(frame3_proc, text = '(usuń)', bg='white', fg='blue', font=myFont, command = partial(usun_element, "CPU"))

    label1_proc.pack(fill='both', expand=1)
    but2_proc.pack(fill='both', expand=1)
    but3_proc.pack(fill='both', expand=1)

    frame1_proc.pack_propagate(0)
    frame2_proc.pack_propagate(0)
    frame3_proc.pack_propagate(0)

    frame1_proc.grid(column=1, row=1)
    frame2_proc.grid(column=2, row=1)
    frame3_proc.grid(column=3, row=1)

    # płyty:

    frame1_mobo = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_mobo = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_mobo = tk.Frame(scrollable_frame, height=250, width=400)

    label1_mobo = tk.Label(frame1_mobo, text='płyta główna: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["MOBO"] == None:
        but2_mobo = tk.Button(frame2_mobo, text='(dodaj)', bg='white', fg='blue', font=myFont,
                              command=przejdz_do_listy_mobo)
    else:
        but2_mobo = tk.Button(frame2_mobo, text=find_elements(mycol, {"_id": klient1.koszyk_dict["MOBO"]})[0]["name"],
                              bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_mobo)
    but3_mobo = tk.Button(frame3_mobo, text='(usuń)', bg='white', fg='blue', font=myFont,
                          command=partial(usun_element, "MOBO"))

    label1_mobo.pack(fill='both', expand=1)
    but2_mobo.pack(fill='both', expand=1)
    but3_mobo.pack(fill='both', expand=1)

    frame1_mobo.pack_propagate(0)
    frame2_mobo.pack_propagate(0)
    frame3_mobo.pack_propagate(0)

    frame1_mobo.grid(column=1, row=2)
    frame2_mobo.grid(column=2, row=2)
    frame3_mobo.grid(column=3, row=2)

    # dyski:

    frame1_drive = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_drive = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_drive = tk.Frame(scrollable_frame, height=250, width=400)

    label1_drive = tk.Label(frame1_drive, text='dysk: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["Dysk"] == None:
        but2_drive = tk.Button(frame2_drive, text='(dodaj)', bg='white', fg='blue', font=myFont,
                              command=przejdz_do_listy_dysk)
    else:
        but2_drive = tk.Button(frame2_drive, text=find_elements(mycol, {"_id": klient1.koszyk_dict["Dysk"]})[0]["name"],
                              bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_dysk)
    but3_drive = tk.Button(frame3_drive, text='(usuń)', bg='white', fg='blue', font=myFont,
                          command=partial(usun_element, "Dysk"))

    label1_drive.pack(fill='both', expand=1)
    but2_drive.pack(fill='both', expand=1)
    but3_drive.pack(fill='both', expand=1)

    frame1_drive.pack_propagate(0)
    frame2_drive.pack_propagate(0)
    frame3_drive.pack_propagate(0)

    frame1_drive.grid(column=1, row=3)
    frame2_drive.grid(column=2, row=3)
    frame3_drive.grid(column=3, row=3)

    # karty:

    frame1_gpu = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_gpu = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_gpu = tk.Frame(scrollable_frame, height=250, width=400)

    label1_gpu = tk.Label(frame1_gpu, text='karta graficzna: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["GPU"] == None:
        but2_gpu = tk.Button(frame2_gpu, text='(dodaj)', bg='white', fg='blue', font=myFont,
                               command=przejdz_do_listy_gpu)
    else:
        but2_gpu = tk.Button(frame2_gpu, text=find_elements(mycol, {"_id": klient1.koszyk_dict["GPU"]})[0]["name"],
                               bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_gpu)
    but3_gpu = tk.Button(frame3_gpu, text='(usuń)', bg='white', fg='blue', font=myFont,
                           command=partial(usun_element, "GPU"))

    label1_gpu.pack(fill='both', expand=1)
    but2_gpu.pack(fill='both', expand=1)
    but3_gpu.pack(fill='both', expand=1)

    frame1_gpu.pack_propagate(0)
    frame2_gpu.pack_propagate(0)
    frame3_gpu.pack_propagate(0)

    frame1_gpu.grid(column=1, row=4)
    frame2_gpu.grid(column=2, row=4)
    frame3_gpu.grid(column=3, row=4)

    # chłodzenia:

    frame1_cool = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_cool = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_cool = tk.Frame(scrollable_frame, height=250, width=400)

    label1_cool = tk.Label(frame1_cool, text='chłodzenie: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["Chlodzenie"] == None:
        but2_cool = tk.Button(frame2_cool, text='(dodaj)', bg='white', fg='blue', font=myFont,
                             command=przejdz_do_listy_cool)
    else:
        but2_cool = tk.Button(frame2_cool, text=find_elements(mycol, {"_id": klient1.koszyk_dict["Chlodzenie"]})[0]["name"],
                             bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_cool)
    but3_cool = tk.Button(frame3_cool, text='(usuń)', bg='white', fg='blue', font=myFont,
                         command=partial(usun_element, "Chlodzenie"))

    label1_cool.pack(fill='both', expand=1)
    but2_cool.pack(fill='both', expand=1)
    but3_cool.pack(fill='both', expand=1)

    frame1_cool.pack_propagate(0)
    frame2_cool.pack_propagate(0)
    frame3_cool.pack_propagate(0)

    frame1_cool.grid(column=1, row=5)
    frame2_cool.grid(column=2, row=5)
    frame3_cool.grid(column=3, row=5)

    # zasilacze:

    frame1_power = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_power = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_power = tk.Frame(scrollable_frame, height=250, width=400)

    label1_power = tk.Label(frame1_power, text='zasilacz: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["Zasilacz"] == None:
        but2_power = tk.Button(frame2_power, text='(dodaj)', bg='white', fg='blue', font=myFont,
                              command=przejdz_do_listy_power)
    else:
        but2_power = tk.Button(frame2_power, text=find_elements(mycol, {"_id": klient1.koszyk_dict["Zasilacz"]})[0]["name"],
                              bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_power)
    but3_power = tk.Button(frame3_power, text='(usuń)', bg='white', fg='blue', font=myFont,
                          command=partial(usun_element, "Zasilacz"))

    label1_power.pack(fill='both', expand=1)
    but2_power.pack(fill='both', expand=1)
    but3_power.pack(fill='both', expand=1)

    frame1_power.pack_propagate(0)
    frame2_power.pack_propagate(0)
    frame3_power.pack_propagate(0)

    frame1_power.grid(column=1, row=6)
    frame2_power.grid(column=2, row=6)
    frame3_power.grid(column=3, row=6)

    # pamiec:

    frame1_mem = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_mem = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_mem = tk.Frame(scrollable_frame, height=250, width=400)

    label1_mem = tk.Label(frame1_mem, text='pamiec ram: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["RAM"] == None:
        but2_mem = tk.Button(frame2_mem, text='(dodaj)', bg='white', fg='blue', font=myFont,
                               command=przejdz_do_listy_ram)
    else:
        but2_mem = tk.Button(frame2_mem, text=find_elements(mycol, {"_id": klient1.koszyk_dict["RAM"]})[0]["name"],
                               bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_ram)
    but3_mem = tk.Button(frame3_mem, text='(usuń)', bg='white', fg='blue', font=myFont,
                           command=partial(usun_element, "RAM"))

    label1_mem.pack(fill='both', expand=1)
    but2_mem.pack(fill='both', expand=1)
    but3_mem.pack(fill='both', expand=1)

    frame1_mem.pack_propagate(0)
    frame2_mem.pack_propagate(0)
    frame3_mem.pack_propagate(0)

    frame1_mem.grid(column=1, row=7)
    frame2_mem.grid(column=2, row=7)
    frame3_mem.grid(column=3, row=7)

    # obudowa:

    frame1_case = tk.Frame(scrollable_frame, height=250, width=400)
    frame2_case = tk.Frame(scrollable_frame, height=250, width=700)
    frame3_case = tk.Frame(scrollable_frame, height=250, width=400)

    label1_case = tk.Label(frame1_case, text='obudowa: ', bg='white', fg='blue', font=myFont)
    if klient1.koszyk_dict["Obudowa"] == None:
        but2_case = tk.Button(frame2_case, text='(dodaj)', bg='white', fg='blue', font=myFont,
                             command=przejdz_do_listy_obudowa)
    else:
        but2_case = tk.Button(frame2_case, text=find_elements(mycol, {"_id": klient1.koszyk_dict["Obudowa"]})[0]["name"],
                             bg='white', fg='blue', font=myFont2, command=przejdz_do_listy_obudowa)
    but3_case = tk.Button(frame3_case, text='(usuń)', bg='white', fg='blue', font=myFont,
                         command=partial(usun_element, "Obudowa"))

    label1_case.pack(fill='both', expand=1)
    but2_case.pack(fill='both', expand=1)
    but3_case.pack(fill='both', expand=1)

    frame1_case.pack_propagate(0)
    frame2_case.pack_propagate(0)
    frame3_case.pack_propagate(0)

    frame1_case.grid(column=1, row=8)
    frame2_case.grid(column=2, row=8)
    frame3_case.grid(column=3, row=8)



    container.place(relx=0, rely=0.4, relwidth=1, relheight=0.6)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_proc(klient1):
    okno_k = tk.Toplevel(root)


    tlo2 = tk.Canvas(okno_k, height = 1000, width = 1600, bg = 'white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Procesory:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):

        def add():
            klient1.koszyk_dict["CPU"] = arg
            print(klient1.koszyk_dict)
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd = 100)
        warning = tk.Label(okienko, text = 'Czy chcesz dodac do koszyka?')
        warning.pack(side = 'top')
        tak = tk.Button(okienko, text = 'TAK', width = 10, command = add)
        tak.pack(side = 'left')
        nie = tk.Button(okienko, text='NIE', width = 10, command = okienko.destroy)
        nie.pack(side='right')

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)



    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)


    row_nr = 1
    for i in find_elements(mycol, myquery):
        if(klient1.koszyk_dict["MOBO"] != None and find_elements(mycol,{"_id": klient1.koszyk_dict["MOBO"]})[0]["Socket"] == i["Socket"]) or klient1.koszyk_dict["MOBO"] == None:
            if (i["Il_sztuk"] > 0):
                response = requests.get(i['IMG'])
                obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
                frame1 = tk.Frame(scrollable_frame, height = 250, width = 700)
                frame2 = tk.Frame(scrollable_frame, height=250, width=700)
                but = tk.Button(scrollable_frame, image = obrazek)
                but2 = tk.Button(frame1, text = (i['name'], '  cena:  ' ,i['cena-brutto']), bg = 'white', fg = 'blue', font = myFont2, command = partial(add_to_cart_pop, i['_id']))
                but3 = tk.Button(frame2, text = ' DODAJ DO KOSZYKA ', bg = 'white', fg = 'blue', font = myFont, command = partial(add_to_cart_pop, i['_id']))
                but.photo = obrazek
                but.grid(column = 2, row = row_nr)
                but2.pack(fill='both', expand=1)
                but3.pack(fill='both', expand=1)
                frame1.pack_propagate(0)
                frame1.grid(column=1, row=row_nr)
                frame2.pack_propagate(0)
                frame2.grid(column=3, row=row_nr)
                row_nr = row_nr + 1


    container.place(relx = 0, rely = 0.2, relwidth = 1, relheight = 0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_dysk(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Dyski:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["Dysk"] = arg
            print(klient1.koszyk_dict)
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(mycol, myquery8):
        if (i["Il_sztuk"] > 0):
            response = requests.get(i['IMG'])
            obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
            frame1 = tk.Frame(scrollable_frame, height=250, width=700)
            frame2 = tk.Frame(scrollable_frame, height=250, width=700)
            but = tk.Button(scrollable_frame, image=obrazek)
            but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2, command=partial(add_to_cart_pop, i["_id"]))
            but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop, i["_id"]))
            but.photo = obrazek
            but.grid(column=2, row=row_nr)
            but2.pack(fill='both', expand=1)
            but3.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            frame2.pack_propagate(0)
            frame2.grid(column=3, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_plyt(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Płyty główne:', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["MOBO"] = arg
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.configure(xscrollcommand=scrollbar2.set)

    row_nr = 1
    for i in find_elements(mycol, myquery2):
        if (klient1.koszyk_dict["CPU"] != None and find_elements(mycol, {"_id": klient1.koszyk_dict["CPU"]})[0]["Socket"] == i["Socket"]) or klient1.koszyk_dict["CPU"] == None:
            if (i["Il_sztuk"] > 0):
                response = requests.get(i['IMG'])
                obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
                frame1 = tk.Frame(scrollable_frame, height=250, width=700)
                frame2 = tk.Frame(scrollable_frame, height=250, width=700)
                but = tk.Button(scrollable_frame, image=obrazek)
                but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2,
                                 command=partial(add_to_cart_pop,i["_id"]))
                but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop,i["_id"]))
                but.photo = obrazek
                but.grid(column=2, row=row_nr)
                but2.pack(fill='both', expand=1)
                but3.pack(fill='both', expand=1)
                frame1.pack_propagate(0)
                frame1.grid(column=1, row=row_nr)
                frame2.pack_propagate(0)
                frame2.grid(column=3, row=row_nr)
                row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_pamiec(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Pamieci ram :', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["RAM"] = arg
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(mycol, myquery4):
        if (i["Il_sztuk"] > 0):
            response = requests.get(i['IMG'])
            obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
            frame1 = tk.Frame(scrollable_frame, height=250, width=700)
            frame2 = tk.Frame(scrollable_frame, height=250, width=700)
            but = tk.Button(scrollable_frame, image=obrazek)
            but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2,
                             command=partial(add_to_cart_pop,i["_id"]))
            but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop,i["_id"]))
            but.photo = obrazek
            but.grid(column=2, row=row_nr)
            but2.pack(fill='both', expand=1)
            but3.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            frame2.pack_propagate(0)
            frame2.grid(column=3, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_zasilacz(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Zasilacze: ', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["Zasilacz"] = arg
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(mycol, myquery6):
        if (i["Il_sztuk"] > 0):
            response = requests.get(i['IMG'])
            obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
            frame1 = tk.Frame(scrollable_frame, height=250, width=700)
            frame2 = tk.Frame(scrollable_frame, height=250, width=700)
            but = tk.Button(scrollable_frame, image=obrazek)
            but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2,
                             command=partial(add_to_cart_pop,i["_id"]))
            but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop,i["_id"]))
            but.photo = obrazek
            but.grid(column=2, row=row_nr)
            but2.pack(fill='both', expand=1)
            but3.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            frame2.pack_propagate(0)
            frame2.grid(column=3, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_obud(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Obudowy: ', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["Obudowa"] = arg
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(mycol, myquery5):
        if (i["Il_sztuk"] > 0):
            response = requests.get(i['IMG'])
            obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
            frame1 = tk.Frame(scrollable_frame, height=250, width=700)
            frame2 = tk.Frame(scrollable_frame, height=250, width=700)
            but = tk.Button(scrollable_frame, image=obrazek)
            but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2,
                             command=partial(add_to_cart_pop,i["_id"]))
            but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop,i["_id"]))
            but.photo = obrazek
            but.grid(column=2, row=row_nr)
            but2.pack(fill='both', expand=1)
            but3.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            frame2.pack_propagate(0)
            frame2.grid(column=3, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_karta(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Karty graficzne: ', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["GPU"] = arg
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(mycol, myquery3):
        if (i["Il_sztuk"] > 0):
            response = requests.get(i['IMG'])
            obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
            frame1 = tk.Frame(scrollable_frame, height=250, width=700)
            frame2 = tk.Frame(scrollable_frame, height=250, width=700)
            but = tk.Button(scrollable_frame, image=obrazek)
            but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2,
                             command=partial(add_to_cart_pop,i["_id"]))
            but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop,i["_id"]))
            but.photo = obrazek
            but.grid(column=2, row=row_nr)
            but2.pack(fill='both', expand=1)
            but3.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            frame2.pack_propagate(0)
            frame2.grid(column=3, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_lista_chlod(klient1):
    okno_k = tk.Toplevel(root)

    tlo2 = tk.Canvas(okno_k, height=1000, width=1600, bg='white')
    tlo2.pack()

    powitanie = tk.Label(okno_k, text='Chlodzenia: ', font=myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    def add_to_cart_pop(arg):
        def add():
            klient1.koszyk_dict["Chlodzenie"] = arg
            okienko.destroy()
            okno_k.destroy()
            klient_listacat(klient1)

        okienko = tk.Toplevel(okno_k, bd=100)
        warning = tk.Label(okienko, text='Czy chcesz dodac do koszyka?')
        warning.pack(side='top')
        tak = tk.Button(okienko, text='TAK', width=10, command=add)
        tak.pack(side='left')
        nie = tk.Button(okienko, text='NIE', width=10, command=okienko.destroy)
        nie.pack(side='right')

    container = ttk.Frame(okno_k)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    def wroc():
        okno_k.destroy()
        klient_listacat(klient1)

    powrot = tk.Button(okno_k, text='WRÓĆ', font=myFont, bg='blue', fg='yellow', command = wroc)
    powrot.place(relx=0.05, rely=0.05, relwidth=0.1, relheight=0.1)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    row_nr = 1
    for i in find_elements(mycol, myquery7):
        if (i["Il_sztuk"] > 0):
            response = requests.get(i['IMG'])
            obrazek = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((250, 250), Image.ANTIALIAS))
            frame1 = tk.Frame(scrollable_frame, height=250, width=700)
            frame2 = tk.Frame(scrollable_frame, height=250, width=700)
            but = tk.Button(scrollable_frame, image=obrazek)
            but2 = tk.Button(frame1, text=(i['name'], '  cena:  ', i['cena-brutto']), bg='white', fg='blue', font=myFont2,
                             command=partial(add_to_cart_pop,i["_id"]))
            but3 = tk.Button(frame2, text=' DODAJ DO KOSZYKA ', bg='white', fg='blue', font=myFont, command=partial(add_to_cart_pop,i["_id"]))
            but.photo = obrazek
            but.grid(column=2, row=row_nr)
            but2.pack(fill='both', expand=1)
            but3.pack(fill='both', expand=1)
            frame1.pack_propagate(0)
            frame1.grid(column=1, row=row_nr)
            frame2.pack_propagate(0)
            frame2.grid(column=3, row=row_nr)
            row_nr = row_nr + 1

    container.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)
    scrollbar.pack(side="right", fill="y")
    scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar2.set)
    scrollbar2.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

def klient_listacat(klient1):
    okno = tk.Toplevel(root)

    def listap():
        klient_lista_proc(klient1)
        okno.destroy()

    def listad():
        klient_lista_dysk(klient1)
        okno.destroy()

    def listaplyt():
        klient_lista_plyt(klient1)
        okno.destroy()

    def listakart():
        klient_lista_karta(klient1)
        okno.destroy()

    def listacool():
        klient_lista_chlod(klient1)
        okno.destroy()

    def listapow():
        klient_lista_zasilacz(klient1)
        okno.destroy()

    def listaobud():
        klient_lista_obud(klient1)
        okno.destroy()

    def listaram():
        klient_lista_pamiec(klient1)
        okno.destroy()

    def przejdz_do_koszyk(klient1):
        koszyk(klient1)
        okno.destroy()

    canvas = tk.Canvas(okno, height=1000, width=1600, bg='white')
    canvas.pack()

    def cofnij():
        okno.destroy()
        klient_wejscie()

    but_powrot = tk.Button(okno, text='Wroc', font=myFont, bg='blue', fg='yellow', command=cofnij)
    but_powrot.place(relx=0.05, rely=0.05, relwidth=0.2, relheight=0.1)

    powitanie = tk.Label(okno, text='ZAMÓW CZĘŚCI:',font = myFont, bg='blue', fg='yellow')
    powitanie.place(relx=0.25, rely=0.05, relwidth=0.5, relheight=0.1)

    button_koszyk = tk.Button(okno, text = 'KOSZYK', font = myFont, fg = 'blue', bg  = 'white', activebackground='blue', command=partial(przejdz_do_koszyk, klient1), relief = 'solid')
    button_koszyk.place(relx=0.4, rely=0.2, relwidth=0.2, relheight=0.2)

    button1 = tk.Button(okno,text = 'PROCESORY',font = myFont, fg = 'blue', activebackground='blue', bg='white', command=listap, relief = 'solid')
    button1.place(relx=0.10, rely=0.5, relwidth=0.2, relheight=0.2)

    button2 = tk.Button(okno, text='PŁYTY GŁÓWNE',font = myFont, fg='blue', activebackground='blue', bg='white', command=listaplyt, relief = 'solid')
    button2.place(relx=0.30, rely=0.5, relwidth=0.2, relheight=0.2)

    button3 = tk.Button(okno, text='KARTY GRAFICZNE',font = myFont, fg='blue', activebackground='blue', bg='white', command=listakart, relief='solid')
    button3.place(relx=0.50, rely=0.5, relwidth=0.2, relheight=0.2)

    button4 = tk.Button(okno, text='ZASILACZE',font = myFont, fg='blue', activebackground='blue', bg='white', command=listapow, relief='solid')
    button4.place(relx=0.70, rely=0.5, relwidth=0.2, relheight=0.2)

    button5 = tk.Button(okno, text='PAMIĘCI RAM',font = myFont, fg='blue', activebackground='blue', bg='white', command=listaram, relief='solid')
    button5.place(relx=0.10, rely=0.7, relwidth=0.2, relheight=0.2)

    button6 = tk.Button(okno, text='DYSKI',font = myFont, fg='blue', activebackground='blue', bg='white', command=listad, relief='solid')
    button6.place(relx=0.30, rely=0.7, relwidth=0.2, relheight=0.2)

    button7 = tk.Button(okno, text='OBUDOWY',font = myFont, fg='blue', activebackground='blue', bg='white', command=listaobud, relief='solid')
    button7.place(relx=0.50, rely=0.7, relwidth=0.2, relheight=0.2)

    button8 = tk.Button(okno, text='CHŁODZENIA',font = myFont, fg='blue', activebackground='blue', bg='white', command=listacool, relief='solid')
    button8.place(relx=0.70, rely=0.7, relwidth=0.2, relheight=0.2)

# _____________________________________________________________________________________

root = tk.Tk()

myFont = Font(family="Times New Roman", size=25)
myFont2 = Font(family="Times New Roman", size=17)

tlo = tk.Canvas(root, height = 1000, width = 1600)
tlo.pack()


plik = tk.PhotoImage(file = 'pomputer1_color.png')
plik2 = tk.PhotoImage(file = 'pomputeralien_color_small.png.')
plik3 = tk.PhotoImage(file = 'pomputer2_color_small.png.')
plik4 = tk.PhotoImage(file = 'pomputer3_color_small.png.')

background_label = tk.Label(root, image=plik)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

etykieta1 = tk.Label(root, text = 'KIM JESTEŚ?', font = myFont, bg = '#1a75ff', fg = 'yellow')
etykieta1.place(relx = 0.25, rely = 0.1, relwidth = 0.5, relheight = 0.1)

etykieta2 = tk.Label(root, text = 'Admin',font = myFont, bg = '#1a75ff', fg = 'yellow')
etykieta2.place(relx = 0.15, rely = 0.30, relwidth = 0.2, relheight = 0.1)

but1 = tk.Button(root, activebackground = 'blue',bg = 'white', image = plik2, height = 150, width = 150, command = admin)
but1.place(relx = 0.15, rely = 0.4, relwidth = 0.2, relheight = 0.3)

etykieta3 = tk.Label(root, text = 'Pracownik',font = myFont, bg = '#1a75ff', fg = 'yellow')
etykieta3.place(relx = 0.40, rely = 0.30, relwidth = 0.2, relheight = 0.1)

but2 = tk.Button(root, activebackground = 'blue',bg = 'white', image = plik3, height = 150, width = 150, command = pracownik)
but2.place(relx = 0.40, rely = 0.4, relwidth = 0.2, relheight = 0.3)

etykieta4 = tk.Label(root, text = 'Klient',font = myFont, bg = '#1a75ff', fg = 'yellow')
etykieta4.place(relx = 0.65, rely = 0.30, relwidth = 0.2, relheight = 0.1)

but3 = tk.Button(root, activebackground = 'blue',bg = 'white', image = plik4, height = 150, width = 150, command = klient_wejscie)
but3.place(relx = 0.65, rely = 0.4, relwidth = 0.2, relheight = 0.3)


root.mainloop()

