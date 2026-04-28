import os
import json
import re
import collections
import logging
from contextlib import contextmanager
from werkzeug.security import check_password_hash
from database import connect_to_db


logger_app = logging.getLogger('hospital_app')
logger_app.setLevel(logging.INFO)
logger_app.propagate = False  


if not logger_app.handlers:
    fh = logging.FileHandler('accessos.log', encoding='utf-8')
    formatter = logging.Formatter(
        '[%(asctime)s] USUARI: %(user)s | ACCIÓ: %(action)s | ESTAT: %(status)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    logger_app.addHandler(fh)

@contextmanager
def get_db_connection():
    conn = connect_to_db()
    if not conn:
        raise Exception("Error de connexió a la base de dades")
    try:
        yield conn
    finally:
        if conn:
            conn.close()

def registrar_log(usuari, accio, estat):
    logger_app.info('', extra={'user': usuari, 'action': accio, 'status': estat})

def validate_dni(dni):
    return re.match(r"^[0-9]{8}[A-Z]$", dni) is not None

def validate_password(password):
    return len(password) >= 8

def verify_credentials(password_hash, pass_web):
    return check_password_hash(password_hash, pass_web)

def get_pending_users():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, usuario, nom_rol FROM usuaris_pendents")
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error recuperant pendents: {e}")
        return []

def approve_user(user_id):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT usuario, password_hash, nom_rol FROM usuaris_pendents WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if user:
                cur.execute("INSERT INTO usuaris_registrats (usuario, password_hash, nom_rol) VALUES (%s, %s, %s)", 
                           (user[0], user[1], user[2]))
                cur.execute("DELETE FROM usuaris_pendents WHERE id = %s", (user_id,))
                conn.commit()
                return True, user[0]
            return False, None
    except Exception as e:
        logging.error(f"Error aprovant usuari {user_id}: {e}")
        return False, None

def reject_user(user_id):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT usuario FROM usuaris_pendents WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if user:
                cur.execute("DELETE FROM usuaris_pendents WHERE id = %s", (user_id,))
                conn.commit()
                return True, user[0]
            return False, None
    except Exception as e:
        logging.error(f"Error rebutjant usuari {user_id}: {e}")
        return False, None

def get_logs(max_lines=10000):
    log_path = "accessos.log"
    if not os.path.exists(log_path): return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return list(collections.deque(f, maxlen=max_lines))[::-1]
    except Exception as e:
        logging.error(f"Error llegint logs: {e}")
        return []

def get_infermer_dependency(dni):
    """Retorna la dependència de metge o planta per a un infermer."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT i.id_metge, i.id_planta,
                       tm.nom AS metge_nom, tm.primer_cognom AS metge_cognom, tm.segon_cognom AS metge_segoncognom,
                       p.nom_planta
                FROM usuaris_registrats u
                LEFT JOIN infermeria i ON u.id_treballador = i.id_treballador
                LEFT JOIN treballador tm ON i.id_metge = tm.id_treballador
                LEFT JOIN planta p ON i.id_planta = p.id_planta
                WHERE u.usuario = %s AND u.nom_rol = 'Infermer'
                """,
                (dni,)
            )
            row = cur.fetchone()
            if not row:
                return None

            id_metge, id_planta, metge_nom, metge_cognom, metge_segoncognom, nom_planta = row
            parts = []
            if id_metge:
                metge_fullname = " ".join(filter(None, [metge_nom, metge_cognom, metge_segoncognom]))
                parts.append(f"Depèn de Metge/ssa: {metge_fullname}")
            if id_planta:
                parts.append(f"És de planta: {nom_planta}")
            if not parts:
                return "No s'ha assignat ni metge ni planta"
            return " · ".join(parts)
    except Exception as e:
        logging.error(f"Error obtenint informació d'infermeria per {dni}: {e}")
        return None


def get_quirofan_schedule(dia_operacio):
    """Retorna les operacions programades per dia i quiròfan."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT q.codi_quirofan,
                       o.hora_operacio,
                       p.nom AS pacient_nom,
                       p.nss,
                       concat(tmetge.nom, ' ', tmetge.primer_cognom, ' ', tmetge.segon_cognom) AS metge_nom,
                       COALESCE(
                           STRING_AGG(DISTINCT concat(ti.nom, ' ', ti.primer_cognom, ' ', ti.segon_cognom), ', '),
                           'Sense infermeria assignada'
                       ) AS infermers
                FROM operacio o
                JOIN quirofan q ON o.id_quirofan = q.id_quirofan
                JOIN pacient p ON o.id_pacient = p.id_pacient
                JOIN metge m ON o.id_metge = m.id_treballador
                JOIN treballador tmetge ON m.id_treballador = tmetge.id_treballador
                LEFT JOIN assistencia_operacio ao ON o.id_operacio = ao.id_operacio
                LEFT JOIN infermeria i ON ao.id_infermer = i.id_treballador
                LEFT JOIN treballador ti ON i.id_treballador = ti.id_treballador
                WHERE o.dia_operacio = %s
                GROUP BY q.codi_quirofan, o.hora_operacio, p.nom, p.nss, metge_nom
                ORDER BY q.codi_quirofan, o.hora_operacio
                """,
                (dia_operacio,)
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint horari de quiròfan per {dia_operacio}: {e}")
        return []


def get_quirofan_equipment():
    """Retorna la llista d'aparells assignats a cada quiròfan amb quantitat."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT q.codi_quirofan,
                       p.nom_planta,
                       ap.nom_aparell,
                       qa.quantitat
                FROM quirofan_aparell qa
                JOIN quirofan q ON qa.id_quirofan = q.id_quirofan
                LEFT JOIN planta p ON q.id_planta = p.id_planta
                JOIN aparell ap ON qa.id_aparell = ap.id_aparell
                ORDER BY q.id_quirofan, ap.nom_aparell
                """
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint aparells de quiròfan: {e}")
        return []


def get_visit_schedule(dia_visita):
    """Retorna les visites planificades per dia."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT v.hora_visita,
                       concat(tmetge.nom, ' ', tmetge.primer_cognom, ' ', tmetge.segon_cognom) AS metge_nom,
                       p.nom AS pacient_nom,
                       p.nss
                FROM visita v
                JOIN metge m ON v.id_metge = m.id_treballador
                JOIN treballador tmetge ON m.id_treballador = tmetge.id_treballador
                JOIN pacient p ON v.id_pacient = p.id_pacient
                WHERE v.dia_visita = %s
                ORDER BY v.hora_visita
                """,
                (dia_visita,)
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint visites per {dia_visita}: {e}")
        return []


def get_habitacio_reserves(id_habitacio):
    """Retorna les reserves previstes d'una habitació."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM get_habitacio_reserves(%s)",
                (id_habitacio,)
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint reserves de la habitació {id_habitacio}: {e}")
        return []


def direct_register_user(dni, password, rol):
    """Registra un usuario directamente en usuaris_registrats (solo para DBA)"""
    try:
        # Validaciones
        if not dni or not password or not rol:
            return False, "DNI, contraseña y rol requeridos"
        
        dni = dni.strip().upper()
        if not validate_dni(dni):
            return False, "DNI no válido. Formato: 8 cifras y letra mayúscula."
        
        if not validate_password(password):
            return False, "La contraseña debe tener mínimo 8 caracteres"
        
        # Verificar que el rol sea válido
        valid_roles = ["Medic", "Infermer", "Administratiu", "dba"]
        if rol not in valid_roles:
            return False, f"Rol no válido. Roles permitidos: {', '.join(valid_roles)}"
        
        # Verificar que el usuario no exista ya
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT usuario FROM usuaris_registrats WHERE usuario = %s", (dni,))
            if cur.fetchone():
                return False, "El DNI ya está registrado"
            
            # Generar hash de contraseña
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            
            # Insertar directamente
            cur.execute("INSERT INTO usuaris_registrats (usuario, password_hash, nom_rol) VALUES (%s, %s, %s)",
                       (dni, password_hash, rol))
            conn.commit()
            
            return True, f"Usuario {dni} registrado exitosamente con rol {rol}"
            
    except Exception as e:
        logging.error(f"Error en registro directo: {e}")
        return False, f"Error en registro: {str(e)}"

def add_patient(nom, nss, adreça, descripcio):
    """Añade un nuevo paciente (solo para administrativos)"""
    try:
        # Validaciones
        if not nom or not nss:
            return False, "Nombre y NSS requeridos"
        
        nom = nom.strip()
        nss = nss.strip()
        
        # Validar formato del nombre (INITCAP)
        if nom != nom.title():
            return False, "El nombre debe estar en formato título (primera letra mayúscula)"
        
        # Validar NSS (15 caracteres)
        if len(nss) != 15:
            return False, "NSS debe tener exactamente 15 caracteres"
        
        # Verificar que el NSS no exista ya
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT nss FROM pacient WHERE nss = %s", (nss,))
            if cur.fetchone():
                return False, "El NSS ya está registrado"
            
            # Insertar paciente
            cur.execute("INSERT INTO pacient (nom, nss, adreça, descripcio) VALUES (%s, %s, %s, %s)",
                       (nom, nss, adreça.strip() if adreça else None, descripcio.strip() if descripcio else None))
            conn.commit()
            
            return True, f"Paciente {nom} registrado exitosamente"
            
    except Exception as e:
        logging.error(f"Error al añadir paciente: {e}")
        return False, f"Error al registrar paciente: {str(e)}"


def get_patient_history(nss):
    """Retorna l'historial de visites, diagnòstics, medicaments, ingressos i operacions d'un pacient."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_pacient, nom FROM pacient WHERE nss = %s",
                (nss,)
            )
            pacient = cur.fetchone()
            if not pacient:
                return None

            id_pacient, nom = pacient

            cur.execute(
                """
                SELECT v.dia_visita,
                       v.hora_visita,
                       v.observacions,
                       concat(tmetge.nom, ' ', tmetge.primer_cognom, ' ', tmetge.segon_cognom) AS metge_nom
                FROM visita v
                JOIN metge m ON v.id_metge = m.id_treballador
                JOIN treballador tmetge ON m.id_treballador = tmetge.id_treballador
                WHERE v.id_pacient = %s
                ORDER BY v.dia_visita, v.hora_visita
                """,
                (id_pacient,)
            )
            visites = cur.fetchall()

            cur.execute(
                """
                SELECT DISTINCT d.nom_malaltia, d.descripcio
                FROM visita_diagnostic vd
                JOIN diagnostic d ON vd.id_diagnostic = d.id_diagnostic
                JOIN visita v ON vd.id_visita = v.id_visita
                WHERE v.id_pacient = %s
                ORDER BY d.nom_malaltia
                """,
                (id_pacient,)
            )
            diagnostics = cur.fetchall()

            cur.execute(
                """
                SELECT DISTINCT m.nom_comercial,
                                m.principi_actiu,
                                vm.dosis,
                                vm.pauta,
                                v.dia_visita
                FROM visita_medicament vm
                JOIN medicament m ON vm.id_medicament = m.id_medicament
                JOIN visita v ON vm.id_visita = v.id_visita
                WHERE v.id_pacient = %s
                ORDER BY v.dia_visita, m.nom_comercial
                """,
                (id_pacient,)
            )
            medicaments = cur.fetchall()

            cur.execute(
                "SELECT COUNT(*) FROM reserva_habitacio WHERE id_pacient = %s",
                (id_pacient,)
            )
            admissions_count = cur.fetchone()[0] or 0

            cur.execute(
                "SELECT COUNT(*) FROM operacio WHERE id_pacient = %s",
                (id_pacient,)
            )
            operation_count = cur.fetchone()[0] or 0

            return {
                'id_pacient': id_pacient,
                'nom': nom,
                'nss': nss,
                'visits': visites,
                'diagnostics': diagnostics,
                'medications': medicaments,
                'admissions_count': admissions_count,
                'operation_count': operation_count
            }
    except Exception as e:
        logging.error(f"Error obtenint història de pacient per {nss}: {e}")
        return None


def get_doctor_schedule(metge_usuario, dia):
    """Retorna l'agenda de visites i operacions d'un metge per un dia, amb hores disponibles."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_treballador FROM usuaris_registrats WHERE usuario = %s",
                (metge_usuario,)
            )
            row = cur.fetchone()
            metge_id = row[0] if row and row[0] else None

            if not metge_id:
                cur.execute(
                    "SELECT id_treballador FROM treballador WHERE nif = %s",
                    (metge_usuario,)
                )
                row = cur.fetchone()
                if row:
                    metge_id = row[0]

            if not metge_id:
                return None

            cur.execute(
                """
                SELECT v.hora_visita,
                       p.nom AS pacient_nom,
                       p.nss
                FROM visita v
                JOIN pacient p ON v.id_pacient = p.id_pacient
                WHERE v.id_metge = %s AND v.dia_visita = %s
                ORDER BY v.hora_visita
                """,
                (metge_id, dia)
            )
            visits = cur.fetchall()

            cur.execute(
                """
                SELECT o.hora_operacio,
                       p.nom AS pacient_nom,
                       p.nss,
                       q.codi_quirofan
                FROM operacio o
                JOIN pacient p ON o.id_pacient = p.id_pacient
                JOIN quirofan q ON o.id_quirofan = q.id_quirofan
                WHERE o.id_metge = %s AND o.dia_operacio = %s
                ORDER BY o.hora_operacio
                """,
                (metge_id, dia)
            )
            operations = cur.fetchall()

            booked = set()
            for visit in visits:
                if visit[0] is not None:
                    booked.add(visit[0].strftime('%H:%M') if hasattr(visit[0], 'strftime') else str(visit[0]))
            for op in operations:
                if op[0] is not None:
                    booked.add(op[0].strftime('%H:%M') if hasattr(op[0], 'strftime') else str(op[0]))

            all_hours = [f"{hour:02d}:00" for hour in range(8, 18)]
            available_hours = [hour for hour in all_hours if hour not in booked]

            return {
                'visits': visits,
                'operations': operations,
                'available_hours': available_hours
            }
    except Exception as e:
        logging.error(f"Error obtenint agenda de metge per {metge_usuario} i {dia}: {e}")
        return None