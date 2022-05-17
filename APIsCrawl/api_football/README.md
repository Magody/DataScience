docker run -p 27040:27017 -v /home/magody/programming/python/data_science/containers_data/mongodb:/data/db --name mongodb_datascience -it mongo

## Access terminal
- docker exec -it mongodb_datascience bash
- mongo
- show dbs
- use apifootball
 db.createUser({user: "developer", pwd: "developer123", roles: [ { role: "userAdminAnyDatabase", db: "admin" }]})
 - use admin
 db.createUser({user: "developer", pwd: "developer123", roles: [ { role: "userAdminAnyDatabase", db: "admin" }]})
