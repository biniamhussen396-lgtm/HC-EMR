# Stop all containers
cd /opt/emr/bahmni-docker/bahmni-standard
sudo docker stop $(sudo docker ps -aq)

# Restoring openmrs (MySQL)
docker start bahmni-standard-openmrsdb-1
docker exec -it bahmni-standard-openmrsdb-1 mysql -uroot -p'adminAdmin!123' openmrs
SHOW DATABASES;
USE openmrs;
SHOW TABLES;
DROP DATABASE openmrs;
CREATE DATABASE openmrs;
\q



# Restoring bahmni_reports (MySQL)
docker start bahmni-standard-reportsdb-1
cat bahmni_reports.sql | docker exec -i bahmni-standard-reportsdb-1 mysql -uroot -p'adminAdmin!123' bahmni_reports

# Restoring bahmni_pacs (PostgreSQL)
docker start bahmni-standard-pacsdb-1
docker exec -it bahmni-standard-pacsdb-1 psql -U bahmni_pacs bahmni_pacs
\c postgres;
drop database bahmni_pacs;
create database bahmni_pacs;
\q
cat bahmni_pacs.pgsql | docker exec -i bahmni-standard-pacsdb-1 psql -U postgres -d bahmni_pacs

# Restoring pacsdb (PostgreSQL)
docker start bahmni-standard-pacsdb-1
docker exec -it bahmni-standard-pacsdb-1 psql -U pacsdb pacsdb
\c postgres;
drop database pacsdb;
create database pacsdb;
\q
cat pacsdb.pgsql | docker exec -i bahmni-standard-pacsdb-1 psql -U postgres -d pacsdb

# Restoring odoo (PostgreSQL)
docker start bahmni-standard-odoodb-1
docker exec -it bahmni-standard-odoodb-1 psql -U odoo odoo
\c postgres;
drop database odoo;
create database odoo;
\q
cat odoo.pgsql | sudo docker exec -i bahmni-standard-odoodb-1 psql -U odoo -d odoo

# Restoring clinlims (PostgreSQL) -- first start openelisdb container
docker start bahmni-standard-openelisdb-1
docker exec -it bahmni-standard-openelisdb-1 psql -U clinlims clinlims
\c postgres;
drop database clinlims;
create database clinlims;
\q
cat clinlims.pgsql | sudo docker exec -i bahmni-standard-openelisdb-1 psql -U clinlims -d clinlims





