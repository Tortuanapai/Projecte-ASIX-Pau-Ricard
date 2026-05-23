# 🔒 Esquema de Seguretat — Hospital RIPA

Aquest apartat recull totes les mesures de seguretat implementades a la base de dades de l'Hospital Blanes RIPA, seguint els principis de l'RGPD i les bones pràctiques en gestió de bases de dades hospitalàries.

---

## 1. Rols i Matriu de Seguretat

S'han definit quatre rols principals, cadascun amb accés limitat a les taules i operacions estrictament necessàries per a la seva funció. Això segueix el **principi de mínim privilegi**: cap rol té més permisos dels que necessita.

| Rol | Taules | Operacions |
|---|---|---|
| **dba** | Totes les taules | SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, GRANT |
| **metge** | VISITA, DIAGNOSTIC, VISITA_MEDICAMENT, VISITA_DIAGNOSTIC, OPERACIO | SELECT, INSERT, UPDATE |
| **metge** | PACIENT, MEDICAMENT, HABITACIO, APARELL | SELECT |
| **infermeria** | ASSISTENCIA_OPERACIO | SELECT, INSERT |
| **infermeria** | HABITACIO, PLANTA | SELECT, UPDATE |
| **infermeria** | PACIENT, VISITA, VISITA_MEDICAMENT, APARELL | SELECT |
| **administratiu** | PACIENT, TREBALLADOR, RESERVA_HABITACIO, VISITA | SELECT, INSERT, UPDATE |
| **administratiu** | PLANTA, HABITACIO, METGE, INFERMERIA, TIPUS_APARELL | SELECT |

> ⚠️ Cap rol excepte el **dba** pot eliminar dades. Això garanteix que els historials clínics i registres de treballadors es mantinguin íntegres en tot moment.

Els scripts SQL amb les comandes de creació de rols i assignació de permisos es troben a: `comandesmatriu.sql`

---

## 2. Data Masking

En un entorn hospitalari és imprescindible protegir la privacitat dels pacients i del personal. S'ha implementat una capa d'emmascarament de dades sensibles seguint l'**RGPD**, de manera que el personal no tingui accés a informació confidencial si no és estrictament necessari.

Les màscares s'han implementat mitjançant **Vistes SQL** sobre l'esquema `mask`.

| Taula | Camp | Què veu el treballador | Tècnica |
|---|---|---|---|
| PACIENTS | NSS | `****-****-2246` | Masking parcial |
| PACIENTS | Adreça | `Madrid**************` | Masking parcial |
| METGES | DNI/NIF | `********` | Masking complet |

Els scripts SQL amb les vistes d'emmascarament es troben a: `comandamasking.sql`

---

## 3. SSL — Xifrat de les Comunicacions

Per garantir que les dades viatgen xifrades entre els clients i el servidor de base de dades, s'ha configurat **SSL** a PostgreSQL amb el protocol **TLSv1.3** i el cipher **TLS_AES_256_GCM_SHA384**.

**Passos realitzats:**

1. Generació del certificat i la clau privada del servidor amb OpenSSL
2. Configuració de `postgresql.conf` per activar SSL i apuntar als fitxers generats
3. Verificació que les connexions es fan via SSL
4. Creació d'un script d'autorenovació del certificat (`renovar-ssl.sh`)
5. Programació amb **cron** per executar la renovació automàticament cada 6 mesos a les 3h de la nit

---

## 4. Compliment Legal — RGPD

Totes les mesures implementades estan alineades amb el Reglament General de Protecció de Dades:

| Mesura Implementada | Article RGPD | Objectiu |
|---|---|---|
| Classificació de rols | 5.1.f | Principi d'Integritat i Confidencialitat |
| Control d'accés granular | 32 | Seguretat del Tractament |
| Data Masking | 25 | Privacitat des del disseny |
| Minimització de les Dades | 5.1.c | Principi de Minimització |
| Xifrat SSL | 32.1.a | Xifrat de dades personals |
| Protecció dels Diagnòstics | 9 | Categories especials de dades |

