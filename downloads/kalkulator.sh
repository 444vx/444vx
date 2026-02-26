#!/bin/bash

echo "=== Kalkulator ==="
echo "Wpisz działanie, np. 2+2 lub 5*3"
echo "Wpisz 'exit' aby zakończyć"

while true; do
    read -p "Podaj działanie: " input
    if [[ "$input" == "exit" ]]; then
        echo "Koniec."
        break
    fi
    # Oblicz wynik
    result=$(echo "scale=2; $input" | bc 2>/dev/null)
    if [[ -z "$result" ]]; then
        echo "Błąd: niepoprawne działanie"
    else
        echo "Wynik: $result"
    fi
done
