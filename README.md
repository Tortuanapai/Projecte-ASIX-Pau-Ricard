# 🏥 Hospital Blanes RIPA - Sistema de Gestió de Base de Dades

Aquest projecte consisteix en el disseny i la implementació d'una base de dades relacional per a la gestió interna de l'Hospital de Blanes. El sistema inclou una interfície web funcional per a la gestió d'usuaris, seguretat i auditoria.

---

## 🛠️ Scripts d'Implementació (Base de Dades)

La base de dades s'ha desenvolupat en **PostgreSQL**:

- 🗄️ **Creació de la Base de Dades:**  
  https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Disseny%20ER%20-%20Model%20Relacional/script_database.sql

- 📋 **Definició de Taules i Restriccions:**  
  https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/7beeb4383c721a6dee397e2a9cb9cd1efabcdac5/Disseny%20ER%20-%20Model%20Relacional/script_tables_v1.sql

---

## 📊 Documentació del Disseny

- 🖼️ **Model Entitat-Relació:**  
  https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/7beeb4383c721a6dee397e2a9cb9cd1efabcdac5/Disseny%20ER%20-%20Model%20Relacional/Model%20E_R_v1.jpg

- 📄 **Model Relacional:**  
  https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/7beeb4383c721a6dee397e2a9cb9cd1efabcdac5/Disseny%20ER%20-%20Model%20Relacional/Model%20Relacional_v1.pdf

---

## 🔐 Esquema de Seguretat

### 📄 Documentació AGPD
- https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/Auditoria%20AGPD.pdf

### 🛡️ Data Masking
- https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/Data%20Masking.pdf

📸 Prova:
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/screenshots/PRUEBADATAMASKING.PNG?raw=true" width="60%">
</p>

### 🧩 Matriu de Seguretat
- https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/Matriu%20de%20Securetat.pdf

📸 Prova:
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/screenshots/PRUEBA_DENIED_PACIENT.PNG?raw=true" width="60%">
</p>

### 🔒 SSL
- https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/Esquema%20de%20Seguretat/SSL.pdf

📸 Prova:
<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/209c878cf9d4e09bd8f8db626803cfd22f4dc195/screenshots/prueba_SSL_USADO.PNG?raw=true" width="60%">
</p>

---

## 💻 Bloc de Connectivitat i Login

| Mòdul | Enllaç | Descripció |
|------|-------|-----------|
| app.py | https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/app.py | Lògica principal |
| database.py | https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/database.py | Connexió PostgreSQL |
| test_db.py | https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/test_db.py | Verificació |
| settings.json | https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/settings.json | Credencials |
| accessos.log | https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/1f43033be7fb871f50a2948d50aeab535e34bb34/Bloc%20de%20connectivitat%20i%20login/accessos.log | Auditoria |

---

## 📖 Funcionament del Sistema

1. Registre → usuari pendent + password xifrada  
2. Aprovació → admin valida  
3. Login → accés segons rol  
4. Auditoria → registre a logs  

---

## 🚀 Com executar el projecte

### 1️⃣ Requisits
**pip install flask psycopg2 werkzeug**
**configurar el fitxer settings.json**
**py app.py**
