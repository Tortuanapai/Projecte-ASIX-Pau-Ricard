import os
import json
import re
import collections
import logging
import random
from datetime import datetime, timedelta
from contextlib import contextmanager
from faker import Faker
from psycopg2.extras import execute_values
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

def _ensure_dummy_indexes(conn):
    index_queries = [
        # --- Tus índices actuales (Excelentes para los JOINs y ordenaciones) ---
        "CREATE INDEX IF NOT EXISTS idx_visita_dia_visita ON visita(dia_visita)",
        "CREATE INDEX IF NOT EXISTS idx_visita_id_metge ON visita(id_metge)",
        "CREATE INDEX IF NOT EXISTS idx_visita_id_pacient ON visita(id_pacient)",
        "CREATE INDEX IF NOT EXISTS idx_operacio_dia_operacio ON operacio(dia_operacio)",
        "CREATE INDEX IF NOT EXISTS idx_operacio_id_metge ON operacio(id_metge)",
        "CREATE INDEX IF NOT EXISTS idx_operacio_id_pacient ON operacio(id_pacient)",
        "CREATE INDEX IF NOT EXISTS idx_reserva_habitacio_id_pacient ON reserva_habitacio(id_pacient)",
        "CREATE INDEX IF NOT EXISTS idx_infermeria_id_metge ON infermeria(id_metge)",
        "CREATE INDEX IF NOT EXISTS idx_infermeria_id_planta ON infermeria(id_planta)",
        
        # --- ¡ÍNDICES EXTRA DE RENDIMIENTO REQUERIDOS! ---
        
        # 1. B-Tree sobre el NSS del paciente: Es el campo de búsqueda de negocio más usado en un hospital.
        "CREATE INDEX IF NOT EXISTS idx_pacient_nss ON hospital_blanes.pacient(nss)",
        
        # 2. Índice Parcial para la eliminación masiva de datos dummy:
        # Al añadir el WHERE, el índice solo ocupa espacio para los datos de prueba,
        # haciendo que el borrado de 50k pacientes y 100k visitas sea instantáneo.
        "CREATE INDEX IF NOT EXISTS idx_pacient_descripcio_dummy ON hospital_blanes.pacient(descripcio) WHERE descripcio = 'DUMMY DATA'",
        "CREATE INDEX IF NOT EXISTS idx_visita_observacions_dummy ON visita(observacions) WHERE observacions = 'DUMMY DATA'"
    ]
    
    cur = conn.cursor()
    for query in index_queries:
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.warning(f'No se pudo crear índice: {e}')


def _clean_text(value):
    if not value:
        return None
    return value.replace('\n', ', ').strip()[:100]


def _create_or_get_planta_ids(cur):
    cur.execute('SELECT id_planta FROM planta ORDER BY id_planta')
    plant_rows = cur.fetchall()
    if plant_rows:
        return [row[0] for row in plant_rows]

    plants = [
        ('Primera', 'Ubicació planta primera', 'Activa'),
        ('Segona', 'Ubicació planta segona', 'Activa'),
        ('Tercera', 'Ubicació planta tercera', 'Activa'),
        ('Quarta', 'Ubicació planta quarta', 'Activa')
    ]
    cur.executemany('INSERT INTO planta (nom_planta, ubicacio, estat_actual) VALUES (%s, %s, %s)', plants)
    cur.execute('SELECT id_planta FROM planta ORDER BY id_planta')
    return [row[0] for row in cur.fetchall()]


def _create_default_quirofans(cur, plant_ids):
    cur.execute('SELECT COUNT(*) FROM quirofan')
    if cur.fetchone()[0] > 0:
        return
    quirofans = []
    for i, plant_id in enumerate(plant_ids[:4], start=1):
        quirofans.append((f'Q{i}', plant_id))
    cur.executemany('INSERT INTO quirofan (codi_quirofan, id_planta) VALUES (%s, %s)', quirofans)


def _create_default_habitacions(cur, plant_ids):
    cur.execute('SELECT COUNT(*) FROM habitacio')
    if cur.fetchone()[0] > 0:
        return
    sizes = ['Individual', 'Doble', 'Suite']
    habitacions = []
    for i in range(1, 21):
        habitacions.append((random.choice(sizes), f'Habitació {i}', 'Lliure', plant_ids[i % len(plant_ids)]))
    cur.executemany('INSERT INTO habitacio (tamany, ubicacio, estat, id_planta) VALUES (%s, %s, %s, %s)', habitacions)


def _normalize_name(value):
    return value.strip().title()


def _build_person_name(fake, cyrillic=False):
    if cyrillic:
        fake_ru = Faker('ru_RU')
        nom = fake_ru.first_name()
        primer_cognom = fake_ru.last_name()
        segon_cognom = fake_ru.last_name()
    else:
        nom = fake.first_name()
        primer_cognom = fake.last_name()
        segon_cognom = fake.last_name()
    return _normalize_name(nom), _normalize_name(primer_cognom), _normalize_name(segon_cognom)


def _batch_insert(cur, sql, rows, batch_size=1000):
    for start in range(0, len(rows), batch_size):
        execute_values(cur, sql, rows[start:start + batch_size])


def delete_dummy_data():
    marker = 'DUMMY DATA'
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Comprobación rápida inicial utilizando el esquema correcto
            cur.execute("SELECT COUNT(*) FROM hospital_blanes.pacient WHERE descripcio = %s", (marker,))
            paciente_count = cur.fetchone()[0]
            if paciente_count == 0:
                return False, 'No se encontró información dummy para eliminar.'

            logging.info('Eliminando datos dummy masivos (100k)... Por favor, espere.')

            # 1. Eliminar de tablas dependientes (Puentes) usando USING (Mucho más rápido que IN SELECT)
            cur.execute("""
                DELETE FROM visita_medicament 
                USING visita 
                WHERE visita_medicament.id_visita = visita.id_visita 
                  AND visita.observacions = %s
            """, (marker,))
            
            cur.execute("""
                DELETE FROM visita_diagnostic 
                USING visita 
                WHERE visita_diagnostic.id_visita = visita.id_visita 
                  AND visita.observacions = %s
            """, (marker,))

            # 2. Eliminar reservas de habitaciones asociadas a pacientes dummy
            cur.execute("""
                DELETE FROM reserva_habitacio 
                USING hospital_blanes.pacient 
                WHERE reserva_habitacio.id_pacient = pacient.id_pacient 
                  AND pacient.descripcio = %s
            """, (marker,))

            # 3. Eliminar asistencias y operaciones dummy
            cur.execute("""
                DELETE FROM assistencia_operacio 
                WHERE id_operacio IN (
                    SELECT o.id_operacio FROM operacio o
                    LEFT JOIN hospital_blanes.treballador t ON o.id_metge = t.id_treballador
                    LEFT JOIN hospital_blanes.pacient p ON o.id_pacient = p.id_pacient
                    WHERE t.observacions = %s OR p.descripcio = %s
                )
            """, (marker, marker))

            cur.execute("""
                DELETE FROM operacio 
                USING hospital_blanes.treballador, hospital_blanes.pacient
                WHERE (operacio.id_metge = treballador.id_treballador AND treballador.observacions = %s)
                   OR (operacio.id_pacient = pacient.id_pacient AND pacient.descripcio = %s)
            """, (marker, marker))

            # 4. Eliminar las 100.000 visitas (Crucial hacerlo ANTES de borrar empleados/pacientes)
            cur.execute("DELETE FROM visita WHERE observacions = %s", (marker,))

            # 5. Eliminar roles de empleados (Especializaciones) usando USING
            cur.execute("""
                DELETE FROM infermeria 
                USING hospital_blanes.treballador 
                WHERE infermeria.id_treballador = treballador.id_treballador AND treballador.observacions = %s
            """, (marker,))
            
            cur.execute("""
                DELETE FROM metge 
                USING hospital_blanes.treballador 
                WHERE metge.id_treballador = treballador.id_treballador AND treballador.observacions = %s
            """, (marker,))
            
            cur.execute("""
                DELETE FROM personal_vari 
                USING hospital_blanes.treballador 
                WHERE personal_vari.id_treballador = treballador.id_treballador AND treballador.observacions = %s
            """, (marker,))

            # 6. Finalmente, eliminar los registros base
            cur.execute("DELETE FROM hospital_blanes.pacient WHERE descripcio = %s", (marker,))
            cur.execute("DELETE FROM hospital_blanes.treballador WHERE observacions = %s", (marker,))
            
            conn.commit()
            return True, 'Se ha eliminado toda la información dummy de la base de datos.'
            
    except Exception as e:
        logging.error(f'Error eliminando dummy data: {e}')
        return False, f'Error al eliminar dummy data: {str(e)}'


def generate_dummy_data():
    marker = 'DUMMY DATA'
    fake_es = Faker('es_ES')
    fake_ru = Faker('ru_RU') # Instancia para la muestra requerida en alfabeto cirílico
    
    Faker.seed(0)
    random.seed(0)
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Verificar si ya existen datos para evitar duplicados
            cur.execute("SELECT COUNT(*) FROM hospital_blanes.pacient WHERE descripcio = %s", (marker,))
            if cur.fetchone()[0] > 0:
                return False, 'Ya existe información dummy en la base de datos.'

            # Estructura previa (Índices y catálogos fijos)
            _ensure_dummy_indexes(conn)
            plant_ids = _create_or_get_planta_ids(cur)
            _create_default_quirofans(cur, plant_ids)
            _create_default_habitacions(cur, plant_ids)
            conn.commit()

            # Configuración de los totales solicitados en la práctica
            total_medicos = 100
            total_enfermeras = 200
            total_limpieza = 100
            total_admin = 50
            total_trabajadores = total_medicos + total_enfermeras + total_limpieza + total_admin

            worker_rows = []
            doctor_rows = []
            nurse_rows = []
            cleaning_rows = []
            admin_rows = []
            
            specialities = ['Cardiología', 'Pediatría', 'Oncología', 'Dermatología', 'Ginecología', 'Neurología', 'Medicina Interna', 'Traumatología', 'Radiología', 'Psiquiatría']
            turns = ['Matí', 'Tarda', 'Nit']

            # 1. Generar estructuras de trabajadores (Con porción cirílica)
            for i in range(total_trabajadores):
                # Aplicamos alfabeto cirílico a un 10% de la muestra
                use_cyrillic = (i % 10 == 0)
                f = fake_ru if use_cyrillic else fake_es
                
                nom = f.first_name()
                primer_cognom = f.last_name()
                segon_cognom = f.last_name()
                address = _clean_text(f.address())
                nif = f'DUMMY{100000000 + i}'
                telefon = ''.join(str(random.randint(6, 9)) for _ in range(9))
                
                worker_rows.append((nif, nom, primer_cognom, segon_cognom, address, telefon, marker))
                
                if i < total_medicos:
                    doctor_rows.append((specialities[i % len(specialities)], turns[i % len(turns)], 'Estudis dummy', 'Currículum dummy'))
                elif i < (total_medicos + total_enfermeras):
                    nurse_rows.append((turns[i % len(turns)], 'Estudis dummy', 'Currículum dummy', None, plant_ids[i % len(plant_ids)]))
                elif i < (total_medicos + total_enfermeras + total_limpieza):
                    cleaning_rows.append(('Neteja', 'Personal de neteja dummy'))
                else:
                    admin_rows.append(('Administració', 'Personal d’administració dummy'))

            # Insertar los trabajadores base
            cur.executemany(
                'INSERT INTO hospital_blanes.treballador (nif, nom, primer_cognom, segon_cognom, adreça, telefon, observacions) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                worker_rows
            )
            conn.commit()

            # Obtener IDs seriales asignados por Postgres
            cur.execute("SELECT id_treballador FROM hospital_blanes.treballador WHERE observacions = %s ORDER BY id_treballador", (marker,))
            worker_ids = [row[0] for row in cur.fetchall()]
            
            doctor_ids = worker_ids[:total_medicos]
            nurse_ids = worker_ids[total_medicos:(total_medicos + total_enfermeras)]
            cleaning_ids = worker_ids[(total_medicos + total_enfermeras):(total_medicos + total_enfermeras + total_limpieza)]
            admin_ids = worker_ids[(total_medicos + total_enfermeras + total_limpieza):]

            # Insertar Médicos
            cur.executemany(
                'INSERT INTO metge (id_treballador, especialitat, torn, estudis, curriculum) VALUES (%s, %s, %s, %s, %s)',
                [(doctor_ids[idx], doctor_rows[idx][0], doctor_rows[idx][1], doctor_rows[idx][2], doctor_rows[idx][3]) for idx in range(len(doctor_rows))]
            )
            
            # Insertar Enfermeras
            infermeria_items = []
            for idx, worker_id in enumerate(nurse_ids):
                metge_id = random.choice(doctor_ids)
                planta_id = plant_ids[idx % len(plant_ids)]
                infermeria_items.append((worker_id, nurse_rows[idx][0], nurse_rows[idx][1], nurse_rows[idx][2], metge_id, planta_id))
            cur.executemany(
                'INSERT INTO infermeria (id_treballador, torn, estudis, curriculum, id_metge, id_planta) VALUES (%s, %s, %s, %s, %s, %s)',
                infermeria_items
            )

            # Insertar Personal Variado (Limpieza + Administración)
            cur.executemany(
                'INSERT INTO personal_vari (id_treballador, tipus_feina, descripcio) VALUES (%s, %s, %s)',
                [(worker_id, row[0], row[1]) for worker_id, row in zip(cleaning_ids + admin_ids, cleaning_rows + admin_rows)]
            )
            conn.commit()

            # 2. INSERTAR 50.000 PACIENTES EN LOTES (Para optimizar memoria)
            patient_batch_size = 5000
            patient_sql = 'INSERT INTO hospital_blanes.pacient (nom, nss, adreça, descripcio) VALUES (%s, %s, %s, %s)'
            patient_rows = []
            
            for j in range(50000):
                # Cada 10 pacientes, metemos uno con nombre en alfabeto cirílico
                use_cyrillic = (j % 10 == 0)
                f = fake_ru if use_cyrillic else fake_es
                
                nom_completo = f"{f.first_name()} {f.last_name()}"
                nss = f'200{j:011d}'
                address = _clean_text(f.address())
                
                patient_rows.append((nom_completo, nss, address, marker))
                
                if len(patient_rows) >= patient_batch_size:
                    cur.executemany(patient_sql, patient_rows)
                    conn.commit()
                    patient_rows = []
                    
            if patient_rows:
                cur.executemany(patient_sql, patient_rows)
                conn.commit()

            # Recorrer los IDs de pacientes generados para poder linkearlos con visitas
            cur.execute("SELECT id_pacient FROM hospital_blanes.pacient WHERE descripcio = %s ORDER BY id_pacient", (marker,))
            patient_ids = [row[0] for row in cur.fetchall()]

            # 3. INSERTAR 100.000 VISITAS EN LOTES DE COMITEO RÁPIDO
            visit_batch_size = 10000
            visit_sql = 'INSERT INTO visita (dia_visita, hora_visita, observacions, id_metge, id_pacient) VALUES (%s, %s, %s, %s, %s)'
            visit_rows = []
            base_date = datetime.today().date()
            
            for j in range(100000):
                dia = base_date - timedelta(days=random.randint(0, 365))
                hora = f'{random.randint(8, 18):02d}:{random.choice([0, 15, 30, 45]):02d}:00'
                visit_rows.append((dia, hora, marker, random.choice(doctor_ids), random.choice(patient_ids)))
                
                if len(visit_rows) >= visit_batch_size:
                    cur.executemany(visit_sql, visit_rows)
                    conn.commit()
                    visit_rows = []
                    
            if visit_rows:
                cur.executemany(visit_sql, visit_rows)
                conn.commit()

            return True, f'Éxito: Se han generado {total_trabajadores} trabajadores ({total_medicos} metges, {total_enfermeras} infermeres, {total_limpieza} neteja, {total_admin} adm.), 50.000 pacients y 100.000 visites (incluyendo muestras en alfabeto cirílico).'
            
    except Exception as e:
        logging.error(f'Error generando dummy data: {e}')
        return False, f'Error al generar dummy data: {str(e)}'


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


def get_visit_count_by_day(dia_visita):
    """Retorna el nombre de visites ateses per dia."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM visita WHERE dia_visita = %s",
                (dia_visita,)
            )
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        logging.error(f"Error obtenint nombre de visites per dia {dia_visita}: {e}")
        return 0


def get_doctor_patient_ranking(limit=20):
    """Retorna el rànquing de metges per nombre de pacients atesos."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT concat(t.nom, ' ', t.primer_cognom, ' ', t.segon_cognom) AS metge_nom,
                       COUNT(DISTINCT pacient_id) AS pacients_atesos
                FROM metge m
                JOIN treballador t ON m.id_treballador = t.id_treballador
                LEFT JOIN (
                    SELECT id_metge, id_pacient AS pacient_id FROM visita
                    UNION
                    SELECT id_metge, id_pacient AS pacient_id FROM operacio
                ) AS atendiments ON atendiments.id_metge = m.id_treballador
                GROUP BY metge_nom
                ORDER BY pacients_atesos DESC, metge_nom
                LIMIT %s
                """,
                (limit,)
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint rànquing de metges: {e}")
        return []


def get_common_diseases(limit=20):
    """Retorna les malalties més comunes basades en visites i operacions."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT m.nom AS malaltia_nom, COUNT(*) AS casos
                FROM malaltia m
                LEFT JOIN (
                    SELECT id_malaltia FROM visita
                    UNION ALL
                    SELECT id_malaltia FROM operacio
                ) AS casos ON casos.id_malaltia = m.id_malaltia
                GROUP BY malaltia_nom
                ORDER BY casos DESC, malaltia_nom
                LIMIT %s
                """,
                (limit,)
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint malalties comunes: {e}")
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


def get_planta_report(nom_planta):
    """Retorna el nombre d'habitacions, quiròfans i personal d'infermeria d'una planta."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT p.nom_planta,
                       COALESCE((SELECT COUNT(*) FROM habitacio h WHERE h.id_planta = p.id_planta), 0) AS habitacions,
                       COALESCE((SELECT COUNT(*) FROM quirofan q WHERE q.id_planta = p.id_planta), 0) AS quirofans,
                       COALESCE((SELECT COUNT(*) FROM infermeria i WHERE i.id_planta = p.id_planta), 0) AS infermeria
                FROM planta p
                WHERE p.nom_planta = %s
                """,
                (nom_planta,)
            )
            return cur.fetchone()
    except Exception as e:
        logging.error(f"Error obtenint informe de planta {nom_planta}: {e}")
        return None


def get_all_staff():
    """Retorna la llista de tot el personal que treballa a l'hospital."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nif,
                       nom_complet,
                       categoria,
                       detall,
                       torn
                FROM (
                    SELECT t.nif,
                           concat(t.nom, ' ', t.primer_cognom, ' ', t.segon_cognom) AS nom_complet,
                           'Metge' AS categoria,
                           m.especialitat AS detall,
                           m.torn AS torn
                    FROM treballador t
                    JOIN metge m ON t.id_treballador = m.id_treballador
                    UNION ALL
                    SELECT t.nif,
                           concat(t.nom, ' ', t.primer_cognom, ' ', t.segon_cognom),
                           'Infermer' AS categoria,
                           concat(
                               COALESCE(p.nom_planta, 'Sense planta'),
                               ' | Metge: ',
                               COALESCE(concat(tm.nom, ' ', tm.primer_cognom, ' ', tm.segon_cognom), 'Sense metge assignat')
                           ) AS detall,
                           i.torn AS torn
                    FROM treballador t
                    JOIN infermeria i ON t.id_treballador = i.id_treballador
                    LEFT JOIN planta p ON i.id_planta = p.id_planta
                    LEFT JOIN treballador tm ON i.id_metge = tm.id_treballador
                    UNION ALL
                    SELECT t.nif,
                           concat(t.nom, ' ', t.primer_cognom, ' ', t.segon_cognom),
                           'Personal Vari' AS categoria,
                           pv.tipus_feina AS detall,
                           NULL AS torn
                    FROM treballador t
                    JOIN personal_vari pv ON t.id_treballador = pv.id_treballador
                    UNION ALL
                    SELECT t.nif,
                           concat(t.nom, ' ', t.primer_cognom, ' ', t.segon_cognom),
                           'Treballador' AS categoria,
                           'No assignat a cap rol específic' AS detall,
                           NULL AS torn
                    FROM treballador t
                    WHERE t.id_treballador NOT IN (
                        SELECT id_treballador FROM metge
                        UNION
                        SELECT id_treballador FROM infermeria
                        UNION
                        SELECT id_treballador FROM personal_vari
                    )
                ) AS personal
                ORDER BY categoria, nom_complet
                """
            )
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Error obtenint l'informe de personal: {e}")
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
            cur.execute("SELECT nss FROM hospital_blanes.pacient WHERE nss = %s", (nss,))
            if cur.fetchone():
                return False, "El NSS ya está registrado"
            
            # Insertar paciente
            cur.execute("INSERT INTO hospital_blanes.pacient (nom, nss, adreça, descripcio) VALUES (%s, %s, %s, %s)",
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
                "SELECT id_pacient, nom FROM hospital_blanes.pacient WHERE nss = %s",
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
