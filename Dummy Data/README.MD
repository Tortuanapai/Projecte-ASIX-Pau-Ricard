## 📊 2. Dummy Data (Dades de Prova)

Per a provar el rendiment i fer una prova d'estrès de la Base de Dades, hem implementat l'apartat de **Dummy Data**.

Bàsicament, el que fem consisteix en afegir milers i milers de registres falsos que siguin realistes per avaluar el rendiment i el comportament de la Base de Dades amb **PostgreSQL**. 

Aquest set de generació de dades simula com seria l'entorn real d'un hospital amb:
* 👥 **50.000** pacients únics.
* 🩺 **100.000** visites mèdiques històriques.
* 💼 **Tot el personal del centre:** 100 metges, 200 infermeres, 50 administratius i 100 treballadors de neteja.

⚙️ La inserció de les dades s'ha realitzat mitjançant scripts de **Python** utilitzant la llibreria `Faker`. S'ha configurat específicament amb codificació **UTF-8** i alfabet **ciríl·lic** per validar el suport de caràcters internacionals requerit pel centre hospitalari.
