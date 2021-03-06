# Conceptplan

# Basisplan

Wij zijn van plan om voor deze opdracht een triviawebsite te maken. Het idee van de website is om spelers in lobby's van 1 tot 5 personen alleen of samen vragen te laten beantwoorden met instelbare moeilijkheidsgraden en challenges. Spelers kunnen punten scoren door een vraag binnen de tijd goed te beantwoorden en hun scores worden opgeslagen in verschillende leaderboards. De score wordt bepaald door de moeilijkheidsgraad van de quiz en de verbonden challenges. Challenges worden dagelijks en om het half uur gewijzigd.

### Minimum requirements

- Index
- Inloggen/ registreren / uitloggen
- Lobby met vragen om te beantwoorden
- Samen kunnen spelen in een lobby
- Challenges bij de vragen die de score beinvloeden
- Scoreboards
- Chatsysteem

# Uitgebreid plan

### Het spel

Om het basisplan uit te breiden voegen wij een nieuwe gamemode toe aan de lobby's. Deze gamemode is gebaseerd op enige elementen van het spel 'werewolf'. In de lobby werken spelers nog steeds samen om vragen te beantwoorden, maar er wordt een rollenspel toegevoegd. Dit rollenspel focust zich op de discussie rondom het beantwoorden van de vragen.

Allereerst zijn er normale spelers die de vragen goed willen beantwoorden voor punten.

Als tweede is er een leider aanwezig die het gesprek leidt en een bonus krijgt als de vragen goed worden beantwoorden. Bij fout beantwoorde vragen verliest de leider echter punten.

Als laatste is er een 'fool' die als doel heeft de groep in de weg te zitten en ze te leiden naar het fout beantwoorden van de vraag. De 'fool' weet het antwoord op de vraag van tevoren en kan dit gebruiken om de groep de verkeerde kant op te sturen. Bij het verkeerd beantwoorden van de vraag krijgt de 'fool' punten.

Een extra functie van de leider is het ontmaskeren van de 'fool'. Als de leider goed raadt wie de 'fool' is van het spel krijgt hij hier punten voor.

Uiteindelijk is het de bedoeling dat er leuke discussie plaatsvindt rondom het beantwoorden van de vragen en dat de rollen van leider en 'fool' slim worden gespeeld wat leidt tot leuke situaties.

### Features

- Index (homepagina/ startpagina. Hub om te navigeren)
- Login (inloggen, mogelijk wachtwoord vergeten toevoegen aan deze route)
- Register (registreren)
- Configuration (moeilijkheidsgraad, gamemode, challenges, lobbysettings)
- Lobby (trivia spelen, score zien, configuration zien)
- Chat (live communiceren over de vragen, gebruikersnamen kunnen zien, rollen verdelen)
- Scoreboard (zien van de scores en mogelijk het zoeken van spelers)
- Profile (zien van je eigen statistieken en badges)
- Badges verzamelen
- Learn more (informatie over het spel, spelregels, tips)

### Score

Fools en leaders worden opgenomen op de leaderboards en krijgen een score gebaseerd op hun 'succesrate'. Dit is een percentage van de gewonnen games als hun rol vermenigvuldigd met een factor 'gespeelde games'. De beste fools en leaders kunnen dagelijks een badge verdienen.

De scoreboards wat betreft de normale gamemode blijft hetzelfde en dagelijks kunnen de beste spelers ook een badge verdienen

### Profiel

Elke speler krijgt zijn eigen profiel met statistieken van hun normale games en speciale games als fool en leader. Op hun profiel staan ook hun badges

### Learn more

Op deze pagina wordt de speciale gamemode gebaseerd op werewolf uitgelegd



