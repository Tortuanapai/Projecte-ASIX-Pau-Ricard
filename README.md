# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema inclou una interfície web funcional per a la gestió d'usuaris, seguretat i auditoria.

---

## 🛠️ Scripts d'Implementació (Base de Dades)

La base de dades s'ha desenvolupat en **PostgreSQL**. Aquests fitxers contenen tota la lògica estructural del sistema:

* 🗄️ **Creació de la Base de Dades:** [script_database.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Disseny%20ER%20-%20Model%20Relacional/script_database.sql)
* 📋 **Definició de Taules i Restriccions:** [script_tables.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Disseny%20ER%20-%20Model%20Relacional/script_tables.sql)

---

## 📊 Documentació del Disseny

Pots consultar la planificació i l'estructura del model mitjançant els següents enllaços:

* 🖼️ **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Disseny%20ER%20-%20Model%20Relacional/Model%20E_R.jpg.jpg)
* 📄 **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Disseny%20ER%20-%20Model%20Relacional/Model%20Relacional_Pau_Ricard.pdf)

---

## 📸 Galeria del Projecte (Screenshots)

### 1. Accés i Registre
Formulari d'inici de sessió i sistema de registre amb validació de format i gestió de rols.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/ss1.png?raw=true" width="45%" alt="Panel Login" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/reg.png?raw=true" width="45%" alt="Panel de registro" />
</p>

### 2. Control d'Errors i Sol·licituds
Validació en temps real per garantir la integritat de les dades i feedback a l'usuari en enviar la sol·licitud.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/control.png?raw=true" width="45%" alt="Control de errores" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/soli.png?raw=true" width="45%" alt="Solicitud enviada" />
</p>

### 3. Panel d'Administració i Dashboard
L'administrador gestiona les aprovacions dels comptes mentre que els usuaris accedeixen al seu panell personalitzat.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/admin.png?raw=true" width="45%" alt="Panel aprobar usuarios" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/panel.png?raw=true" width="45%" alt="Dashboard" />
</p>

### 4. Seguretat i Auditoria
Visualització de logs d'accés i emmagatzematge de contrasenyes mitjançant hashing segur.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/logs.png?raw=true" width="45%" alt="Logs" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/screenshots/hash.png?raw=true" width="45%" alt="Contraseña con hash" />
</p>

---

## 💻 Bloc de Connectivitat i Login

L'aplicació utilitza **Python (Flask)** per connectar la lògica amb PostgreSQL.

### 📁 Fitxers del Mòdul
| Mòdul | Enllaç | Descripció |
| :--- | :--- | :--- |
| **Programa Main** | [app.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/app.py) | Lògica principal, rutes i sessió. |
| **Connector BBDD** | [database.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/database.py) | Gestió de la connexió a PostgreSQL. |
| **Test de Connexió** | [test_db.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/test_db.py) | Script de verificació inicial. |
| **Configuració** | [settings.json](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/settings.json) | Paràmetres de xarxa i credencials. |
| **Registre Logs** | [accessos.log](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/accessos.log) | Auditoria d'accions del sistema. |

---

## 📖 Funcionament del Sistema

1.  **Registre:** L'usuari sol·licita un compte. Les dades es guarden amb estat "pendent" i contrasenya xifrada.
2.  **Aprovació:** L'administrador revisa i valida les sol·licituds des del seu panell exclusiu.
3.  **Accés:** Un cop actiu, l'usuari inicia sessió per accedir a les funcionalitats del seu rol.
4.  **Auditoria:** Tota activitat es registra al fitxer `accessos.log`.

---

## 🚀 Com executar el projecte

### 1. Requisits
Instal·la les dependències:
pip install flask psycopg2 werkzeug
### 2. Base de dades
Crea l'estructura utilitzant els scripts SQL del directori de disseny
Configura el fitxer settings.json amb les credencials de la teva base de dades.
### 3. Execució
Obre una terminal i executa: **py app.py**
