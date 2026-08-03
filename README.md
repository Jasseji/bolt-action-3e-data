# Bolt Action 3E – Configurable DAK v0.4

Poprawka błędu ładowania Army Book w NewRecruit.

Najważniejsza zmiana:
- poprawiono `selectionEntryLinks` na prawidłowe `entryLinks`;
- podniesiono revision systemu i katalogu do 2;
- uproszczono strukturę do działającego przykładu NewRecruit;
- dodano kategorie i ograniczenia plutonów.

## Aktualizacja
Usuń lub zastąp w repozytorium stare pliki `.gst` i `.cat` tymi z paczki.
Plików `.ros` i `.rosz` na razie nie wrzucaj — najpierw testujemy tworzenie pustej listy.

## Konfiguracja jednostek

- jednostkę dodaje się do odpowiedniego plutonu, a doświadczenie i wyposażenie wybiera się wewnątrz jej wpisu;
- dwa gotowe warianty Heer Infantry Squad zastąpiono jednym konfigurowalnym oddziałem;
- Heer Infantry Squad używa grupy modeli 5–10 jak dane 2E: obowiązkowy NCO, 4–9 żołnierzy oraz broń NCO wybierana wewnątrz modelu;
- Panzer III Ausf. L/M i Ausf. N są dostępne wyłącznie jako Regular lub Veteran, zgodnie z Armies of Germany: Third Edition;
- stare wpisy pozostają ukryte, aby wcześniejsze roster files nadal mogły je rozwiązać.
