import datetime
import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import connect_to_db

app = Flask(__name__)
app.secret_key = 'hospital_blanes_ripa_2026_secure_key'

# --- FUNCIÓ DE LOGS ---
def registrar_log(usuari, accio, estat):
    try:
        # Busquem la carpeta on està el script per evitar errors de permisos en el port 80
        ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
        ruta_log = os.path.join(ruta_carpeta, "accessos.log")
        
        hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        linia = f"[{hora}] USUARI: {usuari} | ACCIÓ: {accio} | ESTAT: {estat}\n"
        
        # Mode "a" (append) per afegir sense esborrar el que ja hi ha
        with open(ruta_log, "a", encoding="utf-8") as f:
            f.write(linia)
        
        # Print de control per veure-ho a la terminal de Windows
        print(f"📝 LOG ESCRIT: {usuari} - {accio} ({estat})")
    except Exception as e:
        print(f"⚠️ ERROR ESCRIVENT LOG: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTES ---

@app.route('/')
def inici():
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        dni = request.form.get('dni', '').upper()
        nom = request.form.get('nom', '')
        password = request.form.get('password', '')
        rol = request.form.get('rol', '')
        
        if not re.match(r"^[0-9]{8}[A-Z]$", dni):
            flash('❌ Format de DNI incorrecte.', 'danger')
            return render_template('registro.html')

        password_hash = generate_password_hash(password)
        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT usuario FROM usuaris_registrats WHERE usuario = %s UNION SELECT usuario FROM usuaris_pendents WHERE usuario = %s", (dni, dni))
                if cur.fetchone():
                    flash('❌ Aquest DNI ja existeix.', 'warning')
                else:
                    cur.execute("INSERT INTO usuaris_pendents (usuario, password_hash, nom_rol) VALUES (%s, %s, %s)", (dni, password_hash, rol))
                    conn.commit()
                    registrar_log(dni, "REGISTRE PENDENT", "ÈXIT")
                    flash('✅ Sol·licitud enviada. Espera aprovació.', 'success')
                    cur.close()
                    conn.close()
                    return redirect(url_for('login'))
            except Exception as e:
                if conn: conn.rollback()
                flash(f'❌ Error: {e}', 'danger')
            finally:
                if cur: cur.close()
                if conn: conn.close()
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dni_web = request.form.get('dni', '').upper()
        pass_web = request.form.get('password', '')
        
        conn = connect_to_db()
        if not conn:
            flash('❌ Error de connexió amb la base de dades.', 'danger')
            return render_template('login.html')

        cur = conn.cursor()
        try:
            cur.execute("SELECT password_hash, usuario, nom_rol FROM usuaris_registrats WHERE usuario = %s", (dni_web,))
            usuari = cur.fetchone()
            
            if usuari and check_password_hash(usuari[0], pass_web):
                session.clear()
                session['usuario'] = usuari[1]
                session['nombre'] = usuari[1]
                session['rol'] = usuari[2]
                registrar_log(dni_web, "LOGIN", "ÈXIT")
                
                cur.close()
                conn.close()
                return redirect(url_for('panel'))
            
            cur.execute("SELECT id FROM usuaris_pendents WHERE usuario = %s", (dni_web,))
            if cur.fetchone():
                flash('⚠️ Compte pendent d\'aprovació.', 'warning')
                registrar_log(dni_web, "LOGIN", "PENDENT")
            else:
                flash('❌ Credencials incorrectes.', 'danger')
                registrar_log(dni_web, "LOGIN", "FALLIT")
                
        except Exception as e:
            print(f"Error en consulta: {e}")
        finally:
            # CORRECCIÓ: Tancament segur en el bloc finally
            if cur: cur.close()
            if conn: conn.close()
                
    return render_template('login.html')

@app.route('/panel')
@login_required
def panel():
    return render_template('panel.html', nombre=session.get('nombre'), rol=session.get('rol'))

@app.route('/admin')
@login_required
def admin_panel():
    if session.get('rol') != 'Administrador':
        flash('🚫 Accés denegat.', 'danger')
        return redirect(url_for('panel'))
    
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT id, usuario, nom_rol FROM usuaris_pendents")
    lista = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', lista=lista)

@app.route('/aprovar/<int:id>')
@login_required
def aprovar(id):
    if session.get('rol') != 'Administrador':
        return "No autoritzat", 403
        
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT usuario, password_hash, nom_rol FROM usuaris_pendents WHERE id = %s", (id,))
    u = cur.fetchone()
    
    if u:
        try:
            cur.execute("INSERT INTO usuaris_registrats (usuario, password_hash, nom_rol) VALUES (%s, %s, %s)", (u[0], u[1], u[2]))
            cur.execute("DELETE FROM usuaris_pendents WHERE id = %s", (id,))
            conn.commit()
            registrar_log(session.get('usuario'), f"APROVAR USUARI {u[0]}", "ÈXIT")
            flash(f'✅ Usuari {u[0]} aprovat.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'❌ Error: {e}', 'danger')
            
    cur.close()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/rebutjar/<int:id>')
@login_required
def rebutjar(id):
    if session.get('rol') != 'Administrador':
        return "No autoritzat", 403
        
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT usuario FROM usuaris_pendents WHERE id = %s", (id,))
    u = cur.fetchone()
    
    if u:
        cur.execute("DELETE FROM usuaris_pendents WHERE id = %s", (id,))
        conn.commit()
        registrar_log(session.get('usuario'), f"REBUTJAR USUARI {u[0]}", "ÈXIT")
        flash('🚫 Sol·licitud eliminada.', 'warning')
    
    cur.close()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    registrar_log(session.get('usuario', 'Desconegut'), "LOGOUT", "ÈXIT")
    session.clear()
    return redirect(url_for('login'))

@app.route('/logs')
@login_required
def ver_logs():
    # Solo el administrador debería ver los logs
    if session.get('rol') != 'Administrador':
        flash('🚫 Accés denegat.', 'danger')
        return redirect(url_for('panel'))

    ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta_log = os.path.join(ruta_carpeta, "accessos.log")
    
    lineas_log = []
    if os.path.exists(ruta_log):
        with open(ruta_log, "r", encoding="utf-8") as f:
            # Leemos todas las líneas y las invertimos para ver lo más nuevo primero
            lineas_log = f.readlines()[::-1] 
    
    return render_template('logs.html', logs=lineas_log)

if __name__ == '__main__':
    # Host 0.0.0.0 per permetre l'accés des d'Ubuntu
    app.run(host='0.0.0.0', port=80, debug=False)
