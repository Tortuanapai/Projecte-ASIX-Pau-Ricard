# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema està pensat per coordinar la infraestructura, el personal sanitari i el flux operatiu de pacients.

## 📊 Documentació del Disseny

Pots consultar la planificació i l'estructura del model mitjançant els següents enllaços:

* **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/6d562f8ae37be82cfa39e35b65cd066b75a214d6/Model%20E_R.jpg)
* **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/Model%20Relacional-Pau_Ricard.pdf)

---

## 🛠️ Scripts d'Implementació

La base de dades s'ha desenvolupat en **PostgreSQL**. Per veure el codi de creació de la base de dades i les taules, accedeix als següents fitxers:

* **Creació de la Base de Dades:** [script_database.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/script_database.sql)
* **Definició de Taules i Restriccions:** [script_tables.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/script_tables.sql)

---

## 💻 Sistema de Gestió i Interfície Web

S'ha desenvolupat una aplicació web completa utilitzant **Python (Flask)** que permet gestionar l'accés d'usuaris a la base de dades amb seguretat avançada i auditoria.

### 🚀 Funcionalitats Principals
* **Seguretat:** Hashing de contrasenyes i gestió de sessions segures.
* **Control d'Accessos:** Sistema de registre amb estat "Pendent" fins que un administrador aprova l'usuari.
* **Auditoria en Temps Real:** Registre automàtic de cada moviment en un fitxer de log extern.
* **Interfície Professional:** Disseny amb CSS personalitzat adaptable a diferents mides de pantalla.

### 📁 Estructura del Projecte Web

| Mòdul | Enllaç al Fitxer | Descripció |
| :--- | :--- | :--- |
| **Backend (Main)** | [app.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/app.py) | Lògica principal, rutes de Flask i control de logs. |
| **BBDD Connector** | [database.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/database.py) | Gestió de la connexió amb PostgreSQL. |
| **Configuració** | [settings.json](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/settings.json) | Paràmetres de connexió (IP, Usuari, Port). |
| **Disseny (CSS)** | [style.css](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/style.css) | Estils visuals per a tota l'aplicació. |
| **Auditoria** | [accessos.log](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/accessos.log) | Registre històric d'accions del sistema. |

### 🖥️ Vistes del Sistema (Frontend)
* [**Login**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/login.html): Accés segur per a personal registrat.
* [**Registre**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/registro.html): Sol·licitud d'accés per a nous treballadors.
* [**Panel d'Usuari**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/panel.html): Àrea central de gestió post-login.
* [**Gestió Admin**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/admin.html): Control de comptes pendents d'aprovació.
* [**Visor de Logs**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/logs.html): Pantalla d'administració per consultar l'arxiu `accessos.log`.

---

## 🛠️ Requisits de l'Entorn
* Python 3.x
* Flask (`pip install flask`)
* Psycopg2 (`pip install psycopg2`)
* PostgreSQL v14 o superior

---
© 2026 Projecte ASIX - Pau & Ricard.
