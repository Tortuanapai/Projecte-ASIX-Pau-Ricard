# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema inclou una interfície web funcional per a la gestió d'usuaris, seguretat i auditoria.

---

## 🛠️ Scripts d'Implementació (Base de Dades)

La base de dades s'ha desenvolupat en **PostgreSQL**. Aquests fitxers contenen tota la lògica estructural del sistema:

* **Creació de la Base de Dades:** [script_database.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_database.sql)
* **Definició de Taules i Restriccions:** [script_tables.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_tables.sql)

---

## 📊 Documentació del Disseny

Pots consultar la planificació i l'estructura del model mitjançant els següents enllaços:

* **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/6d562f8ae37be82cfa39e35b65cd066b75a214d6/Model%20E_R.jpg)
* **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/Model%20Relacional-Pau_Ricard.pdf)

---

## 📸 Galeria del Projecte (Screenshots)

### 1. Accés i Registre
Formulari d'inici de sessió i sistema de registre amb validació de format i gestió de rols.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2ab89118068c810834d912b82b03a4a5af5fd5c0/ss1.png?raw=true" width="45%" alt="Registre" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2ab89118068c810834d912b82b03a4a5af5fd5c0/soli.png?raw=true" width="45%" alt="Sol·licitud enviada" />
</p>

### 2. Control d'Errors
Validació en temps real (ex: format de DNI) per garantir la integritat de la base de dades.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/31b3a096ad2ee615ab093b974e45094e080eb881/control.png?raw=true" width="70%" alt="Control d'errors" />
</p>

### 3. Panel de Control i Administració
Vistes personalitzades segons el rol. L'administrador gestiona les aprovacions dels comptes pendents.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/b4794c40289a97d813a9c05c79cf7c249e8411f7/panel.png?raw=true" width="90%" alt="Panel Principal" />
</p>
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/726c467e73380ffed134cdcedbdaa83020da07c1/admin.png?raw=true" width="70%" alt="Panel d'Aprovació" />
</p>

### 4. Seguretat i Auditoria
Visualització de logs i emmagatzematge de contrasenyes mitjançant hashing per complir amb els estàndards de seguretat.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2b2ea1c4bc743c6e45cff0adab8616374f0cb772/logs.png?raw=true" width="70%" alt="Logs d'accés" />
</p>
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2f4240ba25cb9f31cd9413f27c65ef7cb22f9885/hash.png?raw=true" width="60%" alt="Password Hash" />
</p>

---

## 💻 Sistema de Gestió i Interfície Web

L'aplicació utilitza **Python (Flask)** per connectar la lògica amb PostgreSQL.

### 📁 Fitxers del Projecte
| Mòdul | Enllaç | Descripció |
| :--- | :--- | :--- |
| **Programa Main** | [app.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/app.py) | Lògica principal, rutes i sessió. |
| **Connector BBDD** | [database.py](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/database.py) | Gestió de la connexió a PostgreSQL. |
| **Configuració** | [settings.json](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/settings.json) | Paràmetres de connexió i credencials. |
| **Estils CSS** | [style.css](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/style.css) | Disseny visual i responsive. |
| **Registre Logs** | [accessos.log](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/accessos.log) | Fitxer d'auditoria d'accions del sistema. |

---

## 📖 Funcionament del Sistema

1. **Registre:** L'usuari sol·licita un compte enviant el seu DNI, nom i rol. Les dades es guarden amb estat "pendent".
2. **Aprovació:** Un administrador accedeix al panell de gestió per aprovar o rebutjar les sol·licituds.
3. **Accés:** Un cop aprovat, l'usuari pot entrar amb les seves credencials i accedir a les funcionalitats del seu rol.
4. **Auditoria:** Qualsevol intent de login o acció administrativa es registra amb marca de temps al fitxer de logs.

---

## 🚀 Com executar el projecte

### 1. Requisits
Necessites Python 3 i PostgreSQL instal·lats. Instal·la les llibreries:
pip install flask psycopg2 werkzeug
### **2. Base de Dades**
Crea la base de dades executant els scripts SQL esmentats a la secció superior.
Configura el teu Host, User i Password al fitxer settings.json.
### **3. Execució**
Obre una terminal a la carpeta del projecte i executa:
**python app.py**
Accedeix al sistema mitjançant el navegador a http://localhost.
