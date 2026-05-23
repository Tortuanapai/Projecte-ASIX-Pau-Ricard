import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from funciones import (
    get_db_connection, registrar_log, validate_dni, validate_password,
    verify_credentials, get_pending_users, approve_user, reject_user,
    get_logs, direct_register_user, add_patient, get_infermer_dependency,
    get_quirofan_schedule, get_visit_schedule, get_quirofan_equipment,
    get_habitacio_reserves, get_planta_report, get_all_staff,
    get_visit_count_by_day, get_doctor_patient_ranking, get_common_diseases,
    get_patient_history, generate_dummy_data, delete_dummy_data,
    get_doctor_schedule
)

current_user = None
current_rol = None
root = None
pending_tree = None

PRIMARY_COLOR = '#0066cc'
SECONDARY_COLOR = '#004d99'
SUCCESS_COLOR = '#28a745'
DANGER_COLOR = '#dc3545'
BG_COLOR = '#f5f5f5'
TEXT_COLOR = '#333333'
HEADER_COLOR = '#003d7a'
LIGHT_BG = '#ffffff'

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR)
    style.configure('TButton', font=('Segoe UI', 10))
    style.configure('TEntry', font=('Segoe UI', 10))
    style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'))
    style.map('Primary.TButton', background=[('active', SECONDARY_COLOR)])

def create_header(show_logout=False):
    header = tk.Frame(root, bg=HEADER_COLOR, height=80)
    header.pack(fill=tk.X, side=tk.TOP)
    header.pack_propagate(False)
    
    title_frame = tk.Frame(header, bg=HEADER_COLOR)
    title_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
    
    title_label = tk.Label(title_frame, text='Hospital Blanes', font=('Segoe UI', 32, 'bold'),
                          bg=HEADER_COLOR, fg='white')
    title_label.pack(side=tk.LEFT)
    
    if show_logout:
        logout_btn = tk.Button(title_frame, text='Cerrar Sesion', command=logout,
                              bg=DANGER_COLOR, fg='white', font=('Segoe UI', 10, 'bold'),
                              padx=15, pady=8, relief=tk.FLAT, cursor='hand2')
        logout_btn.pack(side=tk.RIGHT)
    
    return header

def create_footer(back_command, show_logout=True):
    footer = tk.Frame(root, bg=BG_COLOR)
    footer.pack(fill=tk.X, side=tk.BOTTOM, padx=30, pady=20)
    
    back_btn = tk.Button(footer, text='Volver', command=back_command,
                        bg='#6c757d', fg='white', font=('Segoe UI', 10, 'bold'),
                        padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
    back_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    if show_logout:
        logout_btn = tk.Button(footer, text='Cerrar Sesion', command=logout,
                              bg=DANGER_COLOR, fg='white', font=('Segoe UI', 10, 'bold'),
                              padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
        logout_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    
    return footer

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def normalize_role(role):
    return role.strip().lower() if role else ''

def show_login_screen():
    global current_user, current_rol
    current_user = None
    current_rol = None
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    center_frame = tk.Frame(main_frame, bg=BG_COLOR)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    
    title = tk.Label(center_frame, text='Acceso con DNI', font=('Segoe UI', 24, 'bold'),
                    bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=(0, 30))
    
    input_frame = tk.Frame(center_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    
    user_label = tk.Label(input_frame, text='DNI:', font=('Segoe UI', 12),
                         bg=LIGHT_BG, fg=TEXT_COLOR)
    user_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    login_user_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    login_user_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    pass_label = tk.Label(input_frame, text='Contrasena:', font=('Segoe UI', 12),
                         bg=LIGHT_BG, fg=TEXT_COLOR)
    pass_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    login_pass_entry = ttk.Entry(input_frame, show='*', width=40, font=('Segoe UI', 11))
    login_pass_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    login_pass_entry.bind('<Return>', lambda e: login(login_user_entry.get(), login_pass_entry.get()))
    
    btn_frame = tk.Frame(center_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    
    login_btn = tk.Button(btn_frame, text='Iniciar Sesion', 
                         command=lambda: login(login_user_entry.get(), login_pass_entry.get()),
                         bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 12, 'bold'),
                         padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    login_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    register_btn = tk.Button(btn_frame, text='Registrarse',
                            command=show_register_screen,
                            bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 12, 'bold'),
                            padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    register_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

def login(dni, password):
    global current_user, current_rol
    dni = dni.strip()
    if not dni or not password:
        messagebox.showerror('Error', 'DNI y contrasena requeridos')
        return
    
    is_admin = dni.lower() == 'admin'
    if not is_admin:
        dni = dni.upper()
        if not validate_dni(dni):
            messagebox.showerror('Error', 'DNI no valido. Formato: 8 cifras y letra mayuscula.')
            return
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT password_hash, nom_rol FROM usuaris_registrats WHERE usuario = %s', (dni,))
            result = cur.fetchone()
            if result and verify_credentials(result[0], password):
                current_user = dni
                current_rol = result[1]
                registrar_log(dni, 'LOGIN', 'EXITO')
                show_panel()
            else:
                registrar_log(dni, 'LOGIN', 'FALLO')
                messagebox.showerror('Error', 'DNI o contrasena incorrectos')
    except Exception as e:
        messagebox.showerror('Error', f'Error en conexion: {str(e)}')
        registrar_log(dni, 'LOGIN', f'ERROR: {str(e)}')

def show_register_screen():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    center_frame = tk.Frame(main_frame, bg=BG_COLOR)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    
    title = tk.Label(center_frame, text='Registro de Nuevo DNI', font=('Segoe UI', 24, 'bold'),
                    bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=(0, 30))
    
    input_frame = tk.Frame(center_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    
    user_label = tk.Label(input_frame, text='DNI:', font=('Segoe UI', 12),
                         bg=LIGHT_BG, fg=TEXT_COLOR)
    user_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    user_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    user_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    pass_label = tk.Label(input_frame, text='Contrasena (minimo 8 caracteres):', font=('Segoe UI', 12),
                         bg=LIGHT_BG, fg=TEXT_COLOR)
    pass_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    pass_entry = ttk.Entry(input_frame, show='*', width=40, font=('Segoe UI', 11))
    pass_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    rol_label = tk.Label(input_frame, text='Rol:', font=('Segoe UI', 12),
                        bg=LIGHT_BG, fg=TEXT_COLOR)
    rol_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    rol_var = tk.StringVar(value='Infermer')
    roles = ['Medic', 'Infermer', 'Administratiu', 'dba']
    rol_combo = ttk.Combobox(input_frame, textvariable=rol_var, values=roles,
                            state='readonly', width=37, font=('Segoe UI', 11))
    rol_combo.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    def registrar():
        dni = user_entry.get().strip().upper()
        password = pass_entry.get()
        rol = rol_var.get()
        
        if not dni or not password:
            messagebox.showerror('Error', 'DNI y contrasena requeridos')
            return
        if not validate_dni(dni):
            messagebox.showerror('Error', 'DNI no valido. Formato: 8 cifras y letra mayuscula.')
            return
        if not validate_password(password):
            messagebox.showerror('Error', 'La contrasena debe tener minimo 8 caracteres')
            return
        
        try:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO usuaris_pendents (usuario, password_hash, nom_rol) VALUES (%s, %s, %s)',
                           (dni, password_hash, rol))
                conn.commit()
            messagebox.showinfo('Exito', 'DNI registrado. Espera la aprobacion del administrador.')
            registrar_log(dni, 'REGISTRO', 'EXITO')
            show_login_screen()
        except Exception as e:
            messagebox.showerror('Error', f'Error en registro: {str(e)}')
            registrar_log(dni, 'REGISTRO', f'ERROR: {str(e)}')
    
    btn_frame = tk.Frame(center_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    
    register_btn = tk.Button(btn_frame, text='Registrarse', command=registrar,
                            bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 12, 'bold'),
                            padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    register_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    back_btn = tk.Button(btn_frame, text='Volver', command=show_login_screen,
                        bg='#6c757d', fg='white', font=('Segoe UI', 12, 'bold'),
                        padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    back_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

def show_panel():
    rol = normalize_role(current_rol)
    if rol == 'administratiu':
        show_administratiu_panel()
    elif rol == 'dba':
        show_dba_panel()
    else:
        show_user_panel()

def show_user_panel():
    clear_window()
    create_header(show_logout=True)
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    welcome = tk.Label(main_frame, text=f'Bienvenido, {current_user}', 
                      font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    welcome.pack(anchor=tk.W, pady=(0, 20))
    
    rol_label = tk.Label(main_frame, text=f'Rol: {current_rol}',
                        font=('Segoe UI', 12), bg=BG_COLOR, fg=TEXT_COLOR)
    rol_label.pack(anchor=tk.W, pady=(0, 30))
    
    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(fill=tk.X, pady=(0, 30))
    
    tk.Button(btn_frame, text='Ver Mi Perfil', command=show_profile,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    if current_rol in ['Metge', 'Medic']:
        tk.Button(btn_frame, text='Mi Agenda', command=show_doctor_schedule,
                 bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    if current_rol in ['Metge', 'Medic', 'Infermer']:
        tk.Button(btn_frame, text='Enfermedades Comunes', command=show_common_diseases,
                 bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text='Agenda Visitas', command=show_visit_schedule,
                 bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text='Historia Paciente', command=show_patient_history,
                 bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
        
        if current_rol in ['Metge', 'Medic']:
            tk.Button(btn_frame, text='Ranking Medicos', command=show_top_doctors,
                     bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                     padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
            
            tk.Button(btn_frame, text='Agenda Quirofanos', command=show_operating_schedule,
                     bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                     padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    create_footer(show_panel)

def show_administratiu_panel():
    clear_window()
    create_header(show_logout=True)
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    welcome = tk.Label(main_frame, text=f'Panel Administrativo - {current_user}',
                      font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    welcome.pack(anchor=tk.W, pady=(0, 30))
    
    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(fill=tk.X)
    
    tk.Label(btn_frame, text='Gestion de Pacientes', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(0, 10))
    tk.Button(btn_frame, text='Dar de Alta Paciente', command=show_add_patient,
             bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Informes', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Informe Planta', command=show_planta_report,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Informe Personal', command=show_all_staff,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Visitas por Dia', command=show_visit_count,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Enfermedades Comunes', command=show_common_diseases,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Consultas', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Reservas Habitaciones', command=show_habitacio_reserves,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Historia Paciente', command=show_patient_history,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Equipamiento Quirofan', command=show_quirofan_equipment,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Datos Dummy', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Generar Dummy Data', command=confirm_generate_dummy_data,
             bg='#17a2b8', fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Eliminar Dummy Data', command=confirm_delete_dummy_data,
             bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    create_footer(show_panel)

def show_dba_panel():
    clear_window()
    create_header(show_logout=True)
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    welcome = tk.Label(main_frame, text=f'Panel DBA - {current_user}',
                      font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    welcome.pack(anchor=tk.W, pady=(0, 30))
    
    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(fill=tk.X)
    
    tk.Label(btn_frame, text='Gestion de Usuarios', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(0, 10))
    tk.Button(btn_frame, text='Usuarios Pendientes', command=show_pending_users,
             bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Alta Directa de Usuario', command=show_direct_register,
             bg='#17a2b8', fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Ver Logs', command=show_logs,
             bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Informes', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Informe Planta', command=show_planta_report,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Informe Personal', command=show_all_staff,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Ranking Medicos', command=show_top_doctors,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Visitas por Dia', command=show_visit_count,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Enfermedades Comunes', command=show_common_diseases,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Agendas', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Agenda Quirofanos', command=show_operating_schedule,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Agenda Visitas', command=show_visit_schedule,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Consultas', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Historia Paciente', command=show_patient_history,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Equipamiento Quirofan', command=show_quirofan_equipment,
             bg=SECONDARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Dar de Alta Paciente', command=show_add_patient,
             bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    tk.Label(btn_frame, text='Datos Dummy', font=('Segoe UI', 12, 'bold'),
            bg=BG_COLOR, fg=HEADER_COLOR).pack(anchor=tk.W, pady=(20, 10))
    tk.Button(btn_frame, text='Generar Dummy Data', command=confirm_generate_dummy_data,
             bg='#17a2b8', fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text='Eliminar Dummy Data', command=confirm_delete_dummy_data,
             bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
             padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(fill=tk.X, pady=5)
    
    create_footer(show_panel)

def show_pending_users():
    global pending_tree
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Usuarios Pendientes de Aprobacion',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    try:
        users = get_pending_users()
        if not users:
            empty_label = tk.Label(main_frame, text='No hay usuarios pendientes',
                                  font=('Segoe UI', 14), bg=BG_COLOR, fg=SUCCESS_COLOR)
            empty_label.pack(pady=40)
        else:
            table_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
            table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            pending_tree = ttk.Treeview(table_frame, columns=('ID', 'DNI', 'Rol'),
                                       height=15, show='tree headings')
            pending_tree.column('#0', width=0, stretch=tk.NO)
            pending_tree.column('ID', anchor=tk.W, width=60)
            pending_tree.column('DNI', anchor=tk.W, width=300)
            pending_tree.column('Rol', anchor=tk.W, width=300)
            pending_tree.heading('#0', text='')
            pending_tree.heading('ID', text='ID')
            pending_tree.heading('DNI', text='DNI')
            pending_tree.heading('Rol', text='Rol')
            
            for user in users:
                pending_tree.insert('', 'end', values=(user[0], user[1], user[2]))
            
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=pending_tree.yview)
            pending_tree.configure(yscroll=scrollbar.set)
            pending_tree.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')
            table_frame.grid_rowconfigure(0, weight=1)
            table_frame.grid_columnconfigure(0, weight=1)
            
            action_frame = tk.Frame(main_frame, bg=BG_COLOR)
            action_frame.pack(fill=tk.X, pady=(0, 20))
            
            tk.Button(action_frame, text='Aprobar DNI', command=approve_pending_user,
                     bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                     padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            tk.Button(action_frame, text='Rechazar DNI', command=reject_pending_user,
                     bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                     padx=20, pady=10, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    except Exception as e:
        messagebox.showerror('Error', f'Error al cargar usuarios: {str(e)}')
    
    create_footer(show_panel)

def approve_pending_user():
    if pending_tree is None:
        return
    selection = pending_tree.selection()
    if not selection:
        messagebox.showwarning('Advertencia', 'Selecciona un DNI')
        return
    
    user_id = pending_tree.item(selection[0])['values'][0]
    try:
        success, dni = approve_user(user_id)
        if success:
            messagebox.showinfo('Exito', f"DNI '{dni}' aprobado correctamente")
            registrar_log(current_user, 'APROBAR_USUARIO', f'DNI {dni} aprobado')
            show_pending_users()
        else:
            messagebox.showerror('Error', 'No se pudo aprobar el DNI')
    except Exception as e:
        messagebox.showerror('Error', f'Error: {str(e)}')

def reject_pending_user():
    if pending_tree is None:
        return
    selection = pending_tree.selection()
    if not selection:
        messagebox.showwarning('Advertencia', 'Selecciona un DNI')
        return
    
    user_id = pending_tree.item(selection[0])['values'][0]
    dni_value = pending_tree.item(selection[0])['values'][1]
    
    if messagebox.askyesno('Confirmar', f"Rechazar al DNI '{dni_value}'?"):
        try:
            success, dni = reject_user(user_id)
            if success:
                messagebox.showinfo('Exito', f"DNI '{dni}' rechazado")
                registrar_log(current_user, 'RECHAZAR_USUARIO', f'DNI {dni} rechazado')
                show_pending_users()
            else:
                messagebox.showerror('Error', 'No se pudo rechazar el DNI')
        except Exception as e:
            messagebox.showerror('Error', f'Error: {str(e)}')

def show_direct_register():
    if current_rol != 'dba':
        messagebox.showerror('Error', 'Solo DBA puede acceder a esta funcion')
        return
    
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Alta Directa de Usuario (DBA)',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 30))
    
    input_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    
    user_label = tk.Label(input_frame, text='DNI:', font=('Segoe UI', 12),
                         bg=LIGHT_BG, fg=TEXT_COLOR)
    user_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    user_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    user_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    pass_label = tk.Label(input_frame, text='Contrasena (minimo 8 caracteres):', font=('Segoe UI', 12),
                         bg=LIGHT_BG, fg=TEXT_COLOR)
    pass_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    pass_entry = ttk.Entry(input_frame, show='*', width=40, font=('Segoe UI', 11))
    pass_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    rol_label = tk.Label(input_frame, text='Rol:', font=('Segoe UI', 12),
                        bg=LIGHT_BG, fg=TEXT_COLOR)
    rol_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    rol_var = tk.StringVar(value='Infermer')
    roles = ['Medic', 'Infermer', 'Administratiu', 'dba']
    rol_combo = ttk.Combobox(input_frame, textvariable=rol_var, values=roles,
                            state='readonly', width=37, font=('Segoe UI', 11))
    rol_combo.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    def registrar_directo():
        dni = user_entry.get().strip().upper()
        password = pass_entry.get()
        rol = rol_var.get()
        success, message = direct_register_user(dni, password, rol)
        if success:
            messagebox.showinfo('Exito', message)
            registrar_log(current_user, 'REGISTRO_DIRECTO', f'DNI {dni} rol {rol}')
            user_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            rol_var.set('Infermer')
        else:
            messagebox.showerror('Error', message)
    
    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    
    tk.Button(btn_frame, text='Registrar Usuario', command=registrar_directo,
             bg='#17a2b8', fg='white', font=('Segoe UI', 12, 'bold'),
             padx=30, pady=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    tk.Button(btn_frame, text='Volver', command=show_panel,
             bg='#6c757d', fg='white', font=('Segoe UI', 12, 'bold'),
             padx=30, pady=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    create_footer(show_panel, show_logout=False)

def show_add_patient():
    if current_rol != 'Administratiu':
        messagebox.showerror('Error', 'Solo los administrativos pueden anadir pacientes')
        return
    
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Alta de Nuevo Paciente',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 30))
    
    input_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    
    nom_label = tk.Label(input_frame, text='Nombre:', font=('Segoe UI', 12),
                        bg=LIGHT_BG, fg=TEXT_COLOR)
    nom_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    nom_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    nom_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    nss_label = tk.Label(input_frame, text='NSS (15 caracteres):', font=('Segoe UI', 12),
                        bg=LIGHT_BG, fg=TEXT_COLOR)
    nss_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    nss_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    nss_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    adreça_label = tk.Label(input_frame, text='Direccion:', font=('Segoe UI', 12),
                           bg=LIGHT_BG, fg=TEXT_COLOR)
    adreça_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    adreça_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    adreça_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    descripcio_label = tk.Label(input_frame, text='Descripcion:', font=('Segoe UI', 12),
                               bg=LIGHT_BG, fg=TEXT_COLOR)
    descripcio_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    descripcio_text = scrolledtext.ScrolledText(input_frame, height=4, font=('Segoe UI', 11))
    descripcio_text.pack(padx=15, pady=(0, 15), fill=tk.X)
    
    def anadir_paciente():
        nom = nom_entry.get().strip()
        nss = nss_entry.get().strip()
        adreça = adreça_entry.get().strip()
        descripcio = descripcio_text.get('1.0', tk.END).strip()
        success, message = add_patient(nom, nss, adreça, descripcio)
        if success:
            messagebox.showinfo('Exito', message)
            registrar_log(current_user, 'ALTA_PACIENTE', f'Paciente {nom} (NSS: {nss})')
            nom_entry.delete(0, tk.END)
            nss_entry.delete(0, tk.END)
            adreça_entry.delete(0, tk.END)
            descripcio_text.delete('1.0', tk.END)
        else:
            messagebox.showerror('Error', message)
    
    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    
    tk.Button(btn_frame, text='Anadir Paciente', command=anadir_paciente,
             bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 12, 'bold'),
             padx=30, pady=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    tk.Button(btn_frame, text='Volver', command=show_panel,
             bg='#6c757d', fg='white', font=('Segoe UI', 12, 'bold'),
             padx=30, pady=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    create_footer(show_panel, show_logout=False)

def show_logs():
    if current_rol not in ['Administratiu', 'dba']:
        messagebox.showerror('Error', 'Solo el administrador puede ver los logs')
        return
    
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Logs de Acceso al Sistema',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    try:
        logs = get_logs()
        text_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        text_widget = scrolledtext.ScrolledText(text_frame, height=20, font=('Consolas', 9),
                                               bg='#f8f9fa', fg=TEXT_COLOR, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.config(state=tk.NORMAL)
        
        for log in logs:
            text_widget.insert(tk.END, log)
        
        text_widget.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror('Error', f'Error al cargar logs: {str(e)}')
    
    create_footer(show_panel)

def show_profile():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    profile_card = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    profile_card.pack(fill=tk.X, padx=100, pady=60)
    
    title = tk.Label(profile_card, text='Mi Perfil', font=('Segoe UI', 22, 'bold'),
                    bg=LIGHT_BG, fg=HEADER_COLOR)
    title.pack(pady=30)
    
    info_frame = tk.Frame(profile_card, bg='#f8f9fa')
    info_frame.pack(fill=tk.X, padx=30, pady=20)
    
    user_info = tk.Label(info_frame, text=f'DNI: {current_user}',
                        font=('Segoe UI', 14), bg='#f8f9fa', fg=TEXT_COLOR, justify=tk.LEFT)
    user_info.pack(anchor=tk.W, pady=15)
    
    rol_info = tk.Label(info_frame, text=f'Rol: {current_rol.capitalize()}',
                       font=('Segoe UI', 14), bg='#f8f9fa', fg=TEXT_COLOR, justify=tk.LEFT)
    rol_info.pack(anchor=tk.W, pady=15)
    
    if current_rol == 'Infermer':
        infermer_info = get_infermer_dependency(current_user)
        infermer_text = infermer_info or "No hay informacion de asignacion"
        dependency_info = tk.Label(info_frame, text=f'Enfermeria: {infermer_text}',
                                  font=('Segoe UI', 14), bg='#f8f9fa', fg=TEXT_COLOR,
                                  justify=tk.LEFT, wraplength=600)
        dependency_info.pack(anchor=tk.W, pady=15)
    
    create_footer(show_panel)

def show_operating_schedule():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Agenda de Quirofanos',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    
    date_label = tk.Label(search_frame, text='Fecha (YYYY-MM-DD):', font=('Segoe UI', 12),
                         bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.pack(side=tk.LEFT, padx=(0, 10))
    
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    def load_schedule():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha invalido. Usa YYYY-MM-DD.')
            return
        
        for item in schedule_tree.get_children():
            schedule_tree.delete(item)
        
        rows = get_quirofan_schedule(selected_date)
        if not rows:
            messagebox.showinfo('Info', 'No hay operaciones programadas para esta fecha.')
            return
        
        for row in rows:
            schedule_tree.insert('', tk.END, values=(row[0], row[1].strftime('%H:%M') if hasattr(row[1], 'strftime') else row[1],
                                                     row[2], row[3], row[4], row[5]))
    
    load_btn = tk.Button(search_frame, text='Cargar Agenda', command=load_schedule,
                        bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                        padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.pack(side=tk.LEFT)
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Quirofan', 'Hora', 'Pacient', 'NSS', 'Medico', 'Infermeros')
    schedule_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        schedule_tree.heading(col, text=col)
        schedule_tree.column(col, anchor=tk.W, width=150)
    
    schedule_tree.column('Pacient', width=220)
    schedule_tree.column('Infermeros', width=260)
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=schedule_tree.yview)
    schedule_tree.configure(yscroll=vsb.set)
    schedule_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    create_footer(show_panel)

def show_quirofan_equipment():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Equipamiento de Quirofan',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Quirofan', 'Planta', 'Aparato', 'Cantidad')
    equipment_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        equipment_tree.heading(col, text=col)
        equipment_tree.column(col, anchor=tk.W, width=180)
    
    equipment_tree.column('Aparato', width=260)
    equipment_tree.grid(row=0, column=0, sticky='nsew')
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=equipment_tree.yview)
    equipment_tree.configure(yscroll=vsb.set)
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    rows = get_quirofan_equipment()
    if not rows:
        messagebox.showinfo('Info', 'No hay equipos asignados a los quirofanos.')
    else:
        for row in rows:
            equipment_tree.insert('', tk.END, values=(row[0], row[1] or '-', row[2], row[3]))
    
    create_footer(show_panel)

def show_habitacio_reserves():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Reservas Habitaciones',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    room_var = tk.StringVar()
    
    room_label = tk.Label(search_frame, text='ID Habitacion:', font=('Segoe UI', 12),
                         bg=BG_COLOR, fg=TEXT_COLOR)
    room_label.pack(side=tk.LEFT, padx=(0, 10))
    
    room_entry = ttk.Entry(search_frame, textvariable=room_var, width=20, font=('Segoe UI', 11))
    room_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    def load_reserves():
        room_id = room_var.get().strip()
        if not room_id:
            messagebox.showerror('Error', "Introduce el ID de la habitacion")
            return
        try:
            room_id = int(room_id)
        except ValueError:
            messagebox.showerror('Error', 'El ID debe ser un numero')
            return
        
        for item in reserves_tree.get_children():
            reserves_tree.delete(item)
        
        rows = get_habitacio_reserves(room_id)
        if not rows:
            messagebox.showinfo('Info', 'No hay reservas para esta habitacion')
            return
        
        for row in rows:
            reserves_tree.insert('', tk.END, values=(row[0], row[1] if row[1] else 'Sin fecha', row[2]))
        
        registrar_log(current_user, 'VER_RESERVES_HABITACIO', f'ID Habitacion: {room_id}')
    
    load_btn = tk.Button(search_frame, text='Cargar Reservas', command=load_reserves,
                        bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                        padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.pack(side=tk.LEFT)
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Fecha Ingreso', 'Fecha Salida', 'Paciente')
    reserves_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        reserves_tree.heading(col, text=col)
        reserves_tree.column(col, anchor=tk.W, width=200)
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=reserves_tree.yview)
    reserves_tree.configure(yscroll=vsb.set)
    reserves_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    create_footer(show_panel)

def show_planta_report():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Informe de Planta',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    planta_var = tk.StringVar()
    
    planta_label = tk.Label(search_frame, text='Planta:', font=('Segoe UI', 12),
                           bg=BG_COLOR, fg=TEXT_COLOR)
    planta_label.pack(side=tk.LEFT, padx=(0, 10))
    
    planta_combo = ttk.Combobox(search_frame, textvariable=planta_var,
                               values=['Primera', 'Segunda', 'Tercera', 'Cuarta'],
                               state='readonly', width=24, font=('Segoe UI', 11))
    planta_combo.pack(side=tk.LEFT, padx=(0, 10))
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    info_title = tk.Label(result_frame, text='Resultado', font=('Segoe UI', 18, 'bold'),
                         bg=LIGHT_BG, fg=HEADER_COLOR)
    info_title.pack(anchor=tk.W, padx=20, pady=(20, 10))
    
    habitacions_label = tk.Label(result_frame, text='Habitaciones: -', font=('Segoe UI', 14),
                                bg=LIGHT_BG, fg=TEXT_COLOR)
    habitacions_label.pack(anchor=tk.W, padx=20, pady=10)
    
    quirofans_label = tk.Label(result_frame, text='Quirofanos: -', font=('Segoe UI', 14),
                              bg=LIGHT_BG, fg=TEXT_COLOR)
    quirofans_label.pack(anchor=tk.W, padx=20, pady=10)
    
    infermeria_label = tk.Label(result_frame, text='Personal de enfermeria: -', font=('Segoe UI', 14),
                               bg=LIGHT_BG, fg=TEXT_COLOR)
    infermeria_label.pack(anchor=tk.W, padx=20, pady=10)
    
    def load_planta_report():
        planta = planta_var.get().strip()
        if not planta:
            messagebox.showerror('Error', 'Selecciona una planta.')
            return
        
        row = get_planta_report(planta)
        if not row:
            messagebox.showinfo('Info', 'No hay informacion para esta planta.')
            habitacions_label.config(text='Habitaciones: 0')
            quirofans_label.config(text='Quirofanos: 0')
            infermeria_label.config(text='Personal de enfermeria: 0')
            return
        
        _, habitacions, quirofans, infermeria = row
        habitacions_label.config(text=f'Habitaciones: {habitacions}')
        quirofans_label.config(text=f'Quirofanos: {quirofans}')
        infermeria_label.config(text=f'Personal de enfermeria: {infermeria}')
        registrar_log(current_user, 'CONSULTA_INFORME_PLANTA', f'Planta: {planta}')
    
    consult_btn = tk.Button(search_frame, text='Consultar', command=load_planta_report,
                           bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                           padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    consult_btn.pack(side=tk.LEFT)
    
    create_footer(show_panel)

def show_all_staff():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Informe de Personal',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('NIF', 'Nombre Completo', 'Categoria', 'Detalle', 'Turno')
    staff_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        staff_tree.heading(col, text=col)
        staff_tree.column(col, anchor=tk.W, width=180)
    
    staff_tree.column('Detalle', width=320)
    staff_tree.column('Nombre Completo', width=240)
    staff_tree.grid(row=0, column=0, sticky='nsew')
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=staff_tree.yview)
    staff_tree.configure(yscroll=vsb.set)
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    rows = get_all_staff()
    if not rows:
        messagebox.showinfo('Info', 'No hay personal registrado.')
    else:
        for row in rows:
            staff_tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], row[4] or '-'))
    
    registrar_log(current_user, 'CONSULTA_INFORME_PERSONAL', 'Lista de todo el personal')
    create_footer(show_panel)

def show_visit_count():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Visitas por Dia',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    
    date_label = tk.Label(search_frame, text='Fecha (YYYY-MM-DD):', font=('Segoe UI', 12),
                         bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.pack(side=tk.LEFT, padx=(0, 10))
    
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    count_label = tk.Label(main_frame, text='Visitas atendidas: -', font=('Segoe UI', 18),
                          bg=BG_COLOR, fg=TEXT_COLOR)
    count_label.pack(anchor=tk.W, pady=(0, 30))
    
    def load_count():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha invalido. Usa YYYY-MM-DD.')
            return
        
        count = get_visit_count_by_day(selected_date)
        count_label.config(text=f'Visitas atendidas: {count}')
        registrar_log(current_user, 'CONSULTA_VISITES_PER_DIA', f'Fecha: {selected_date}')
    
    load_btn = tk.Button(search_frame, text='Consultar', command=load_count,
                        bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                        padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.pack(side=tk.LEFT)
    
    create_footer(show_panel)

def show_top_doctors():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Ranking de Medicos',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Medico', 'Pacientes Atendidos')
    doctor_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        doctor_tree.heading(col, text=col)
        doctor_tree.column(col, anchor=tk.W, width=260)
    
    doctor_tree.column('Pacientes Atendidos', width=180)
    doctor_tree.grid(row=0, column=0, sticky='nsew')
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=doctor_tree.yview)
    doctor_tree.configure(yscroll=vsb.set)
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    rows = get_doctor_patient_ranking()
    if not rows:
        messagebox.showinfo('Info', 'No hay medicos con atenciones registradas.')
    else:
        for row in rows:
            doctor_tree.insert('', tk.END, values=(row[0], row[1]))
    
    registrar_log(current_user, 'VER_RANKING_MEDICOS', 'Ranking de medicos por pacientes atendidos')
    create_footer(show_panel)

def show_common_diseases():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Enfermedades Comunes',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Enfermedad', 'Casos')
    disease_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        disease_tree.heading(col, text=col)
        disease_tree.column(col, anchor=tk.W, width=260)
    
    disease_tree.column('Casos', width=180)
    disease_tree.grid(row=0, column=0, sticky='nsew')
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=disease_tree.yview)
    disease_tree.configure(yscroll=vsb.set)
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    rows = get_common_diseases()
    if not rows:
        messagebox.showinfo('Info', 'No hay enfermedades registradas.')
    else:
        for row in rows:
            disease_tree.insert('', tk.END, values=(row[0], row[1]))
    
    registrar_log(current_user, 'VER_MALALTIES_COMUNS', 'Enfermedades comunes')
    create_footer(show_panel)

def show_visit_schedule():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Agenda de Visitas',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    
    date_label = tk.Label(search_frame, text='Fecha (YYYY-MM-DD):', font=('Segoe UI', 12),
                         bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.pack(side=tk.LEFT, padx=(0, 10))
    
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    def load_visits():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha invalido. Usa YYYY-MM-DD.')
            return
        
        for item in visits_tree.get_children():
            visits_tree.delete(item)
        
        rows = get_visit_schedule(selected_date)
        if not rows:
            messagebox.showinfo('Info', 'No hay visitas programadas para esta fecha.')
            return
        
        for row in rows:
            visits_tree.insert('', tk.END, values=(row[0].strftime('%H:%M') if hasattr(row[0], 'strftime') else row[0],
                                                   row[1], row[2], row[3]))
    
    load_btn = tk.Button(search_frame, text='Cargar Visitas', command=load_visits,
                        bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                        padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.pack(side=tk.LEFT)
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Hora', 'Medico', 'Paciente', 'NSS')
    visits_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    
    for col in columns:
        visits_tree.heading(col, text=col)
        visits_tree.column(col, anchor=tk.W, width=180)
    
    visits_tree.column('Paciente', width=220)
    visits_tree.column('Medico', width=220)
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=visits_tree.yview)
    visits_tree.configure(yscroll=vsb.set)
    visits_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    
    create_footer(show_panel)

def show_doctor_schedule():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Mi Agenda',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    
    date_label = tk.Label(search_frame, text='Fecha (YYYY-MM-DD):', font=('Segoe UI', 12),
                         bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.pack(side=tk.LEFT, padx=(0, 10))
    
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    def load_schedule():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha invalido. Usa YYYY-MM-DD.')
            return
        
        for item in schedule_tree.get_children():
            schedule_tree.delete(item)
        
        for item in available_tree.get_children():
            available_tree.delete(item)
        
        schedule = get_doctor_schedule(current_user, selected_date)
        if schedule is None:
            messagebox.showerror('Error', "No se ha podido obtener la agenda del medico.")
            return
        
        if not schedule['visits'] and (not schedule['operations']):
            messagebox.showinfo('Info', 'No tienes visitas ni operaciones programadas para esta fecha.')
        
        for visit in schedule['visits']:
            schedule_tree.insert('', tk.END, values=('Visita', visit[0].strftime('%H:%M') if hasattr(visit[0], 'strftime') else visit[0],
                                                     visit[1], visit[2], '-'))
        
        for op in schedule['operations']:
            schedule_tree.insert('', tk.END, values=('Operacion', op[0].strftime('%H:%M') if hasattr(op[0], 'strftime') else op[0],
                                                     op[1], op[2], op[3]))
        
        if schedule['available_hours']:
            for hour in schedule['available_hours']:
                available_tree.insert('', tk.END, values=(hour,))
        else:
            available_tree.insert('', tk.END, values=('Sin horas disponibles (08:00-17:00)',))
        
        registrar_log(current_user, 'VER_AGENDA_MEDICO', f'Fecha={selected_date}')
    
    load_btn = tk.Button(search_frame, text='Cargar Agenda', command=load_schedule,
                        bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                        padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.pack(side=tk.LEFT)
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    columns = ('Tipo', 'Hora', 'Paciente', 'NSS', 'Quirofan')
    schedule_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=12)
    
    for col in columns:
        schedule_tree.heading(col, text=col)
        schedule_tree.column(col, anchor=tk.W, width=140)
    
    schedule_tree.column('Paciente', width=220)
    schedule_tree.column('Quirofan', width=140)
    schedule_tree.grid(row=0, column=0, sticky='nsew', padx=(0, 0), pady=(0, 10))
    
    available_label = tk.Label(result_frame, text='Horas disponibles (08:00-17:00):', 
                              font=('Segoe UI', 12, 'bold'), bg=LIGHT_BG, fg=TEXT_COLOR)
    available_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=(10, 5))
    
    available_tree = ttk.Treeview(result_frame, columns=('Hora',), show='headings', height=6)
    available_tree.heading('Hora', text='Hora')
    available_tree.column('Hora', anchor=tk.W, width=120)
    available_tree.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 10))
    
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=schedule_tree.yview)
    schedule_tree.configure(yscroll=vsb.set)
    vsb.grid(row=0, column=1, sticky='ns', rowspan=3)
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_rowconfigure(2, weight=0)
    result_frame.grid_columnconfigure(0, weight=1)
    
    create_footer(show_panel)

def show_patient_history():
    clear_window()
    create_header()
    
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title = tk.Label(main_frame, text='Historia de Paciente',
                    font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W, pady=(0, 20))
    
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 20))
    
    nss_var = tk.StringVar()
    
    nss_label = tk.Label(search_frame, text='NSS del Paciente:', font=('Segoe UI', 12),
                        bg=BG_COLOR, fg=TEXT_COLOR)
    nss_label.pack(side=tk.LEFT, padx=(0, 10))
    
    nss_entry = ttk.Entry(search_frame, textvariable=nss_var, width=30, font=('Segoe UI', 11))
    nss_entry.pack(side=tk.LEFT, padx=(0, 10))
    
    def load_history():
        nss = nss_var.get().strip()
        if not nss:
            messagebox.showerror('Error', 'Introduce el NSS del paciente')
            return
        if len(nss) != 15:
            messagebox.showerror('Error', 'El NSS debe tener 15 caracteres')
            return
        
        history = get_patient_history(nss)
        if not history:
            messagebox.showinfo('Info', "No se ha encontrado ningun paciente con este NSS")
            return
        
        text_area.config(state=tk.NORMAL)
        text_area.delete('1.0', tk.END)
        text_area.insert(tk.END, f"Paciente: {history['nom']}\n")
        text_area.insert(tk.END, f"NSS: {history['nss']}\n")
        text_area.insert(tk.END, f"Visitas totales: {len(history['visits'])}\n")
        text_area.insert(tk.END, f"Ingresos totales: {history['admissions_count']}\n")
        text_area.insert(tk.END, f"Operaciones totales: {history['operation_count']}\n\n")
        text_area.insert(tk.END, 'Diagnosticos:\n')
        if history['diagnostics']:
            for diag in history['diagnostics']:
                text_area.insert(tk.END, f' - {diag[0]}\n')
        else:
            text_area.insert(tk.END, ' - Sin diagnostico registrado\n')
        text_area.insert(tk.END, '\n')
        text_area.insert(tk.END, 'Medicamentos prescritos:\n')
        if history['medications']:
            for med in history['medications']:
                dosis = med[2] or 'Sin dosis'
                pauta = med[3] or 'Sin pauta'
                text_area.insert(tk.END, f' - {med[0]} ({med[1]}) | Dosi: {dosis} | Pauta: {pauta} | Fecha visita: {med[4]}\n')
        else:
            text_area.insert(tk.END, ' - Sin medicamentos registrados\n')
        text_area.insert(tk.END, '\n')
        text_area.insert(tk.END, 'Detalle de visitas:\n')
        if history['visits']:
            for visita in history['visits']:
                hora = visita[1].strftime('%H:%M') if hasattr(visita[1], 'strftime') else visita[1]
                observaciones = visita[2] if visita[2] else 'Sin observaciones'
                text_area.insert(tk.END, f' - {visita[0]} {hora} | Medico: {visita[3]} | Observaciones: {observaciones}\n')
        else:
            text_area.insert(tk.END, ' - Sin visitas registradas\n')
        text_area.config(state=tk.DISABLED)
        registrar_log(current_user, 'VER_HISTORIA_PACIENTE', f'NSS={nss}')
    
    load_btn = tk.Button(search_frame, text='Buscar', command=load_history,
                        bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'),
                        padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.pack(side=tk.LEFT)
    
    result_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    text_area = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=('Segoe UI', 11),
                                         state=tk.DISABLED)
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    create_footer(show_panel)

def confirm_generate_dummy_data():
    if messagebox.askyesno('Confirmar', 'Generar datos dummy de prueba? Esto puede tardar varios minutos.'):
        messagebox.showinfo('Generando', 'Iniciando la creacion de datos dummy. Por favor espera.')
        success, message = generate_dummy_data()
        if success:
            messagebox.showinfo('Datos dummy generados', message)
        else:
            messagebox.showerror('Error', message)
        show_dba_panel()

def confirm_delete_dummy_data():
    if messagebox.askyesno('Confirmar', 'Eliminar toda la informacion dummy generada en la base de datos?'):
        success, message = delete_dummy_data()
        if success:
            messagebox.showinfo('Eliminado', message)
        else:
            messagebox.showerror('Error', message)
        show_dba_panel()

def logout():
    registrar_log(current_user, 'LOGOUT', 'EXITO')
    show_login_screen()

def main():
    global root
    root = tk.Tk()
    root.title('Hospital Blanes - Sistema de Gestion')
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f'{screen_width}x{screen_height}+0+0')
    root.state('zoomed')
    configure_styles()
    root.configure(bg=BG_COLOR)
    show_login_screen()
    root.mainloop()

if __name__ == '__main__':
    main()
