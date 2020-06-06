#  Przy uruchamianiu programu jako argumenty mozna podac
#  nazwe pliku graficznego oraz maksymalny procentowy
#  odsetek jaki moga stanowic krawedzie w calym pliku

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import sys

# Sprawdzanie czy jako argument zostala podana nazwa pliku oraz
# ewentualnie dopuszczalny odsetek krawedzi
if len(sys.argv) == 3:
    file_name = sys.argv[1]
    edges_percentage = int(sys.argv[2])
elif len(sys.argv) == 2:
    file_name = sys.argv[1]
    # Domyslnie dopuszczalny odsetek krawedzi w calym pliku to 20%
    edges_percentage = 20
else:
    # Jesli nie zostala podana nazwa pliku, program pyta o nia uzytkownika
    file_name = input("Podaj nazwe pliku: ")
    edges_percentage = 20
# Otwieranie pliku graficznego
image = np.array(Image.open(file_name)).astype(np.uint8)

# Tworzenie kopii pliku w odcieniach szarosci
gray_img = np.round(0.299 * image[:, :, 0] +
                    0.587 * image[:, :, 1] +
                    0.114 * image[:, :, 2]).astype(np.uint8)

# Operator Sobel'a - Feldmana
h, v = gray_img.shape
# Filtry w kierunku x oraz y (macierze)
y_direction_filter = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
x_direction_filter = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])

# Tworzymy liste zer, do ktorej zapiszemy plik z wykrytymi krawedziami
newImage = np.zeros((h, v))

print("Wykrywanie krawedzi...")  # Wiadomosc dla uzytkownika

# Dzialamy operatorem na kazdy wektor utwozony z pikseli
for i in range(1, h - 1):
    for j in range(1, v - 1):
        x_Grad = 0  # Gradient w kierunku x
        y_Grad = 0  # Gradient w kierunku y

        for x in range(3):
            for y in range(3):
                x_Grad += ((x_direction_filter[x, y] *
                            gray_img[i - 1 + x, j - 1 + y]))

        for x in range(3):
            for y in range(3):
                y_Grad += ((y_direction_filter[x, y] *
                            gray_img[i - 1 + x, j - 1 + y]))

        # Definicja "wielkosci" wykrytej krawedzi (dla pojedynczego piksela)
        magnitude = np.sqrt(x_Grad**2 + y_Grad**2)
        # Zapisywanie krawedzi
        newImage[i - 1, j - 1] = magnitude

print("Zakonczono wykrywanie krawedzi")  # Wiadomosc dla uzytkownika

# Zmienna pomocnicza okreslajaca czulosc sprawdzania czy piksel jest czarny
sensitivity = 20  # 0 - maksymalna czulosc, 255 - minimalna czulosc


def black(pixel, number):
    # Funkcja sprawdzajaca pixel przyjety jako argument jest czarny
    # Argument number okresla czulosc
    if pixel < number:
        return True
    return False

print("Nanoszenie krawedzi na oryginalny plik...")  # Wiadomosc dla uzytkownika
while True:
    greens = 0  # Zmienna liczaca ilosc zielonych pikseli
    img2 = Image.open(file_name)  # Otwieranie oryginalnego pliku
    pixels2 = img2.load()  # Tworzenie macierzy pikseli rgb
    for i in range(img2.size[0]):  # Sprawdzanie kazdego piksela
        for j in range(img2.size[1]):
            # Zabezpieczenie przed przekroczeniem indeksow pikseli
            if (i+1 < img2.size[0]) and (j+1 < img2.size[1]):
                # Sprawdzanie czy natrafiony piksel jest krawedzia
                if not(black(newImage[j, i], sensitivity)):
                    # Jesli piksel to krawedz ustawiamy jego kolor na zielen
                    pixels2[i, j] = (0, 255, 0)
                    # Zliczanie zielonego piksela
                    greens += 1
    # Sprawdzanie czy krawedzie nie przekraczaja dopuszczalnej ilosci
    if(greens/(img2.size[0] * img2.size[1]) < edges_percentage/100):
        break  # Jesli krawedzi jest wystarczajaco malo, konczymy nanoszenie
    sensitivity += 3  # Zmniejszamy czulosc

print("Zakonczono nanoszenie krawedzi")  # Wiadomosc dla uzytkownika
plt.imshow(img2)  # Linia sluzaca wyswietlaniu pliku z zaznaczonymi krawedziami

# Lista w ktorej zapisane zostana katy w zakresie 0-180 deg
angles = []
# Lista w ktorej zapiszemy ilosc krawedzi nachylonych pod danym katem
how_many = []

for angle in range(0, 181, 4):
    angles.append(angle)  # Dodawanie do listy katow
    how_many.append(0)  # Wypelnianie listy zerami

for i in range(len(angles)):
    angles[i] = angles[i] * np.pi / 180  # Zmienianie stopni na radiany


r = 35.0 / 7.0  # Stala okreslajaca dlugosc wykrywanych krawedzi
print("Badanie orientacji wykrytych krawedzi")  # Wiadomosc dla uzytkownika

for i in range(0, img2.size[0]):  # Sprawdzanie wszystkich pikseli
    for j in range(0, img2.size[1]):
        if (i + 1 < img2.size[0]) and (j + 1 < img2.size[1]):
            # Zabezpieczenie przed przekroczeniem limitu pikseli
            if (i + r * 6 < img2.size[0]-1) and (j + r * 6 < img2.size[1] - 1):
                # Sprawdzamy krawedz tylko jesli startowy piksel jest zielony
                if pixels2[i, j] == (0, 255, 0):
                    for k in range(len(angles)):  # Badanie wszystkich nachylen
                        # Sprawdzanie czy na krawedzi znajduje sie
                        # wystarczajaca ilosc zielonych pikseli
                        if ((pixels2[np.floor(i+1*r*np.cos(angles[k])),
                             np.floor(j+1*r*np.sin(angles[k]))] ==
                            (0, 255, 0)) and
                            (pixels2[np.floor(i+2*r*np.cos(angles[k])),
                             np.floor(j+2*r*np.sin(angles[k]))] ==
                            (0, 255, 0)) and
                            (pixels2[np.floor(i+3*r*np.cos(angles[k])),
                             np.floor(j+3*r*np.sin(angles[k]))] ==
                            (0, 255, 0)) and
                            (pixels2[np.floor(i+4*r*np.cos(angles[k])),
                             np.floor(j+4*r*np.sin(angles[k]))] ==
                            (0, 255, 0)) and
                            (pixels2[np.floor(i+5*r*np.cos(angles[k])),
                             np.floor(j+5*r*np.sin(angles[k]))] ==
                            (0, 255, 0)) and
                            (pixels2[np.floor(i+6*r*np.cos(angles[k])),
                             np.floor(j + 6 * r * np.sin(angles[k]))] ==
                             (0, 255, 0))):
                                how_many[k] += 1

print("Zakonczono badanie orientacji")  # Wiadomosc dla uzytkownika

# Wyswietlanie pliku z wykrytymi krawedziami i wykresu ich orientacji
fig, ax = plt.subplots()
ax.bar(angles, how_many, 0.05)
ax.set_ylabel('Occurance')
ax.set_xlabel('Angle [rad]')
plt.show()
