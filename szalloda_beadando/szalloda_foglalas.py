from abc import ABC, abstractmethod
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class Szoba(ABC):
    def __init__(self, szobaszam, ar):
        self.szobaszam = szobaszam
        self.ar = ar
        self.foglalt_datumok = set()

    @abstractmethod
    def kiir(self):
        pass

    def foglal(self, datum):
        if datum in self.foglalt_datumok:
            raise ValueError("A szoba már le van foglalva")
        self.foglalt_datumok.add(datum)

    def lemond(self, datum):
        if datum not in self.foglalt_datumok:
            raise ValueError("A szoba nem volt foglalt")
        self.foglalt_datumok.remove(datum)

class EgyagyasSzoba(Szoba):
    def kiir(self):
        return f"Egyágyas szoba {self.szobaszam}, ára: {self.ar}"

class KetagyasSzoba(Szoba):
    def kiir(self):
        return f"Kétágyas szoba {self.szobaszam}, ára: {self.ar}"

class Szalloda:
    def __init__(self, nev):
        self.nev = nev
        self.szobak = []

    def uj_szoba(self, szobatipus, szobaszam, ar):
        if any(szoba.szobaszam == szobaszam for szoba in self.szobak):
            raise ValueError("A szoba már létezik")
        if szobatipus == 'egyagyas':
            szoba = EgyagyasSzoba(szobaszam, ar)
        elif szobatipus == 'ketagyas':
            szoba = KetagyasSzoba(szobaszam, ar)
        else:
            raise ValueError("Ismeretlen szobatipus.")
        self.szobak.append(szoba)

    def szoba_foglalas(self, szobaszam, datum):
        for szoba in self.szobak:
            if szoba.szobaszam == szobaszam:
                if datum > datetime.now():
                    szoba.foglal(datum)
                    return szoba.ar
                else:
                    raise ValueError("A foglalás csak jövőbeli dátumra lehetséges.")
        raise ValueError("Nincs ilyen szobaszám a szállodában.")

    def szoba_lemondas(self, szobaszam, datum):
        for szoba in self.szobak:
            if szoba.szobaszam == szobaszam:
                szoba.lemond(datum)
                return
        raise ValueError("Nincs ilyen szobaszám a szállodában.")

    def listaz_foglalasok(self):
        foglalasok = []
        for szoba in self.szobak:
            for datum in szoba.foglalt_datumok:
                datum = datum.strftime("%Y-%m-%d")
                foglalasok.append(f"{szoba.kiir()}, dátum: {datum}")
        return foglalasok

def default_adatok():
    fragro_hotel = Szalloda("Fragro Hotel")
    fragro_hotel.uj_szoba('egyagyas', 101, 10000)
    fragro_hotel.uj_szoba('egyagyas', 102, 10000)
    fragro_hotel.uj_szoba('ketagyas', 201, 15000)
    fragro_hotel.uj_szoba('ketagyas', 202, 15000)
    fragro_hotel.uj_szoba('ketagyas', 203, 15000)

    fragro_hotel.szoba_foglalas(101, datetime(2024, 5, 15))
    fragro_hotel.szoba_foglalas(201, datetime(2024, 5, 15))
    fragro_hotel.szoba_foglalas(202, datetime(2024, 5, 16))
    fragro_hotel.szoba_foglalas(203, datetime(2024, 5, 17))
    fragro_hotel.szoba_foglalas(102, datetime(2024, 5, 17))

    return [fragro_hotel]

class HotelFoglaloGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Hotel Foglaló Rendszer")

        self.szallodak = default_adatok()

        self.menu = tk.Frame(self.master)
        self.menu.pack()

        self.hotel_listbox = tk.Listbox(self.menu, selectmode=tk.SINGLE)
        self.hotel_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for szallo in self.szallodak:
            self.hotel_listbox.insert(tk.END, szallo.nev)

        tk.Button(self.menu, text="Foglalás", command=self.foglalas_gui).pack()
        tk.Button(self.menu, text="Lemondás", command=self.lemondas_gui).pack()
        tk.Button(self.menu, text="Foglalások listázása", command=self.listaz_gui).pack()

    def foglalas_gui(self):

        try:
            selected_hotel = self.hotel_listbox.curselection()[0]
        except IndexError:
            messagebox.showerror("Nincs hotel kiválasztva", "Válassz ki egy hotelt")
            return

        foglalas_window = tk.Toplevel(self.master)
        foglalas_window.title("Foglalás")

        tk.Label(foglalas_window, text="Szobaszám:").pack()
        szobaszam_entry = tk.Entry(foglalas_window)
        szobaszam_entry.pack()

        tk.Label(foglalas_window, text="Dátum (év-hónap-nap):").pack()
        datum_entry = tk.Entry(foglalas_window)
        datum_entry.pack()

        def foglalas_submit():
            szobaszam = int(szobaszam_entry.get())
            datum_str = datum_entry.get()
            try:
                datum = datetime.strptime(datum_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Hiba", "Hibás időformátum")
                return

            try:
                ar = self.szallodak[selected_hotel].szoba_foglalas(szobaszam, datum)
                messagebox.showinfo("Foglalás megerősítve", f"Sikeres foglalás {ar} Ft-ért!")
                foglalas_window.destroy()
            except ValueError as e:
                messagebox.showerror("Hiba", str(e))

        tk.Button(foglalas_window, text="Foglalás", command=foglalas_submit).pack()

    def lemondas_gui(self):

        try:
            selected_hotel = self.hotel_listbox.curselection()[0]
        except IndexError:
            messagebox.showerror("Nincs hotel kiválasztva", "Válassz ki egy hotelt")
            return

        lemondas_window = tk.Toplevel(self.master)
        lemondas_window.title("Lemondás")

        tk.Label(lemondas_window, text="Szobaszám:").pack()
        szobaszam_entry = tk.Entry(lemondas_window)
        szobaszam_entry.pack()

        tk.Label(lemondas_window, text="Dátum (év-hónap-nap):").pack()
        datum_entry = tk.Entry(lemondas_window)
        datum_entry.pack()

        def lemondas_submit():
            szobaszam = int(szobaszam_entry.get())
            datum_str = datum_entry.get()
            datum = datetime.strptime(datum_str, "%Y-%m-%d")

            try:
                self.szallodak[selected_hotel].szoba_lemondas(szobaszam, datum)
                messagebox.showinfo("Lemondás megerősítve", "Sikeres lemondás!")
                lemondas_window.destroy()
            except ValueError as e:
                messagebox.showerror("Hiba", str(e))

        tk.Button(lemondas_window, text="Lemondás", command=lemondas_submit).pack()

    def listaz_gui(self):

        try:
            selected_hotel = self.hotel_listbox.curselection()[0]
        except IndexError:
            messagebox.showerror("Nincs hotel kiválasztva", "Válassz ki egy hotelt")
            return

        listazas_window = tk.Toplevel(self.master)
        listazas_window.title("Foglalások listája")

        foglalasok = self.szallodak[selected_hotel].listaz_foglalasok()
        for foglalas in foglalasok:
            tk.Label(listazas_window, text=foglalas).pack()




if __name__ == "__main__":
    root = tk.Tk()
    app = HotelFoglaloGUI(root)
    root.mainloop()