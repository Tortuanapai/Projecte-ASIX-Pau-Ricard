# Esquema d'Alta Disponibilitat, Infraestructura i Seguretat (RIPA)

Aquest directori conté la documentació i l'enfocament tècnic utilitzat per al disseny de la infraestructura, emmagatzematge i la replicació de la base de dades de l'hospital (`hospital_blanes`).

## 🏗️ 1. Infraestructura Hardware i Arquitectura Híbrida
El sistema s'ha dissenyat s'un model híbrid per optimitzar recursos i garantir la continuïtat del servei de l'hospital les 24 hores del dia, els 365 dies de l'any:
* **Node Principal (Master):** Servidor físic local que gestiona el trànsit diari i les escriptures en calent.
* **Node Rèplica (Slave [Cloud]):** Servidor allotjat a una instància d'AWS (Amazon Web Services) configurat dins d'una VPC privada.
* **Seguretat de Xarxa:** Tota la comunicació i sincronització entre el node local i el núvol viatja xifrada a través d'un túnel **VPN Site-To-Site (AES 256)**, protegint les dades mèdiques confidencials contra accessos no autoritzats.

## 💾 2. Particionament de Servidor i Gestió de Volums (LVM)
Per protegir la integritat del sistema operatiu i dels fitxers crítics de la base de dades davant de possibles fallades de disc, s'ha implementat una estructura basada en **LVM (Logical Volume Manager)** sobre una matriu de discs en **RAID 10**:
* **Aïllament de dades:** Es divideixen en contenidors lògics independents els directoris de dades (`/var`), fitxers temporals (`/tmp`), binaris, logs i el directori de còpies de seguretat.
* **Flexibilitat:** Aquesta configuració permet ampliar l'espai de qualsevol partició en calent si les necessitats de l'hospital augmenten, garantint redundància i un millor rendiment físic.

## 🔒 3. Seguretat, Xifrat de Dades i Connexions
L'accés al servidor de bases de dades està totalment restringit i auditat:
* **Configuració de Seguretat (`postgresql.conf` i `pg_hba.conf`):** S'activa el trànsit extern controlat per permetre la connexió dels terminals de l'hospital i el node de rèplica d'AWS, emprant el mètode d'autenticació robust `scram-sha-256`.
* **Capa SSL/TLS:** Tot el trànsit intern de la xarxa s'obliga a viatjar encriptat mitjançant certificats SSL (`server.key` i `server.crt`). 
* **Manteniment Automàtic:** S'ha integrat un script de Bash vinculat al **Cron** del sistema per renovar automàticament de forma desatesa aquests certificats cada 6 mesos, evitant talls inesperats de servei per caducitat.

## 🔄 4. Alta Disponibilitat, Backups i Resolució de Desastres
El sistema compta amb un pla complet de contingència davant d'incidents crítics:
* **Failover Automatitzat:** Si el servidor físic local pateix un desastre físic, el node d'AWS assumeix el rol principal de lectura i escriptura immediatament a través de serveis de recuperació gestionats (AWS DRS).
* **Política de Còpies de Seguretat (Backups):** S'utilitzen scripts automatitzats en Bash per realitzar extraccions de dades en calent (`pg_dump` en format Custom compressiu) cap al volum aïllat `lv_pgbackup`. Aquestes còpies es repliquen automàticament cap al Cloud de forma xifrada i mantenen una regla de rotació de les darreres 5 còpies per optimitzar l'espai de disc.
* **Pla de Restauració:** El sistema està preparat tant per realitzar una restauració total des de zero davant d'una pèrdua absoluta, com una restauració parcial selectiva de les taules crítiques de l'hospital (Pacients i Visites) en pocs minuts en cas d'error humà.
