# ais_dispatch

Stores AIS data in a local database and periodically sends to a remote server.  
Before deployment, the following environment variables need to be set:  

POSTGRES_USER=  
POSTGRES_PASSWORD=  
POSTGRES_DB=  
DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@db:5432/$POSTGRES_DB  
AIS_HOST=  
AIS_PORT=  
REMOTE_SERVER_ADDRESS=  
REMOTE_SERVER_USER=  
REMOTE_SERVER_PW=  
