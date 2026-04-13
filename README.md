# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema inclou una interfície web funcional per a la gestió d'usuaris, seguretat i auditoria.

## 📊 Documentació del Disseny

Pots consultar la planificació i l'estructura del model mitjançant els següents enllaços:

* **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/6d562f8ae37be82cfa39e35b65cd066b75a214d6/Model%20E_R.jpg)
* **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/Model%20Relacional-Pau_Ricard.pdf)

---

## 🛠️ Scripts d'Implementació

La base de dades s'ha desenvolupat en **PostgreSQL**. Aquests fitxers contenen tota la lògica estructural del sistema:

* **Creació de la Base de Dades:** [script_database.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_database.sql)
* **Definició de Taules i Restriccions:** [script_tables.sql](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_tables.sql)

---

## 📸 Galeria del Projecte (Screenshots)

### 1. Accés i Registre
El sistema compta amb un formulari d'inici de sessió i un sistema de registre amb validació de format i gestió de rols.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2ab89118068c810834d912b82b03a4a5af5fd5c0/ss1.png?raw=true" width="45%" alt="Registre" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2ab89118068c810834d912b82b03a4a5af5fd5c0/soli.png?raw=true" width="45%" alt="Sol·licitud enviada" />
</p>

### 2. Control d'Errors
S'ha implementat un control de format per evitar entrades incorrectes, com ara la validació en temps real del DNI per garantir la integritat de les dades.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/31b3a096ad2ee615ab093b974e45094e080eb881/control.png?raw=true" width="70%" alt="Control d'errors" />
</p>

### 3. Panel de Control i Administració
L'usuari accedeix a un panel principal segons el seu rol. L'administrador pot gestionar les aprovacions dels nous usuaris des d'una vista dedicada.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/b4794c40289a97d813a9c05c79cf7c249e8411f7/panel.png?raw=true" width="90%" alt="Panel Principal" />
</p>
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/726c467e73380ffed134cdcedbdaa83020da07c1/admin.png?raw=true" width="70%" alt="Panel d'Aprovació" />
</p>

### 4. Seguretat i Auditoria
Registre detallat d'activitat (logs) i emmagatzematge segur de credencials mitjançant hashing per complir amb els estàndards de seguretat informàtica.
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2b2ea1c4bc743c6e45cff0adab8616374f0cb772/logs.png?raw=true" width="70%" alt="Logs d'accés" />
</p>
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2f4240ba25cb9f31cd9413f27c65ef7cb22f9885/hash.png?raw=true" width="60%" alt="Password Hash" />
</p>

---

## 💻 Sistema de Gestió i Interfície Web

L'aplicació utilitza **Python (Flask)** per connectar la lògica de negoci amb la base de dades PostgreSQL.

### 📁 Estructura del Projecte
| Mòdul | Descripció |
| :--- | :--- |
| **app.py** | Lògica principal, gestió de rutes i generació de logs. |
| **database.py** | Connector central i configuració de la connexió a la BDD. |
| **style.css** | Estils visuals i maquetació responsive. |
| **accessos.log** | Arxiu físic on es guarden les auditories de seguretat. |

---
© 2026 Projecte ASIX - Pau & Ricard.
