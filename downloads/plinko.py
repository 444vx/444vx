#!/usr/bin/env python3
import random

saldo = 100
mnozniki = [0.5, 1.25, 1.5, 2, 3]

print("=== Witaj w Plinko! ===")
print(f"Saldo startowe: {saldo}")
print("Startujesz grę wpisując: start <kwota>")
print("Wyjście: exit")

while True:
    cmd = input("Twoja komenda: ").strip().lower()
    if cmd == "exit":
        print(f"Kończysz grę z saldem: {saldo}")
        break
    if cmd.startswith("start "):
        try:
            kwota = float(cmd.split()[1])
            if kwota > saldo:
                print("Nie masz tyle punktów!")
                continue
        except:
            print("Nieprawidłowa kwota")
            continue

        wynik = random.choice(mnozniki)
        wygrana = round(kwota * wynik, 2)
        saldo = round(saldo - kwota + wygrana, 2)
        print(f"Kulka wylądowała na {wynik}x! Twoje saldo: {saldo}\n")
    else:
        print("Nieznana komenda.")
