# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema inclou una interfície web funcional per a la gestió d'usuaris, seguretat i auditoria.

---

## 1. 📊 Disseny de la Base de Dades (Model E-R)

La base de dades s'ha desenvolupat en **PostgreSQL**. Aquesta secció inclou tota la planificació estructural i els scripts de creació.

### 🖼️ Documentació del Disseny
* **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/7beeb4383c721a6dee397e2a9cb9cd1efabcdac5/Disseny%20ER%20-%20Model%20Relacional/Model%20E_R_v1.jpg)
* **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/7beeb4383c721a6dee397e2a9cb9cd1efabcdac5/Disseny%20ER%20-%20Model%20Relacional/Model%20Relacional_v1.pdf)

### 🛠️ Scripts d'Implementació
* 🗄️ **Creació de la Base de Dades:** [script_database.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Disseny%20ER%20-%20Model%20Relacional/script_database.sql)
* 📋 **Definició de Taules i Restriccions:** [script_tables.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/7beeb4383c721a6dee397e2a9cb9cd1efabcdac5/Disseny%20ER%20-%20Model%20Relacional/script_tables_v1.sql)

---

## 2. 💻 Bloc de Connectivitat i Login

L'aplicació utilitza **Python (Flask)** per connectar la interfície web amb PostgreSQL, gestionant sessions, validacions i rols d'usuari.

### 📁 Fitxers del Mòdul
| Mòdul | Enllaç | Descripció |
| :--- | :--- | :--- |
| **Programa Main** | [app.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/Bloc%20de%20connectivitat%20i%20login/app.py) | Lògica principal, rutes i servidor Flask. |
| **Funcions Auxiliars** | [funciones.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/Bloc%20de%20connectivitat%20i%20login/funciones.py) | Lògica de negoci, validacions i decoradors. |
| **Connector BBDD** | [database.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/Bloc%20de%20connectivitat%20i%20login/database.py) | Gestió de la connexió a PostgreSQL. |
| **Configuració** | [settings.json](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/Bloc%20de%20connectivitat%20i%20login/settings.json) | Paràmetres de xarxa i credencials de la BBDD. |

### 📸 Captures de Funcionament
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/ss1.png?raw=true" width="45%" alt="Panel Login" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/reg.png?raw=true" width="45%" alt="Panel de registro" />
</p>
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/admin.png?raw=true" width="45%" alt="Panel administrar" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/panel.png?raw=true" width="45%" alt="Dashboard" />
</p>

---

## 3. 🛡️ Esquema de Seguretat i Privacitat

Implementació de mesures tècniques per garantir la protecció de dades sensibles i el control d'accessos segons el rol de l'usuari.

### 📄 Documentació de Seguretat
* **Auditoria AGPD:** [Document de Seguretat AGPD](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/Auditoria%20AGPD.pdf) – Marc normatiu.
* **Matriu de Seguretat:** [Esquema de Seguretat](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/Matriu%20de%20Securetat.pdf) – Definició d'accessos per rol.
* **Data Masking:** [Documentació Data Masking](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/Data%20Masking.pdf) – Dissociació de dades.
* **Criptografia SSL:** [Configuració SSL](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/SSL.pdf) – Seguretat en el trànsit de dades.

### 🧪 Proves de Seguretat i Auditoria
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/screenshots/PRUEBADATAMASKING.PNG?raw=true" width="31%" alt="Data Masking" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/screenshots/PRUEBA_DENIED_PACIENT.PNG?raw=true" width="31%" alt="Accés Denegat" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/screenshots/prueba_SSL_USADO.PNG?raw=true" width="31%" alt="SSL" />
</p>
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/logs.png?raw=true" width="45%" alt="Logs Auditoria" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/hash.png?raw=true" width="45%" alt="Hashing contrasenyes" />
</p>

---

## 🚀 Com executar el projecte

### 1. Requisits
Instal·la les dependències:
pip install flask psycopg2 werkzeug
