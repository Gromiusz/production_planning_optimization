import pulp as pl

import numpy as np
from scipy.stats import multivariate_t

''' Generowanie wektora losowego R '''
df = 5 # stopnie swobody
mu = np.array([55, 40, 50, 35, 45, 30])
Sigma = np.array([
    [1, 1, 0, 2, -1, -1],
    [1, 16, -6, -6, -2, 12],
    [0, -6, 4, 2, -2, -5],
    [2, -6, 2, 25, 0, -17],
    [-1, -2, -2, 0, 9, -5],
    [-1, 12, -5, -17, -5, 36]
])

def pojedyncza_ograniczona_probka(mu, Sigma, df, dolna_granica=20, gorna_granica=60):
    while True:
        probka = multivariate_t.rvs(loc=mu, shape=Sigma, df=df)
        if np.all((probka >= dolna_granica) & (probka <= gorna_granica)):
            return probka



probka_rozkladu_T_studenta = pojedyncza_ograniczona_probka(mu, Sigma, df)
print("Wygenerowany wektor:", probka_rozkladu_T_studenta)

miesiace = ['Styczen', 'Luty', 'Marzec']
komponenty = ['A', 'B']
zasoby_produkcyjne = ['Z1', 'Z2']

realizacja_umowy = {
    'A': 1100,
    'B': 1200
}

koszty_produkcji = {
    'A': {'Styczen': 4.7, 'Luty': 0.29, 'Marzec': 0.7},
    'B': {'Styczen': 5, 'Luty': 0.2, 'Marzec': 0.55}
}

zapotrzebowanie_na_sztuke = {
    'A': {'Z1': 0.2, 'Z2': 0.8},
    'B': {'Z1': 0.7, 'Z2': 0.3}
}

mozliwe_dostawy = {
    'Z1': {'Styczen': 600, 'Luty': 700, 'Marzec': 550},
    'Z2': {'Styczen': 1400, 'Luty': 900, 'Marzec': 1200}
}

ilosc_wyprodukowanego_komponentu = pl.LpVariable.dicts("Ilosc_wyprodukowanego_komponentu", ((komponent, miesiac) for komponent in komponenty for miesiac in miesiace), lowBound=0, cat='Integer')
ilosc_skladowanego_komonentu = pl.LpVariable.dicts("Ilosc_skladowanego_komponentu", ((komponent, miesiac) for komponent in komponenty for miesiac in miesiace), lowBound=0, cat='Integer')
miesieczny_koszt_skladowanego_komponentu = pl.LpVariable.dicts("Koszt_skladowania_komponentu", ((komponent, miesiac) for komponent in komponenty for miesiac in miesiace), lowBound=0)
miesieczny_koszt_produkcji_komponentu = pl.LpVariable.dicts("Koszt_produkcji_komponentu", ((komponent, miesiac) for komponent in komponenty for miesiac in miesiace), lowBound=0)
koszt_calkowity = pl.LpVariable("Koszty_calkowite", lowBound=0)

model = pl.LpProblem("Minimalizacja_kosztow", pl.LpMinimize)

for komponent in komponenty:
    for i, miesiac in enumerate(miesiace):
        model += ilosc_skladowanego_komonentu[komponent, 'Styczen'] == ilosc_wyprodukowanego_komponentu[komponent, 'Styczen']
        if miesiac != 'Styczen':
            model += ilosc_skladowanego_komonentu[komponent, miesiac] == ilosc_skladowanego_komonentu[komponent, miesiace[i-1]] + ilosc_wyprodukowanego_komponentu[komponent, miesiac]
        model += miesieczny_koszt_skladowanego_komponentu[komponent, miesiac] >= (ilosc_skladowanego_komonentu[komponent, miesiac] - 150.0) * 0.15 * koszty_produkcji[komponent][miesiac]
        model += miesieczny_koszt_produkcji_komponentu[komponent, miesiac] >= ilosc_wyprodukowanego_komponentu[komponent, miesiac] * koszty_produkcji[komponent][miesiac]
    
    model += ilosc_skladowanego_komonentu[komponent, 'Marzec'] >= realizacja_umowy[komponent]


# TODO zapotrzebowanie
model += ilosc_wyprodukowanego_komponentu >= zapotrzebowanie_na_sztuke[komponent]

model += koszt_calkowity >= pl.lpSum([(miesieczny_koszt_produkcji_komponentu[komponent, miesiac] + miesieczny_koszt_skladowanego_komponentu[komponent, miesiac]) for komponent in komponenty for miesiac in miesiace])
model += koszt_calkowity, "Koszt_calkowity"


solver = pl.PULP_CBC_CMD(timeLimit=3600)
model.solve(solver)
