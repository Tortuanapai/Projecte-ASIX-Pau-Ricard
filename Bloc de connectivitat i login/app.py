import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from funciones import get_db_connection, registrar_log, validate_dni, validate_password, verify_credentials, get_pending_users, approve_user, reject_user, get_logs, direct_register_user, add_patient, get_infermer_dependency, get_quirofan_schedule, get_visit_schedule, get_quirofan_equipment, get_habitacio_reserves, get_patient_history
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

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR)
    style.configure('TButton', font=('Segoe UI', 10))
    style.configure('TEntry', font=('Segoe UI', 10))
    style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'))
    style.map('Primary.TButton', background=[('active', SECONDARY_COLOR)])
    style.configure('Header.TLabel', font=('Segoe UI', 28, 'bold'), foreground='white')
    style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground=HEADER_COLOR)
    style.configure('Subtitle.TLabel', font=('Segoe UI', 14), foreground=TEXT_COLOR)

def create_welcome_frame(parent, title, rol=None):
    welcome_frame = tk.Frame(parent, bg='white', relief=tk.FLAT, bd=1)
    welcome_frame.pack(fill=tk.X, padx=30, pady=20)
    title_label = tk.Label(welcome_frame, text=title, font=('Segoe UI', 18, 'bold'), bg='white', fg=DANGER_COLOR if 'Panel' in title else HEADER_COLOR)
    title_label.pack(anchor=tk.W, padx=20, pady=10)
    if rol:
        rol_label = tk.Label(welcome_frame, text=f'🔖 Rol: {rol}', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
        rol_label.pack(anchor=tk.W, padx=20, pady=(0, 10))
    return welcome_frame

def create_button(parent, text, command, bg, **kwargs):
    defaults = {'fg': 'white', 'font': ('Segoe UI', 12, 'bold'), 'padx': 20, 'pady': 15, 'relief': tk.FLAT, 'cursor': 'hand2', 'width': 50}
    defaults.update(kwargs)
    btn = tk.Button(parent, text=text, command=command, bg=bg, **defaults)
    btn.pack(fill=tk.X, pady=10)
    return btn

def create_logout_footer(parent):
    footer_frame = tk.Frame(parent, bg=BG_COLOR)
    footer_frame.pack(fill=tk.X, padx=30, pady=20)
    btn_logout = tk.Button(footer_frame, text='🚪 Cerrar Sesión', command=logout, bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
    btn_logout.pack(fill=tk.X)
    return footer_frame

def create_screen_footer(parent, back_action, show_logout=True):
    footer_frame = tk.Frame(parent, bg=BG_COLOR)
    footer_frame.pack(fill=tk.X, padx=30, pady=20)
    back_btn = tk.Button(footer_frame, text='← Volver', command=back_action, bg='#6c757d', fg='white', font=('Segoe UI', 11, 'bold'), padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
    back_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    if show_logout:
        logout_btn = tk.Button(footer_frame, text='🚪 Cerrar Sesión', command=logout, bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
        logout_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    return footer_frame

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def create_header_frame():
    header = tk.Frame(root, bg=HEADER_COLOR, height=100)
    header.pack(fill=tk.X, side=tk.TOP)
    title_label = tk.Label(header, text='🏥 Hospital Blanes', font=('Segoe UI', 32, 'bold'), bg=HEADER_COLOR, fg='white')
    title_label.pack(pady=20)
    return header

def show_login_screen():
    global current_user, current_rol
    current_user = None
    current_rol = None
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    center_frame = tk.Frame(main_frame, bg=BG_COLOR)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    title = tk.Label(center_frame, text='Acceso con DNI', font=('Segoe UI', 24, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=(0, 30))
    input_frame = tk.Frame(center_frame, bg='white', relief=tk.FLAT, bd=2)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    user_label = tk.Label(input_frame, text='🆔 DNI:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    user_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    login_user_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    login_user_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    pass_label = tk.Label(input_frame, text='🔐 Contraseña:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    pass_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    login_pass_entry = ttk.Entry(input_frame, show='•', width=40, font=('Segoe UI', 11))
    login_pass_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    login_pass_entry.bind('<Return>', lambda e: login(login_user_entry.get(), login_pass_entry.get()))
    btn_frame = tk.Frame(center_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    login_btn = tk.Button(btn_frame, text='🔓 Iniciar Sesión', command=lambda: login(login_user_entry.get(), login_pass_entry.get()), bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    login_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    register_btn = tk.Button(btn_frame, text='📝 Registrarse', command=show_register_screen, bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    register_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

def show_panel():
    if current_rol == 'Administratiu':
        show_administratiu_panel()
    elif current_rol == 'dba':
        show_dba_panel()
    else:
        show_user_panel()

def login(dni, password):
    global current_user, current_rol
    dni = dni.strip()
    if not dni or not password:
        messagebox.showerror('Error', 'DNI y contraseña requeridos')
        return
    is_admin = dni.lower() == 'admin'
    if not is_admin:
        dni = dni.upper()
        if not validate_dni(dni):
            messagebox.showerror('Error', 'DNI no válido. Formato: 8 cifras y letra mayúscula.')
            return
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT password_hash, nom_rol FROM usuaris_registrats WHERE usuario = %s', (dni,))
            result = cur.fetchone()
            if result and verify_credentials(result[0], password):
                current_user = dni
                current_rol = result[1]
                registrar_log(dni, 'LOGIN', 'ÉXITO')
                show_panel()
            else:
                registrar_log(dni, 'LOGIN', 'FALLO')
                messagebox.showerror('❌ Error', 'DNI o contraseña incorrectos')
    except Exception as e:
        messagebox.showerror('❌ Error', f'Error en conexión: {str(e)}')
        registrar_log(dni, 'LOGIN', f'ERROR: {str(e)}')

def show_register_screen():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    center_frame = tk.Frame(main_frame, bg=BG_COLOR)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    title = tk.Label(center_frame, text='Registro de Nuevo DNI', font=('Segoe UI', 24, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=(0, 30))
    input_frame = tk.Frame(center_frame, bg='white', relief=tk.FLAT, bd=2)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    user_label = tk.Label(input_frame, text='🆔 DNI:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    user_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    user_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    user_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    pass_label = tk.Label(input_frame, text='🔐 Contraseña (mín. 8 caracteres):', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    pass_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    pass_entry = ttk.Entry(input_frame, show='•', width=40, font=('Segoe UI', 11))
    pass_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    rol_label = tk.Label(input_frame, text='👨\u200d⚕️ Rol:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    rol_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    rol_var = tk.StringVar(value='Infermer')
    roles = ['Medic', 'Infermer', 'Administratiu', 'dba']
    rol_combo = ttk.Combobox(input_frame, textvariable=rol_var, values=roles, state='readonly', width=37, font=('Segoe UI', 11))
    rol_combo.pack(padx=15, pady=(0, 15), fill=tk.X)

    def registrar():
        dni = user_entry.get().strip().upper()
        password = pass_entry.get()
        rol = rol_var.get()
        if not dni or not password:
            messagebox.showerror('Error', 'DNI y contraseña requeridos')
            return
        if not validate_dni(dni):
            messagebox.showerror('Error', 'DNI no válido. Formato: 8 cifras y letra mayúscula.')
            return
        if not validate_password(password):
            messagebox.showerror('Error', 'La contraseña debe tener mínimo 8 caracteres')
            return
        try:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO usuaris_pendents (usuario, password_hash, nom_rol) VALUES (%s, %s, %s)', (dni, password_hash, rol))
                conn.commit()
            messagebox.showinfo('✅ Éxito', 'DNI registrado. Espera la aprobación del administrador.')
            registrar_log(dni, 'REGISTRO', 'ÉXITO')
            show_login_screen()
        except Exception as e:
            messagebox.showerror('❌ Error', f'Error en registro: {str(e)}')
            registrar_log(dni, 'REGISTRO', f'ERROR: {str(e)}')
    btn_frame = tk.Frame(center_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    register_btn = tk.Button(btn_frame, text='✓ Registrarse', command=registrar, bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    register_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    back_btn = tk.Button(btn_frame, text='← Volver', command=show_login_screen, bg='#6c757d', fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    back_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

def show_direct_register():
    if current_rol != 'dba':
        messagebox.showerror('❌ Error', 'Solo DBA puede acceder a esta función')
        return
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    center_frame = tk.Frame(main_frame, bg=BG_COLOR)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    title = tk.Label(center_frame, text='👤 Alta Directa de Usuario (DBA)', font=('Segoe UI', 24, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=(0, 30))
    input_frame = tk.Frame(center_frame, bg='white', relief=tk.FLAT, bd=2)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    user_label = tk.Label(input_frame, text='🆔 DNI:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    user_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    user_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    user_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    pass_label = tk.Label(input_frame, text='🔐 Contraseña (mín. 8 caracteres):', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    pass_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    pass_entry = ttk.Entry(input_frame, show='•', width=40, font=('Segoe UI', 11))
    pass_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    rol_label = tk.Label(input_frame, text='👨\u200d⚕️ Rol:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    rol_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    rol_var = tk.StringVar(value='Infermer')
    roles = ['Medic', 'Infermer', 'Administratiu', 'dba']
    rol_combo = ttk.Combobox(input_frame, textvariable=rol_var, values=roles, state='readonly', width=37, font=('Segoe UI', 11))
    rol_combo.pack(padx=15, pady=(0, 15), fill=tk.X)

    def registrar_directo():
        dni = user_entry.get().strip().upper()
        password = pass_entry.get()
        rol = rol_var.get()
        success, message = direct_register_user(dni, password, rol)
        if success:
            messagebox.showinfo('✅ Éxito', message)
            registrar_log(current_user, 'REGISTRO_DIRECTO', f'DNI {dni} rol {rol}')
            user_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            rol_var.set('Infermer')
        else:
            messagebox.showerror('❌ Error', message)
    btn_frame = tk.Frame(center_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    register_btn = tk.Button(btn_frame, text='✓ Registrar Usuario', command=registrar_directo, bg='#17a2b8', fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    register_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    back_btn = tk.Button(btn_frame, text='← Volver', command=show_panel, bg='#6c757d', fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    back_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

def show_add_patient():
    if current_rol != 'Administratiu':
        messagebox.showerror('❌ Error', 'Solo los administrativos pueden añadir pacientes')
        return
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    center_frame = tk.Frame(main_frame, bg=BG_COLOR)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
    title = tk.Label(center_frame, text='🏥 Alta de Nuevo Paciente', font=('Segoe UI', 24, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(pady=(0, 30))
    input_frame = tk.Frame(center_frame, bg='white', relief=tk.FLAT, bd=2)
    input_frame.pack(fill=tk.X, pady=20, padx=20)
    nom_label = tk.Label(input_frame, text='👤 Nombre:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    nom_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
    nom_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    nom_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    nss_label = tk.Label(input_frame, text='🆔 NSS (15 caracteres):', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    nss_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    nss_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    nss_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    adreça_label = tk.Label(input_frame, text='🏠 Dirección:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    adreça_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    adreça_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 11))
    adreça_entry.pack(padx=15, pady=(0, 15), fill=tk.X)
    descripcio_label = tk.Label(input_frame, text='📝 Descripción:', font=('Segoe UI', 12), bg='white', fg=TEXT_COLOR)
    descripcio_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
    descripcio_text = scrolledtext.ScrolledText(input_frame, height=4, font=('Segoe UI', 11))
    descripcio_text.pack(padx=15, pady=(0, 15), fill=tk.X)

    def añadir_paciente():
        nom = nom_entry.get().strip()
        nss = nss_entry.get().strip()
        adreça = adreça_entry.get().strip()
        descripcio = descripcio_text.get('1.0', tk.END).strip()
        success, message = add_patient(nom, nss, adreça, descripcio)
        if success:
            messagebox.showinfo('✅ Éxito', message)
            registrar_log(current_user, 'ALTA_PACIENTE', f'Paciente {nom} (NSS: {nss})')
            nom_entry.delete(0, tk.END)
            nss_entry.delete(0, tk.END)
            adreça_entry.delete(0, tk.END)
            descripcio_text.delete('1.0', tk.END)
        else:
            messagebox.showerror('❌ Error', message)
    btn_frame = tk.Frame(center_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30, fill=tk.X)
    add_btn = tk.Button(btn_frame, text='✓ Añadir Paciente', command=añadir_paciente, bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    add_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    back_btn = tk.Button(btn_frame, text='← Volver', command=show_panel, bg='#6c757d', fg='white', font=('Segoe UI', 12, 'bold'), padx=30, pady=12, relief=tk.FLAT, cursor='hand2')
    back_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

def show_administratiu_panel():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    create_welcome_frame(main_frame, f'👨\u200d💼 Panel Administratiu - {current_user}')
    options_frame = tk.Frame(main_frame, bg=BG_COLOR)
    options_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    options_title = tk.Label(options_frame, text='Gestión Administrativa', font=('Segoe UI', 16, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    options_title.pack(pady=(0, 20))
    create_button(options_frame, '🏥 Dar de Alta Paciente', show_add_patient, SUCCESS_COLOR)
    create_button(options_frame, '🛏️ Ver Reserves Habitacions', show_habitacio_reserves, SECONDARY_COLOR)
    create_button(options_frame, '📊 Història Pacient', show_patient_history, SECONDARY_COLOR)
    create_button(options_frame, '📦 Equipament Quiròfan', show_quirofan_equipment, SECONDARY_COLOR)
    create_logout_footer(main_frame)

def show_user_panel():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    create_welcome_frame(main_frame, f'👋 Bienvenido, {current_user}', current_rol)
    options_frame = tk.Frame(main_frame, bg=BG_COLOR)
    options_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    options_title = tk.Label(options_frame, text='Opciones Disponibles', font=('Segoe UI', 16, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    options_title.pack(pady=(0, 20))
    create_button(options_frame, '👤 Ver Mi Perfil', show_profile, SECONDARY_COLOR, width=40)
    if current_rol == 'Metge':
        create_button(options_frame, '📅 Veure Meva Agenda', show_doctor_schedule, SECONDARY_COLOR)
    create_logout_footer(main_frame)

def show_admin_panel():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    create_welcome_frame(main_frame, f'👨\u200d💼 Panel Administratiu - {current_user}')
    options_frame = tk.Frame(main_frame, bg=BG_COLOR)
    options_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    options_title = tk.Label(options_frame, text='Gestión Administrativa', font=('Segoe UI', 16, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    options_title.pack(pady=(0, 20))
    create_button(options_frame, '⏳ Usuarios Pendientes de Aprobación', show_pending_users, DANGER_COLOR)
    create_button(options_frame, '📋 Ver Logs de Sistema', show_logs, PRIMARY_COLOR)
    create_button(options_frame, '📊 Història Pacient', show_patient_history, SECONDARY_COLOR)
    create_button(options_frame, '🏥 Dar de Alta Paciente', show_add_patient, SUCCESS_COLOR)
    create_logout_footer(main_frame)

def show_dba_panel():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    create_welcome_frame(main_frame, f'🛠️ Panel DBA - {current_user}')
    options_frame = tk.Frame(main_frame, bg=BG_COLOR)
    options_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    options_title = tk.Label(options_frame, text='Gestión de Base de Datos', font=('Segoe UI', 16, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    options_title.pack(pady=(0, 20))
    create_button(options_frame, '👤 Alta Directa de Usuario (DBA)', show_direct_register, '#17a2b8')
    create_button(options_frame, '📋 Ver Logs de Sistema', show_logs, PRIMARY_COLOR)
    create_button(options_frame, '📅 Agenda Quiròfanos', show_operating_schedule, SECONDARY_COLOR)
    create_button(options_frame, '📋 Agenda Visites', show_visit_schedule, SECONDARY_COLOR)
    create_button(options_frame, '📊 Història Pacient', show_patient_history, SECONDARY_COLOR)
    create_button(options_frame, '📦 Equipament Quiròfan', show_quirofan_equipment, SECONDARY_COLOR)
    create_button(options_frame, '🏥 Dar de Alta Paciente', show_add_patient, SUCCESS_COLOR)
    create_logout_footer(main_frame)

def show_pending_users():
    global pending_tree
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='⏳ Usuarios Pendientes de Aprobación', font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    try:
        users = get_pending_users()
        if not users:
            empty_label = tk.Label(main_frame, text='✓ No hay usuarios pendientes', font=('Segoe UI', 14), bg=BG_COLOR, fg=SUCCESS_COLOR)
            empty_label.pack(pady=40)
        else:
            table_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
            pending_tree = ttk.Treeview(table_frame, columns=('ID', 'DNI', 'Rol'), height=15, show='tree headings')
            pending_tree.column('#0', width=0, stretch=tk.NO)
            pending_tree.column('ID', anchor=tk.W, width=60)
            pending_tree.column('DNI', anchor=tk.W, width=300)
            pending_tree.column('Rol', anchor=tk.W, width=300)
            pending_tree.heading('#0', text='')
            pending_tree.heading('ID', text='ID')
            pending_tree.heading('DNI', text='🆔 DNI')
            pending_tree.heading('Rol', text='🔖 Rol')
            for user in users:
                pending_tree.insert('', 'end', values=(user[0], user[1], user[2]))
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=pending_tree.yview)
            pending_tree.configure(yscroll=scrollbar.set)
            pending_tree.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')
            table_frame.grid_rowconfigure(0, weight=1)
            table_frame.grid_columnconfigure(0, weight=1)
            action_frame = tk.Frame(main_frame, bg=BG_COLOR)
            action_frame.pack(pady=20, padx=30, fill=tk.X)
            approve_btn = tk.Button(action_frame, text='✓ Aprobar DNI', command=approve_pending_user, bg=SUCCESS_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
            approve_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            reject_btn = tk.Button(action_frame, text='✗ Rechazar DNI', command=reject_pending_user, bg=DANGER_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=20, pady=10, relief=tk.FLAT, cursor='hand2')
            reject_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    except Exception as e:
        messagebox.showerror('❌ Error', f'Error al cargar usuarios: {str(e)}')
    create_screen_footer(main_frame, show_panel, show_logout=False)

def approve_pending_user():
    if pending_tree is None:
        return
    selection = pending_tree.selection()
    if not selection:
        messagebox.showwarning('⚠️ Advertencia', 'Selecciona un DNI')
        return
    user_id = pending_tree.item(selection[0])['values'][0]
    try:
        success, dni = approve_user(user_id)
        if success:
            messagebox.showinfo('✅ Éxito', f"DNI '{dni}' aprobado correctamente")
            registrar_log(current_user, 'APROBAR_USUARIO', f'DNI {dni} aprobado')
            show_pending_users()
        else:
            messagebox.showerror('❌ Error', 'No se pudo aprobar el DNI')
    except Exception as e:
        messagebox.showerror('❌ Error', f'Error: {str(e)}')

def reject_pending_user():
    if pending_tree is None:
        return
    selection = pending_tree.selection()
    if not selection:
        messagebox.showwarning('⚠️ Advertencia', 'Selecciona un DNI')
        return
    user_id = pending_tree.item(selection[0])['values'][0]
    dni_value = pending_tree.item(selection[0])['values'][1]
    if messagebox.askyesno('Confirmar', f"¿Rechazar al DNI '{dni_value}'?"):
        try:
            success, dni = reject_user(user_id)
            if success:
                messagebox.showinfo('✅ Éxito', f"DNI '{dni}' rechazado")
                registrar_log(current_user, 'RECHAZAR_USUARIO', f'DNI {dni} rechazado')
                show_pending_users()
            else:
                messagebox.showerror('❌ Error', 'No se pudo rechazar el DNI')
        except Exception as e:
            messagebox.showerror('❌ Error', f'Error: {str(e)}')

def show_logs():
    if current_rol not in ['Administratiu', 'dba']:
        messagebox.showerror('❌ Error', 'Solo el administrador puede ver los logs')
        return
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='📋 Logs de Acceso al Sistema', font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    try:
        logs = get_logs()
        text_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        text_widget = scrolledtext.ScrolledText(text_frame, height=20, font=('Consolas', 9), bg='#f8f9fa', fg=TEXT_COLOR, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.config(state=tk.NORMAL)
        for log in logs:
            text_widget.insert(tk.END, log)
        text_widget.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror('❌ Error', f'Error al cargar logs: {str(e)}')
    create_screen_footer(main_frame, show_panel)

def show_profile():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    profile_card = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    profile_card.pack(fill=tk.X, padx=100, pady=60)
    title = tk.Label(profile_card, text='👤 Mi Perfil', font=('Segoe UI', 22, 'bold'), bg='white', fg=HEADER_COLOR)
    title.pack(pady=30)
    info_frame = tk.Frame(profile_card, bg='#f8f9fa')
    info_frame.pack(fill=tk.X, padx=30, pady=20)
    user_info = tk.Label(info_frame, text=f'🆔 DNI: {current_user}', font=('Segoe UI', 14), bg='#f8f9fa', fg=TEXT_COLOR, justify=tk.LEFT)
    user_info.pack(anchor=tk.W, pady=15)
    rol_info = tk.Label(info_frame, text=f'🔖 Rol: {current_rol.capitalize()}', font=('Segoe UI', 14), bg='#f8f9fa', fg=TEXT_COLOR, justify=tk.LEFT)
    rol_info.pack(anchor=tk.W, pady=15)
    if current_rol == 'Infermer':
        infermer_info = get_infermer_dependency(current_user)
        infermer_text = infermer_info or "No hi ha informació d'assignació"
        dependency_info = tk.Label(info_frame, text=f'🏥 Infermeria: {infermer_text}', font=('Segoe UI', 14), bg='#f8f9fa', fg=TEXT_COLOR, justify=tk.LEFT, wraplength=600)
        dependency_info.pack(anchor=tk.W, pady=15)
    btn_frame = tk.Frame(profile_card, bg='white')
    btn_frame.pack(fill=tk.X, padx=30, pady=30)
    create_screen_footer(profile_card, show_panel)

def show_operating_schedule():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='📅 Agenda de Quiròfanos', font=('Segoe UI', 22, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, padx=30, pady=10)
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    date_label = tk.Label(search_frame, text='Data (YYYY-MM-DD):', font=('Segoe UI', 12), bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def load_schedule():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha inválido. Usa YYYY-MM-DD.')
            return
        for item in schedule_tree.get_children():
            schedule_tree.delete(item)
        rows = get_quirofan_schedule(selected_date)
        if not rows:
            messagebox.showinfo('Info', 'No hay operaciones programadas para esta fecha.')
            return
        for row in rows:
            schedule_tree.insert('', tk.END, values=(row[0], row[1].strftime('%H:%M') if hasattr(row[1], 'strftime') else row[1], row[2], row[3], row[4], row[5]))
    load_btn = tk.Button(search_frame, text='🔎 Cargar Agenda', command=load_schedule, bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    result_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    columns = ('Quirofan', 'Hora', 'Pacient', 'NSS', 'Metge', 'Infermers')
    schedule_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    for col in columns:
        schedule_tree.heading(col, text=col)
        schedule_tree.column(col, anchor=tk.W, width=150)
    schedule_tree.column('Pacient', width=220)
    schedule_tree.column('Infermers', width=260)
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=schedule_tree.yview)
    schedule_tree.configure(yscroll=vsb.set)
    schedule_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    create_screen_footer(main_frame, show_panel)

def show_quirofan_equipment():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='📦 Equipament de Quiròfan', font=('Segoe UI', 22, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    result_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    columns = ('Quiròfan', 'Planta', 'Aparell', 'Quantitat')
    equipment_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    for col in columns:
        equipment_tree.heading(col, text=col)
        equipment_tree.column(col, anchor=tk.W, width=180)
    equipment_tree.column('Aparell', width=260)
    equipment_tree.grid(row=0, column=0, sticky='nsew')
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=equipment_tree.yview)
    equipment_tree.configure(yscroll=vsb.set)
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    rows = get_quirofan_equipment()
    if not rows:
        messagebox.showinfo('Info', 'No hi ha equips assignats als quiròfans.')
    else:
        for row in rows:
            equipment_tree.insert('', tk.END, values=(row[0], row[1] or '-', row[2], row[3]))
    create_screen_footer(main_frame, show_panel)

def show_habitacio_reserves():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='🛏️ Reserves Habitacions', font=('Segoe UI', 22, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, padx=30, pady=10)
    room_var = tk.StringVar()
    room_label = tk.Label(search_frame, text='ID Habitació:', font=('Segoe UI', 12), bg=BG_COLOR, fg=TEXT_COLOR)
    room_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    room_entry = ttk.Entry(search_frame, textvariable=room_var, width=20, font=('Segoe UI', 11))
    room_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def load_reserves():
        room_id = room_var.get().strip()
        if not room_id:
            messagebox.showerror('Error', "Introdueix l'ID de la habitació")
            return
        try:
            room_id = int(room_id)
        except ValueError:
            messagebox.showerror('Error', 'El ID ha de ser un número')
            return
        for item in reserves_tree.get_children():
            reserves_tree.delete(item)
        rows = get_habitacio_reserves(room_id)
        if not rows:
            messagebox.showinfo('Info', 'No hay reserves para aquesta habitació')
            return
        for row in rows:
            reserves_tree.insert('', tk.END, values=(row[0], row[1] if row[1] else 'Sense data', row[2]))
        registrar_log(current_user, 'VER_RESERVES_HABITACIO', f'ID Habitació: {room_id}')
    load_btn = tk.Button(search_frame, text='🔎 Cargar Reserves', command=load_reserves, bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    result_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    columns = ('Data Ingres', 'Data Sortida', 'Pacient')
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
    create_screen_footer(main_frame, show_panel)

def show_visit_schedule():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='📅 Agenda de Visites', font=('Segoe UI', 22, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, padx=30, pady=10)
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    date_label = tk.Label(search_frame, text='Data (YYYY-MM-DD):', font=('Segoe UI', 12), bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def load_visits():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha inválido. Usa YYYY-MM-DD.')
            return
        for item in visits_tree.get_children():
            visits_tree.delete(item)
        rows = get_visit_schedule(selected_date)
        if not rows:
            messagebox.showinfo('Info', 'No hay visitas programadas para esta fecha.')
            return
        for row in rows:
            visits_tree.insert('', tk.END, values=(row[0].strftime('%H:%M') if hasattr(row[0], 'strftime') else row[0], row[1], row[2], row[3]))
    load_btn = tk.Button(search_frame, text='🔎 Cargar Visites', command=load_visits, bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    result_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    columns = ('Hora', 'Metge', 'Pacient', 'NSS')
    visits_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=18)
    for col in columns:
        visits_tree.heading(col, text=col)
        visits_tree.column(col, anchor=tk.W, width=180)
    visits_tree.column('Pacient', width=220)
    visits_tree.column('Metge', width=220)
    vsb = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=visits_tree.yview)
    visits_tree.configure(yscroll=vsb.set)
    visits_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    result_frame.grid_rowconfigure(0, weight=1)
    result_frame.grid_columnconfigure(0, weight=1)
    create_screen_footer(main_frame, show_panel)

def show_doctor_schedule():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='📅 Agenda de Metge', font=('Segoe UI', 22, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, padx=30, pady=10)
    date_var = tk.StringVar(value=datetime.today().date().isoformat())
    date_label = tk.Label(search_frame, text='Data (YYYY-MM-DD):', font=('Segoe UI', 12), bg=BG_COLOR, fg=TEXT_COLOR)
    date_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    date_entry = ttk.Entry(search_frame, textvariable=date_var, width=20, font=('Segoe UI', 11))
    date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def load_schedule():
        date_text = date_var.get().strip()
        try:
            selected_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Error', 'Formato de fecha inválido. Usa YYYY-MM-DD.')
            return
        for item in schedule_tree.get_children():
            schedule_tree.delete(item)
        for item in available_tree.get_children():
            available_tree.delete(item)
        schedule = get_doctor_schedule(current_user, selected_date)
        if schedule is None:
            messagebox.showerror('Error', "No s'ha pogut obtenir l'agenda del metge.")
            return
        if not schedule['visits'] and (not schedule['operations']):
            messagebox.showinfo('Info', 'No tens visites ni operacions programades per aquesta data.')
        for visit in schedule['visits']:
            schedule_tree.insert('', tk.END, values=('Visita', visit[0].strftime('%H:%M') if hasattr(visit[0], 'strftime') else visit[0], visit[1], visit[2], '-'))
        for op in schedule['operations']:
            schedule_tree.insert('', tk.END, values=('Operació', op[0].strftime('%H:%M') if hasattr(op[0], 'strftime') else op[0], op[1], op[2], op[3]))
        if schedule['available_hours']:
            for hour in schedule['available_hours']:
                available_tree.insert('', tk.END, values=(hour,))
        else:
            available_tree.insert('', tk.END, values=('Sense hores disponibles (08:00-17:00)',))
        registrar_log(current_user, 'VER_AGENDA_METGE', f'Data={selected_date}')
    load_btn = tk.Button(search_frame, text='🔎 Carregar Agenda', command=load_schedule, bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    result_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    columns = ('Tipus', 'Hora', 'Pacient', 'NSS', 'Quiròfan')
    schedule_tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=12)
    for col in columns:
        schedule_tree.heading(col, text=col)
        schedule_tree.column(col, anchor=tk.W, width=140)
    schedule_tree.column('Pacient', width=220)
    schedule_tree.column('Quiròfan', width=140)
    schedule_tree.grid(row=0, column=0, sticky='nsew', padx=(0, 0), pady=(0, 10))
    available_label = tk.Label(result_frame, text='Hores disponibles (08:00-17:00):', font=('Segoe UI', 12, 'bold'), bg='white', fg=TEXT_COLOR)
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
    create_screen_footer(main_frame, show_panel)

def show_patient_history():
    clear_window()
    create_header_frame()
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True)
    title_frame = tk.Frame(main_frame, bg=BG_COLOR)
    title_frame.pack(fill=tk.X, padx=30, pady=20)
    title = tk.Label(title_frame, text='📊 Història de Pacient', font=('Segoe UI', 22, 'bold'), bg=BG_COLOR, fg=HEADER_COLOR)
    title.pack(anchor=tk.W)
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, padx=30, pady=10)
    nss_var = tk.StringVar()
    nss_label = tk.Label(search_frame, text='NSS del Pacient:', font=('Segoe UI', 12), bg=BG_COLOR, fg=TEXT_COLOR)
    nss_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    nss_entry = ttk.Entry(search_frame, textvariable=nss_var, width=30, font=('Segoe UI', 11))
    nss_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def load_history():
        nss = nss_var.get().strip()
        if not nss:
            messagebox.showerror('Error', 'Introdueix el NSS del pacient')
            return
        if len(nss) != 15:
            messagebox.showerror('Error', 'El NSS ha de tenir 15 caràcters')
            return
        history = get_patient_history(nss)
        if not history:
            messagebox.showinfo('Info', "No s'ha trobat cap pacient amb aquest NSS")
            return
        text_area.config(state=tk.NORMAL)
        text_area.delete('1.0', tk.END)
        text_area.insert(tk.END, f"Pacient: {history['nom']}\n")
        text_area.insert(tk.END, f"NSS: {history['nss']}\n")
        text_area.insert(tk.END, f"Visites totals: {len(history['visits'])}\n")
        text_area.insert(tk.END, f"Ingressos totals: {history['admissions_count']}\n")
        text_area.insert(tk.END, f"Operacions totals: {history['operation_count']}\n\n")
        text_area.insert(tk.END, 'Diagnòstics:\n')
        if history['diagnostics']:
            for diag in history['diagnostics']:
                text_area.insert(tk.END, f' - {diag[0]}\n')
        else:
            text_area.insert(tk.END, ' - Sense diagnòstic registrat\n')
        text_area.insert(tk.END, '\n')
        text_area.insert(tk.END, 'Medicaments prescrits:\n')
        if history['medications']:
            for med in history['medications']:
                dosis = med[2] or 'Sense dosis'
                pauta = med[3] or 'Sense pauta'
                text_area.insert(tk.END, f' - {med[0]} ({med[1]}) | Dosi: {dosis} | Pauta: {pauta} | Data visita: {med[4]}\n')
        else:
            text_area.insert(tk.END, ' - Sense medicaments registrats\n')
        text_area.insert(tk.END, '\n')
        text_area.insert(tk.END, 'Detall de visites:\n')
        if history['visits']:
            for visita in history['visits']:
                hora = visita[1].strftime('%H:%M') if hasattr(visita[1], 'strftime') else visita[1]
                observacions = visita[2] if visita[2] else 'Sense observacions'
                text_area.insert(tk.END, f' - {visita[0]} {hora} | Metge: {visita[3]} | Observacions: {observacions}\n')
        else:
            text_area.insert(tk.END, ' - Sense visites registrades\n')
        text_area.config(state=tk.DISABLED)
        registrar_log(current_user, 'VER_HISTORIA_PACIENT', f'NSS={nss}')
    load_btn = tk.Button(search_frame, text='🔎 Buscar', command=load_history, bg=PRIMARY_COLOR, fg='white', font=('Segoe UI', 11, 'bold'), padx=15, pady=10, relief=tk.FLAT, cursor='hand2')
    load_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    result_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
    text_area = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=('Segoe UI', 11), state=tk.DISABLED)
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    create_screen_footer(main_frame, show_panel)

def logout():
    registrar_log(current_user, 'LOGOUT', 'ÉXITO')
    show_login_screen()

def main():
    global root
    root = tk.Tk()
    root.title('🏥 Hospital Blanes - Sistema de Gestión')
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