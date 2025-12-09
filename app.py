import streamlit as st
import pandas as pd
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="LMS MiniPreu", page_icon="🎓", layout="wide")

# --- ESTILOS CSS (Para que no se vea feo) ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #4F46E5; text-align: center; margin-bottom: 1rem;}
    .sub-header {font-size: 1.5rem; color: #333; margin-top: 1rem;}
    .card {background-color: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 5px solid #4F46E5; margin-bottom: 10px;}
    .success-card {background-color: #e6fffa; padding: 15px; border-radius: 10px; border: 1px solid #38b2ac;}
    .stButton>button {width: 100%; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# --- SIMULACIÓN DE BASE DE DATOS (En el futuro esto será Google Sheets) ---
if 'preguntas_db' not in st.session_state:
    st.session_state['preguntas_db'] = [
        {"id": 1, "texto": "¿Qué implica la palabra 'despertó' en el texto?", "opciones": ["Acción física", "Conciencia", "Sueño", "Miedo"], "correcta": "Conciencia"},
        {"id": 2, "texto": "Identifique la idea principal del párrafo 2.", "opciones": ["El clima", "La política", "La economía", "La salud"], "correcta": "La política"}
    ]

if 'resultados_db' not in st.session_state:
    st.session_state['resultados_db'] = [
        {"Alumno": "Juan Pérez", "Puntaje": 850, "Habilidad": "Interpretar"},
        {"Alumno": "Maria Silva", "Puntaje": 620, "Habilidad": "Localizar"}
    ]

# --- GESTIÓN DE SESIÓN (LOGIN) ---
if 'usuario_actual' not in st.session_state:
    st.session_state['usuario_actual'] = None
if 'rol_actual' not in st.session_state:
    st.session_state['rol_actual'] = None

def login(usuario, password):
    # Simulación de credenciales
    if usuario == "profe" and password == "admin123":
        st.session_state['usuario_actual'] = "Profesor Alejandro"
        st.session_state['rol_actual'] = "Tutor"
        st.rerun()
    elif usuario == "alumno" and password == "1234":
        st.session_state['usuario_actual'] = "Estudiante Demo"
        st.session_state['rol_actual'] = "Estudiante"
        st.rerun()
    else:
        st.error("Usuario o contraseña incorrectos")

def logout():
    st.session_state['usuario_actual'] = None
    st.session_state['rol_actual'] = None
    st.rerun()

# ==========================================
# VISTA: LOGIN
# ==========================================
if st.session_state['usuario_actual'] is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 class='main-header'>🔐 LMS MiniPreu</h1>", unsafe_allow_html=True)
        st.info("Prueba ingresando con:\n\n👤 **Profe**: usuario `profe` | clave `admin123`\n\n🎓 **Alumno**: usuario `alumno` | clave `1234`")
        
        with st.form("login_form"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar")
            
            if submit:
                login(user, pwd)

# ==========================================
# VISTA: PANEL DEL TUTOR (ADMIN)
# ==========================================
elif st.session_state['rol_actual'] == "Tutor":
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/teacher.png", width=80)
        st.write(f"Hola, **{st.session_state['usuario_actual']}**")
        if st.button("Cerrar Sesión"): logout()
    
    st.markdown("<h1 class='main-header'>Panel de Control Docente 🛠️</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Crear Preguntas", "📊 Progreso Alumnos", "📂 Subir Material"])
    
    with tab1:
        st.markdown("<div class='card'>Agrega nuevas preguntas al ensayo semanal.</div>", unsafe_allow_html=True)
        with st.form("nueva_pregunta"):
            texto = st.text_area("Enunciado de la pregunta:")
            op1 = st.text_input("Opción A")
            op2 = st.text_input("Opción B")
            op3 = st.text_input("Opción C")
            correcta = st.selectbox("¿Cuál es la correcta?", ["A", "B", "C"])
            
            if st.form_submit_button("Guardar Pregunta"):
                # Aquí guardamos en la "base de datos" simulada
                nueva = {"id": len(st.session_state['preguntas_db'])+1, "texto": texto, "opciones": [op1, op2, op3], "correcta": correcta}
                st.session_state['preguntas_db'].append(nueva)
                st.success("¡Pregunta guardada exitosamente!")

    with tab2:
        st.subheader("Resultados Recientes")
        df = pd.DataFrame(st.session_state['resultados_db'])
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Alumno")["Puntaje"])
        
    with tab3:
        st.warning("Funcionalidad en construcción: Aquí subirás PDFs a Google Drive.")

# ==========================================
# VISTA: PANEL DEL ESTUDIANTE
# ==========================================
elif st.session_state['rol_actual'] == "Estudiante":
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/student-male.png", width=80)
        st.write(f"Bienvenido, **{st.session_state['usuario_actual']}**")
        st.metric("Tu último puntaje", "720 pts", "+30")
        if st.button("Cerrar Sesión"): logout()

    st.markdown("<h1 class='main-header'>Tu Espacio de Estudio 🚀</h1>", unsafe_allow_html=True)
    
    modo = st.radio("¿Qué quieres hacer hoy?", ["Hacer Ensayo", "Ver mis Estadísticas"], horizontal=True)
    
    if modo == "Hacer Ensayo":
        st.markdown("<div class='card'>Responde las siguientes preguntas cargadas por tu profesor.</div>", unsafe_allow_html=True)
        
        # Aquí cargamos las preguntas que EL PROFE creó en la otra pestaña
        for p in st.session_state['preguntas_db']:
            st.write(f"**Pregunta {p['id']}:** {p['texto']}")
            st.radio(f"Selecciona:", p['opciones'], key=f"p_{p['id']}")
            st.markdown("---")
        
        if st.button("Enviar Ensayo"):
            st.balloons()
            st.success("¡Ensayo enviado! Tu profesor recibirá los resultados.")
            
    elif modo == "Ver mis Estadísticas":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Habilidades Lectoras")
            chart_data = pd.DataFrame({'Habilidad': ['Localizar', 'Interpretar', 'Evaluar'], 'Logro': [80, 50, 90]})
            st.bar_chart(chart_data.set_index('Habilidad'))
        with col2:
            st.info("💡 **Consejo:** Debes reforzar 'Interpretar'. Revisa la guía #4.")
