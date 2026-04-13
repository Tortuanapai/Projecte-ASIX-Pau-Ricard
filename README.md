# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema inclou una interfície web funcional per a la gestió d'usuaris, seguretat i auditoria.

## 📊 Documentació del Disseny

Pots consultar la planificació i l'estructura del model mitjançant els següents enllaços:

* **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/6d562f8ae37be82cfa39e35b65cd066b75a214d6/Model%20E_R.jpg)
* **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/Model%20Relacional-Pau_Ricard.pdf)

---

## 📸 Galeria del Projecte (Screenshots)

### 1. Accés i Registre
El sistema compta amb un formulari d'inici de sessió i un sistema de registre amb validació de format (DNI) i gestió de rols.
<p align="center">
  <img src="https://raw.githubusercontent.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/main/screenshots/login.png" width="45%" />
  <img src="https://raw.githubusercontent.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/main/screenshots/registro.png" width="45%" />
</p>

### 2. Panel de Control i Administració
Un cop autenticat, l'usuari accedeix a un panel personalitzat. L'administrador disposa d'eines exclusives per aprovar nous usuaris pendents.
<p align="center">
  <img src="https://raw.githubusercontent.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/main/screenshots/panel_general.png" width="90%" />
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/main/screenshots/admin_panel.png" width="70%" />
</p>

### 3. Seguretat i Auditoria
Totes les accions es registren en un visor de logs en temps real. A la base de dades (PostgreSQL), les contrasenyes s'emmagatzemen xifrades amb algoritmes de hashing (scrypt).
<p align="center">
  <img src="https://raw.githubusercontent.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/main/screenshots/logs_view.png" width="70%" />
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/main/screenshots/database_hash.png" width="50%" />
</p>

---

## 🛠️ Scripts d'Implementació

La base de dades s'ha desenvolupat en **PostgreSQL**.
* **Creació de la Base de Dades:** [script_database.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_database.sql)
* **Definició de Taules i Restriccions:** [script_tables.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_tables.sql)

---

## 💻 Sistema de Gestió i Interfície Web

L'aplicació utilitza **Python (Flask)** per connectar la lògica de negoci amb la base de dades.

### 📁 Estructura del Projecte
| Mòdul | Descripció |
| :--- | :--- |
| **app.py** | Lògica principal i rutes de Flask. |
| **database.py** | Connector central amb PostgreSQL. |
| **style.css** | Disseny visual basat en variables i flexbox. |
| **accessos.log** | Arxiu físic de logs d'activitat. |

---
© 2026 Projecte ASIX - Pau & Ricard.
