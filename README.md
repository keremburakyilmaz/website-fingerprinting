# Browser fingerprinting demonstration
This is a MVP implementation of browser fingerprinting, a local webserver and a database, that can store and retrieve a certain user behaviour together with a fingerprint. The user can show a certain behaviour on the website by clicking a button to increase the counter. With a submit button the user can store their fingerprint ID together with the number of button clicks in the database. If the user revists the site, the current number of button clicks will be retrieved from the database based on the fingerprint ID.

## Local deployment
```
npm ci
npm start
```
Website is hosted on: http://localhost:3000

## Docker deployment
```
docker-compose build --no-cache client
docker-compose up -d
```
This will run both server and client
Website is hosted on: http://localhost:80

To get interactive terminal of client:
```
docker-compose run client bash
```
