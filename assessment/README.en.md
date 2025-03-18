# Assessment Assignment

## Assignment goal:
Demonstrate that you are able to set up a Django web application in combination with Django REST Framework for storing geolocation data.

## Assignment description

### 1. Setup:
- Create an .env file based on the .env.example file.

- Run `docker compose build`
- Run `docker compose up`
- Run `docker compose exec web python manage.py migrate`
- Run `docker compose restart`

The application should now be available at the following url:
[http://localhost:8000/status](http://localhost:8000/status)

### 2. Application structure
- In the geoapi app, create a model that stores geolocation data, consisting of the following fields:
- `location` (PointField - a geometric point that stores latitude and longitude)
- `timestamp` (datetime)
- `user` (optional foreign key to a user model, if authentication is added)

#### Prerequisites:
- Use GeoDjango's `PointField` to store location data (latitude, longitude).

### 3. API functionality
- Implement a **POST API endpoint** where users can submit their geolocation (latitude and longitude).
- The API must validate that the location data is valid.
- Use GeoDjango to manage geospatial queries and storage.
- Implement a **GET API endpoint** that allows users to retrieve a list of stored geolocations, optionally filtered by user (if authentication is added).
- Add filtering based on distance. For example: show geolocations within a certain radius range of a given point.
- Come up with a way to dynamically create views based on data models provided by users (for example via a configuration file) So that each model has its own endpoint.

### 4. End result
- Deliver a working application that can be started with Docker Compose.
- All required API endpoints must be functional and properly tested.

## Criteria for assessment:
- Correctness of implementation.
- Structure and readability of the code.
- Use of Django REST Framework for implementing API endpoints.

## Delivery:
- A link to a publicly available repository (e.g. GitHub, GitLab) containing the code, including Docker configuration.
- A brief description of your approach and explanation of design choices in the `README.md`.

## Implementation 

### Data model design
I created the `GeoLocation` model as the core of the application using GeoDjango's spatial capabilities:

- **Location**: I implemented this as a `PointField` with spatial indexing to optimise performance for geographic queries. I set the geography parameter to true for more accurate distance calculations.
- **Timestamp**: I included this field to store when each location was recorded, with a default value of the current time.
- **User**: I added an optional foreign key to Django's built-in User model, allowing locations to be associated with authenticated users.

I incorporated several performance optimisations:
- Spatial index on the location field for faster geographic queries
- Standard index on timestamp for efficient time-based filtering
- Default ordering by most recent timestamp

### API design
I built the API using Django REST Framework with a RESTful architecture:

- **ModelViewSet**: I employed this to provide complete CRUD operations for geolocation data
- **Flexible data input**: I designed the API to accept coordinates in two formats:
  - JSON format with a `coordinates` array: `{"coordinates": [longitude, latitude]}`
  - Form format with separate `longitude` and `latitude` fields
- **Permissions**: I configured the API to allow read access to all users, while authenticated users get their locations automatically associated with their accounts
- **Error handling**: I implemented comprehensive validation and error responses for invalid data or server issues

I structured all endpoints to follow RESTful conventions with appropriate HTTP methods:
- POST /api/locations/ - Create a new location
- GET /api/locations/ - List all locations with optional filtering
- GET /api/locations/{id}/ - Retrieve a specific location

### Filtering
I implemented two primary filtering mechanisms:

- **Distance filtering**: I created this to find locations within a specified radius from a reference point
  - Query parameter: `distance` (in meters)
  - Reference point: `lat` (latitude) and `lng` (longitude)
  - Example: `/api/locations/?lat=52.3740&lng=4.8897&distance=5000` finds locations within 5km of Amsterdam

- **User filtering**: I added this to filter locations by specific users
  - Query parameter: `user` (user ID)
  - Example: `/api/locations/?user=1` returns all locations for user with ID 1
  - This can be combined with distance filtering for more specific queries

I used GeoDjango's spatial functions and database extensions for efficient geographic calculations directly in the database rather than in application code.


## Testing

To run unit tests run 

`docker compose exec web python manage.py test assessment/geoapi`