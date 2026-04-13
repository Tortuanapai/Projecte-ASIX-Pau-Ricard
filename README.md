# 🏥 Hospital Blanes RIPA
> **Sistema de Gestió de Base de Dades i Interfície Web**

Aquest projecte integra una base de dades relacional robusta en **PostgreSQL** amb una interfície de gestió desenvolupada en **Python (Flask)**. Està dissenyat per coordinar la infraestructura, el personal i l'auditoria de seguretat d'un entorn hospitalari.

---

## 🛠️ Stack Tecnològic

| Tecnologia | Ús |
| :--- | :--- |
| **PostgreSQL** | Motor de base de dades relacional |
| **Python 3** | Lògica de backend i gestió de dades |
| **Flask** | Framework web per a la interfície |
| **Jinja2** | Motor de plantilles HTML |
| **CSS3** | Disseny visual personalitzat i responsive |

---

## 📂 Recursos i Disseny

### 📐 Arquitectura de Dades
Pots consultar la documentació tècnica del modelat aquí:
* 🖼️ **Model Entitat-Relació:** [Veure Diagrama E/R](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/6d562f8ae37be82cfa39e35b65cd066b75a214d6/Model%20E_R.jpg)
* 📄 **Model Relacional:** [Consultar Document PDF](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/8e20e9f5b9b97cd6a11603186edff92e41a2d7d7/Model%20Relacional-Pau_Ricard.pdf)

### 📜 Scripts SQL
1. [**script_database.sql**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_database.sql) → Creació de l'instància.
2. [**script_tables.sql**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/script_tables.sql) → Taules, claus i restriccions.

---

## 📸 Demo Visual (Screenshots)

<p align="center">
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/2ab89118068c810834d912b82b03a4a5af5fd5c0/ss1.png?raw=true" width="30%" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/31b3a096ad2ee615ab093b974e45094e080eb881/control.png?raw=true" width="30%" />
  <img src="https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/b4794c40289a97d813a9c05c79cf7c249e8411f7/panel.png?raw=true" width="30%" />
</p>

---

## 💻 Estructura del Programari

### 📂 Arxius Principals
| Fitxer | Funció Principal |
| :--- | :--- |
| [**app.py**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/app.py) | **Main:** Rutes, gestió de sessions i Flask. |
| [**database.py**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/database.py) | **Connector:** Execució de queries i connexió BBDD. |
| [**settings.json**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/settings.json) | **Config:** Credencials de PostgreSQL. |
| [**style.css**](https://github.com/Tortuanapai/Projecte-ASIX-Pau-Ricard/blob/main/static/css/style.css) | **Frontend:** Maquetació i estils visuals. |

### 🌐 Plantilles HTML (`/templates`)
| Arxiu | Descripció |
| :--- | :--- |
| **login.html** | Formulari d'accés segur al sistema. |
| **registre.html** | Formulari de sol·licitud per a nous usuaris. |
| **panel.html** | Àrea principal personalitzada segons el rol de l'usuari. |
| **admin_pendents.html** | Panell exclusiu per aprovar o rebutjar sol·licituds. |
| **logs.html** | Visor en temps real del fitxer `accessos.log`. |

---

## 📖 Flux de Funcionament

1. **Registre:** L'usuari envia dades; aquestes queden en estat **Pendent** amb la password hashada.
2. **Aprovació:** L'Admin valida l'usuari des del seu panell exclusiu.
3. **Sessió:** L'usuari accedeix segons el seu rol (**Metge, Admin, etc.**).
4. **Auditoria:** Cada acció (login, registre, aprovació) genera un log en temps real.

---

## 🚀 Guia de Desplegament

### 1. Preparació de l'entorn
Instal·la les dependències necessàries mitjançant pip:
pip install flask psycopg2 werkzeug
