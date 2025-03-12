# Assessment Opdracht

## Doel van de opdracht:
Toon aan dat je in staat bent om een Django-webapplicatie op te zetten in combinatie met Django REST Framework voor het opslaan van geolocatiegegevens. 

## Opdrachtomschrijving

### 1. Setup:
- Maak een .env file aan op basis van de .env.example file.
- Run `docker compose build`
- Run `docker compose up`
- Run `docker compose exec web python manage.py migrate`
- Run `docker compose restart`

De applicatie moet nu beschikbaar zijn op de volgende url:
[http://localhost:8000/status](http://localhost:8000/status)

### 2. Applicatiestructuur
- Maak in de geoapi app een model dat geolocatiegegevens opslaat, bestaande uit de volgende velden:
  - `location` (PointField - een geometrisch punt dat latitude en longitude opslaat)
  - `timestamp` (datetime)
  - `user` (optionele foreign key naar een user model, indien authenticatie wordt toegevoegd)

#### Vereisten:
- Gebruik GeoDjango's `PointField` om locatiegegevens (latitude, longitude) op te slaan.

### 3. API-functionaliteit
- Implementeer een **POST API endpoint** waar gebruikers hun geolocatie (latitude en longitude) kunnen indienen.
  - De API moet valideren dat de locatiegegevens geldig zijn.
  - Gebruik GeoDjango om georuimtelijke query's en opslag te beheren.
- Implementeer een **GET API endpoint** waarmee gebruikers een lijst van opgeslagen geolocaties kunnen ophalen, eventueel gefilterd op gebruiker (als authenticatie wordt toegevoegd).
- Voeg filtering toe op basis van afstand. Bijvoorbeeld: laat geolocaties binnen een bepaald straalbereik van een opgegeven punt zien.
- Bedenk een methode om dynamisch views te maken op basis van datamodellen die door gebruikers worden aangeleverd (bijvoorbeeld via een configuratiebestand) Zodat voor elk model een eigen endpoint wordt gemaakt.

### 4. Eindresultaat
- Lever een werkende applicatie op die gestart kan worden met Docker Compose.
- Alle vereiste API endpoints moeten functioneel zijn en correct getest.

## Criteria voor beoordeling:
- Correctheid van de implementatie.
- Structuur en leesbaarheid van de code.
- Gebruik van Django REST Framework voor het implementeren van API endpoints.

## Levering:
- Een link naar een publiek beschikbare repository (bijv. GitHub, GitLab) waarin de code staat, inclusief de Docker-configuratie.
- Een korte beschrijving van je aanpak en uitleg van ontwerpkeuzes in de `README.md`.
