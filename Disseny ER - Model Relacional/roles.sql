hospital_blanes=# -- 1. Donar permisos per utilitzar l'esquema
hospital_blanes=# GRANT USAGE ON SCHEMA hospital_blanes TO administratiu, dba, infermer, medic;
GRANT
hospital_blanes=# 
hospital_blanes=# -- 2. Permisos totales absolutos para el DBA (Administrador de la BD)
hospital_blanes=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hospital_blanes TO dba;
GRANT
hospital_blanes=# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hospital_blanes TO dba;
GRANT
hospital_blanes=# 
hospital_blanes=# -- 3. Permisos de lectura y escriptura per als sanitaris y administratius
hospital_blanes=# GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA hospital_blanes TO medic, infermer, administratiu;
GRANT
hospital_blanes=# GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA hospital_blanes TO medic, infermer, administratiu;
GRANT
hospital_blanes=# 
