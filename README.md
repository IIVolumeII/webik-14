# Simple Trivia

Een triviawebsite gemaakt door Timon Brouwer (11857692) uit groep 14

![schets](schetsen/Screenshot.png)


## Features

De huidige features van deze triviasite zijn:

- Het maken van accounts
  - Registeren
  - Inloggen
  - Wachtwoord veranderen
- Triviavragen van verschillende categorieen, moeilijkheden en vraagtypes beantwoorden
- Het bijhouden van scores
- Global leaderboards met de top 5 spelers
- Een eigen profiel
- Een homepage
- Een learn more pagina

## Repository

- De model van de code bestaat uit helpers.py en users.py. In users.py staan functies omtrent het registreren en inloggen en in helpers.py staan functies voor de triviavragen en de scores
- De view van de code bestaat uit de bestanden in het mapje templates
- De controller van de code bestaat uit application.py

- De database heet finance.db
- De table voor het registreren en inloggen van de gebruikers is "users"
- De table voor het bijhouden van de scores is "score"
- De table voor het bewaren van de triviavragen is "portfolio"

- Play is een manier om de trivia te spelen met een eigen configuratie. Het is nodig dat er een keuze wordt gemaakt in elk onderdeel
- Quickplay is een manier om snel de trivia te spelen met een willekeurige configuratie voor elke vraag. De gebruiker kan op ieder moment stoppen
