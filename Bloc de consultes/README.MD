# 🔍 Bloc de Consultes — Hospital RIPA

Aquest bloc conté totes les funcions de consulta i lògica de negoci de l'aplicació, implementades en Python amb connexió directa a PostgreSQL.

---

## Consultes disponibles

### Historial d'un pacient
A partir del NSS del pacient, es recupera el seu historial clínic complet: visites ordenades per data i hora, diagnòstics associats, medicaments prescrits amb la seva dosi i pauta, nombre d'ingressos i nombre d'operacions realitzades.

### Agenda d'un metge per dia
Donat un metge i una data concreta, es retornen totes les visites i operacions programades per aquell dia, incloent el quiròfan assignat. A més, es calculen automàticament les hores lliures disponibles en la franja de 8h a 18h.

### Alta de pacient
Permet registrar un nou pacient a la base de dades, validant el format del nom, la longitud del NSS (15 caràcters) i que no existeixi ja al sistema.

### Registre d'usuaris
Gestiona el registre de nous treballadors, amb validació de format del DNI i de la contrasenya, assignació de rol i emmagatzematge segur de la contrasenya amb hash.

### Eliminació de Dummy Data
Funció d'esborrament massiu i optimitzat de les dades de prova, eliminant en ordre correcte totes les dependències (visita_medicament, visita_diagnostic, reserva_habitacio, assistencia_operacio, operacio, visites i pacients) per evitar errors de clau forana.

---

## Índexos implementats

Per garantir un bon rendiment amb grans volums de dades (50.000 pacients, 100.000 visites), s'han creat els índexos següents:

| Índex | Camp | Motiu |
|---|---|---|
| idx_visita_dia_visita | visita.dia_visita | Consultes per data |
| idx_visita_id_metge | visita.id_metge | JOINs per metge |
| idx_visita_id_pacient | visita.id_pacient | JOINs per pacient |
| idx_operacio_dia_operacio | operacio.dia_operacio | Consultes per data |
| idx_pacient_nss | pacient.nss | Cerca per NSS (camp clau de negoci) |
| idx_pacient_descripcio_dummy | pacient.descripcio (parcial) | Esborrament ràpid de dummy data |
| idx_visita_observacions_dummy | visita.observacions (parcial) | Esborrament ràpid de dummy data |

Els índexos parcials sobre el marcador `'DUMMY DATA'` fan que l'eliminació massiva sigui pràcticament instantània, ja que el motor no ha d'escanejar tota la taula.

---

## Estructura del mòdul

| Fitxer | Descripció |
|---|---|
| `bloc_consultes.py` | Totes les funcions de consulta, lògica de negoci i gestió d'índexos |
| `database.py` | Connexió a la base de dades PostgreSQL |
| `accessos.log` | Registre d'accessos i accions del sistema |

