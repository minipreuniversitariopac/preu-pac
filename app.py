import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Preu PAC", page_icon="🎓", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS (LA MAGIA) ---
def conectar_google_sheets():
    try:
        # Accedemos a la llave secreta que guardaste en Streamlit
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abrimos tu hoja de cálculo
        sheet = client.open("BaseDatos_Preu") # ¡OJO! Este nombre debe ser exacto al de tu Drive
        return sheet
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

# --- FUNCIONES DE BASE DE DATOS ---
def obtener_usuario(username):
    sheet = conectar_google_sheets()
    if sheet:
        worksheet = sheet.worksheet("usuarios")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        # Buscamos el usuario
        usuario = df[df['usuario'] == username]
        if not usuario.empty:
            return usuario.iloc[0]
    return None

def guardar_pregunta_nueva(texto, op_a, op_b, op_c, correcta):
    sheet = conectar_google_sheets()
    if sheet:
        worksheet = sheet.worksheet("preguntas")
        # Generamos un ID simple basado en el tiempo
        nuevo_id = int(time.time())
        worksheet.append_row([nuevo_id, texto, op_a, op_b, op_c, correcta])
        return True
    return False

def leer_preguntas():
    sheet = conectar_google_sheets()
    if sheet:
        worksheet = sheet.worksheet("preguntas")
        data = worksheet.get_all_records()
        return data
    return []

# --- INTERFAZ GRÁFICA ---

# 1. SISTEMA DE LOGIN
if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

if st.session_state['usuario_logueado'] is None:
    st.title("🎓 Acceso al Preuniversitario")
    
    with st.form("login_form"):
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            datos_usuario = obtener_usuario(user)
            if datos_usuario is not None and str(datos_usuario['password']) == str(password):
                st.session_state['usuario_logueado'] = datos_usuario
                st.success(f"¡Bienvenido {datos_usuario['nombre']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

else:
    # 2. PANEL PRINCIPAL (YA LOGUEADO)
    usuario = st.session_state['usuario_logueado']
    
    # Barra lateral con menú y botón de salir
    with st.sidebar:
        st.write(f"Hola, **{usuario['nombre']}**")
        st.write(f"Rol: {usuario['rol']}")
        if st.button("Cerrar Sesión"):
            st.session_state['usuario_logueado'] = None
            st.rerun()
    
    # VISTA DE PROFESOR
    if usuario['rol'] == 'Tutor':
        st.title("Panel de Profesor 🍎")
        pestana = st.tabs(["Crear Pregunta", "Ver Preguntas Actuales"])
        
        with pestana[0]:
            st.write("Agrega una nueva pregunta a la base de datos.")
            with st.form("nueva_pregunta"):
                txt = st.text_input("Pregunta")
                a = st.text_input("Opción A")
                b = st.text_input("Opción B")
                c = st.text_input("Opción C")
                corr = st.selectbox("Correcta", ["A", "B", "C"])
                
                if st.form_submit_button("Guardar en Base de Datos"):
                    if guardar_pregunta_nueva(txt, a, b, c, corr):
                        st.success("¡Pregunta guardada en Google Sheets!")
                    else:
                        st.error("Hubo un error al guardar.")
        
        with pestana[1]:
            st.write("Estas son las preguntas que están en tu Excel:")
            preguntas = leer_preguntas()
            if preguntas:
                st.dataframe(preguntas)
            else:
                st.info("No hay preguntas cargadas aún.")

    # VISTA DE ALUMNO
    elif usuario['rol'] == 'Estudiante':
        st.title("Zona de Ensayos 📝")
        st.write("Aquí aparecerán tus pruebas.")
        
        preguntas = leer_preguntas()
        if preguntas:
            for p in preguntas:
                st.markdown(f"**{p['texto']}**")
                opcion = st.radio(f"Selecciona:", [p['op_a'], p['op_b'], p['op_c']], key=p['id'])
                st.write("---")
            
            if st.button("Enviar Respuestas"):
                st.balloons()
                st.success("Respuestas enviadas (simulación)")
        else:
            st.info("El profesor aún no ha subido preguntas. ¡Vuelve más tarde!")
