## Obrir "Query Tool" desde usuari postgres ##

-- Forçar desconnexió

SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'ripa' AND pid <> pg_backend_pid();

-- Borrar base de dades

DROP DATABASE IF EXISTS ripa;

-- Borrar rols antics

DROP ROLE IF EXISTS administratiu;
DROP ROLE IF EXISTS dba;
DROP ROLE IF EXISTS infermer;
DROP ROLE IF EXISTS medic;