import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import streamlit.components.v1 as components
import json

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Preu PAC", page_icon="🎓", layout="wide")

# --- GESTIÓN DE SECRETOS Y ERRORES ---
# Esto evita que la app muera si faltan secretos, usando valores por defecto
try:
    GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
except:
    GEMINI_KEY = ""

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    """Conecta a la base de datos de Google Sheets de forma segura."""
    try:
        # Verifica si existe el secreto
        if "gcp_service_account" not in st.secrets:
            st.warning("⚠️ Falta configurar el secreto 'gcp_service_account' en Streamlit.")
            return None
            
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Arreglo común: a veces las private_key vienen con \\n en vez de \n reales
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("BaseDatos_Preu") # Asegúrate que tu Excel se llame así
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")
        return None

def obtener_usuario(username):
    sheet = conectar_google_sheets()
    if sheet:
        try:
            worksheet = sheet.worksheet("usuarios")
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            # Filtramos el usuario
            if 'usuario' in df.columns:
                usuario = df[df['usuario'] == username]
                if not usuario.empty:
                    return usuario.iloc[0]
            else:
                st.error("La hoja 'usuarios' no tiene una columna llamada 'usuario'.")
        except gspread.exceptions.WorksheetNotFound:
            st.error("No se encontró la pestaña 'usuarios' en el Excel.")
        except Exception as e:
            st.error(f"Error al leer usuarios: {e}")
    return None

# --- COMPONENTE: SIMULADOR PRO (REACT) ---
def mostrar_simulador_pro():
    """Renderiza la aplicación React completa dentro de Streamlit"""
    
    # Código HTML/JS/React incrustado
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="es">
      <head>
        <meta charset="UTF-8" />
        <title>Simulador</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #ffffff; }
            #root { padding-bottom: 50px; }
            /* Animaciones suaves */
            .btn-anim { transition: all 0.2s; }
            .btn-anim:active { transform: scale(0.95); }
        </style>
        <script type="importmap">
        {
          "imports": {
            "react": "https://esm.sh/react@18.2.0",
            "react-dom/client": "https://esm.sh/react-dom@18.2.0/client",
            "lucide-react": "https://esm.sh/lucide-react@0.263.1"
          }
        }
        </script>
        <script>
          window.process = { env: { API_KEY: "REPLACE_WITH_API_KEY" } };
        </script>
      </head>
      <body>
        <div id="root"></div>
        <script type="text/babel" data-type="module">
          import React, { useState, useEffect } from 'react';
          import ReactDOM from 'react-dom/client';
          import { Play, Pause, Check, XCircle, Clock, Save, ArrowLeft, BookOpen, Calculator, FlaskConical } from 'lucide-react';

          const OPTIONS = ['A', 'B', 'C', 'D', 'E'];
          // Tiempos en segundos (2h 20m, etc)
          const EXAM_DURATIONS = { 'math': 8400, 'leng': 9000, 'ciencias': 9600 };

          const App = () => {
            const [phase, setPhase] = useState('SETUP'); 
            const [config, setConfig] = useState({ name: 'Ensayo', count: 65, type: 'math' });
            const [answers, setAnswers] = useState({});
            const [timeLeft, setTimeLeft] = useState(0);
            const [isPaused, setIsPaused] = useState(false);

            useEffect(() => {
                let timer;
                if (phase === 'TAKING' && !isPaused && timeLeft > 0) {
                    timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
                }
                return () => clearInterval(timer);
            }, [phase, isPaused, timeLeft]);

            const formatTime = (s) => {
                const h = Math.floor(s/3600);
                const m = Math.floor((s%3600)/60);
                const sec = s%60;
                return `${h}:${m.toString().padStart(2,'0')}:${sec.toString().padStart(2,'0')}`;
            };

            const startExam = () => {
                setTimeLeft(EXAM_DURATIONS[config.type] || 7200);
                setPhase('TAKING');
            };

            // --- VISTAS ---
            
            // 1. CONFIGURACIÓN
            if (phase === 'SETUP') return (
                <div className="max-w-2xl mx-auto mt-4 p-8 bg-white rounded-3xl border border-slate-100 shadow-xl text-center">
                    <h1 className="text-4xl font-black text-slate-800 mb-2 tracking-tight">Nuevo Ensayo</h1>
                    <p className="text-slate-500 mb-10">Selecciona la materia y configura tu simulación.</p>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                        {[
                            {id: 'math', label: 'Matemática', icon: Calculator, color: 'blue'},
                            {id: 'leng', label: 'Lenguaje', icon: BookOpen, color: 'red'},
                            {id: 'ciencias', label: 'Ciencias', icon: FlaskConical, color: 'green'}
                        ].map(item => {
                            const Icon = item.icon;
                            const isSelected = config.type === item.id;
                            return (
                                <button 
                                    key={item.id}
                                    onClick={() => setConfig({...config, type: item.id})}
                                    className={`p-6 rounded-2xl border-2 flex flex-col items-center gap-3 transition-all duration-300 ${isSelected ? `border-${item.color}-500 bg-${item.color}-50 text-${item.color}-700 shadow-md scale-105` : 'border-slate-100 text-slate-400 hover:border-slate-200 hover:bg-slate-50'}`}
                                >
                                    <Icon size={32} />
                                    <span className="font-bold">{item.label}</span>
                                </button>
                            )
                        })}
                    </div>
                    
                    <div className="mb-8 max-w-xs mx-auto">
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Cantidad de Preguntas</label>
                        <input 
                            type="number" 
                            value={config.count} 
                            onChange={(e) => setConfig({...config, count: parseInt(e.target.value)})}
                            className="w-full p-4 border border-slate-200 rounded-xl text-center font-bold text-2xl outline-none focus:ring-2 focus:ring-slate-900 transition"
                        />
                    </div>

                    <button onClick={startExam} className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition shadow-lg hover:shadow-xl flex items-center justify-center gap-3 btn-anim">
                        <Play size={24} fill="currentColor" /> Comenzar Simulación
                    </button>
                </div>
            );

            // 2. REALIZANDO ENSAYO
            if (phase === 'TAKING') return (
                <div className="max-w-6xl mx-auto p-2">
                    {/* Header Flotante */}
                    <div className="sticky top-2 bg-white/90 backdrop-blur-md border border-slate-200 p-4 flex justify-between items-center mb-8 z-50 rounded-2xl shadow-lg">
                        <div className="flex items-center gap-4">
                            <div className={`p-3 rounded-xl ${config.type === 'math' ? 'bg-blue-100 text-blue-700' : config.type === 'leng' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                                {config.type === 'math' ? <Calculator size={24}/> : config.type === 'leng' ? <BookOpen size={24}/> : <FlaskConical size={24}/>}
                            </div>
                            <div>
                                <h2 className="font-bold text-slate-800 capitalize leading-tight">{config.type}</h2>
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{Object.keys(answers).length} / {config.count} Respondidas</span>
                            </div>
                        </div>
                        
                        <div className="flex items-center gap-3 sm:gap-6">
                            <div className={`font-mono text-2xl font-bold tabular-nums ${timeLeft < 300 ? 'text-red-500 animate-pulse' : 'text-slate-700'}`}>
                                {formatTime(timeLeft)}
                            </div>
                            <div className="h-8 w-px bg-slate-200"></div>
                            <button onClick={() => setIsPaused(!isPaused)} className="p-3 bg-slate-100 rounded-full hover:bg-slate-200 transition text-slate-600">
                                {isPaused ? <Play size={24} fill="currentColor"/> : <Pause size={24} fill="currentColor"/>}
                            </button>
                            <button onClick={() => setPhase('REVIEW')} className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold text-sm hover:bg-slate-800 transition shadow-md">
                                Terminar
                            </button>
                        </div>
                    </div>

                    {isPaused ? (
                        <div className="flex flex-col items-center justify-center py-32 text-slate-300 animate-in fade-in duration-500">
                            <Pause size={80} className="mb-6 opacity-20"/>
                            <h2 className="text-3xl font-bold text-slate-400">Ensayo Pausado</h2>
                            <p>Tómate un respiro.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 pb-20">
                            {Array.from({length: config.count}, (_, i) => i + 1).map(num => (
                                <div key={num} className="bg-white border border-slate-100 p-4 rounded-2xl flex flex-col items-center shadow-sm hover:shadow-md transition-all duration-200 group">
                                    <span className="text-xs font-bold text-slate-300 mb-3 group-hover:text-slate-500 transition-colors">Pregunta {num}</span>
                                    <div className="flex gap-1.5 justify-center w-full">
                                        {OPTIONS.map(opt => (
                                            <button
                                                key={opt}
                                                onClick={() => setAnswers({...answers, [num]: opt})}
                                                className={`w-9 h-9 rounded-full text-sm font-bold border flex items-center justify-center transition-all duration-200 ${
                                                    answers[num] === opt 
                                                    ? 'bg-slate-900 text-white border-slate-900 scale-110 shadow-lg' 
                                                    : 'bg-white text-slate-400 border-slate-200 hover:border-slate-400 hover:scale-105'
                                                }`}
                                            >
                                                {opt}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            );

            // 3. FINALIZADO
            return (
                <div className="max-w-xl mx-auto mt-10 text-center p-12 bg-white rounded-[2rem] shadow-2xl border border-slate-100">
                    <div className="w-24 h-24 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-8 shadow-inner">
                        <Check size={48} strokeWidth={4} />
                    </div>
                    <h2 className="text-4xl font-black text-slate-900 mb-4">¡Ensayo Terminado!</h2>
                    <p className="text-slate-500 text-lg mb-8">Has respondido <strong className="text-slate-900">{Object.keys(answers).length}</strong> preguntas.</p>
                    
                    <div className="p-6 bg-blue-50 text-blue-900 rounded-2xl text-sm mb-8 text-left border border-blue-100">
                        <h4 className="font-bold flex items-center gap-2 mb-2"><Save size={16}/> Guardado de Datos</h4>
                        <p>Tus respuestas están listas. En la próxima actualización, estos datos se enviarán automáticamente a tu base de datos para generar estadísticas.</p>
                    </div>

                    <button onClick={() => setPhase('SETUP')} className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition flex items-center justify-center gap-2">
                        <ArrowLeft size={20}/> Volver al Inicio
                    </button>
                </div>
            );
          };

          const root = ReactDOM.createRoot(document.getElementById('root'));
          root.render(<App />);
        </script>
      </body>
    </html>
    """
    # Inyectar API KEY si existe
    final_html = HTML_TEMPLATE.replace("REPLACE_WITH_API_KEY", GEMINI_KEY)
    components.html(final_html, height=900, scrolling=True)

# --- LÓGICA PRINCIPAL DE LA APP ---

if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

# --- PANTALLA DE LOGIN ---
if st.session_state['usuario_logueado'] is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🎓 Acceso Preu PAC")
        st.markdown("Ingresa tus credenciales para acceder al sistema.")
        
        with st.form("login_form"):
            user = st.text_input("Usuario", placeholder="Ej: profe")
            password = st.text_input("Contraseña", type="password", placeholder="••••••")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                if not user or not password:
                    st.warning("Por favor completa todos los campos.")
                else:
                    with st.spinner("Verificando credenciales..."):
                        datos = obtener_usuario(user)
                        if datos is not None:
                            # Convertimos a string para asegurar comparación
                            if str(datos['password']) == str(password):
                                st.session_state['usuario_logueado'] = datos
                                st.success("¡Acceso correcto!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Contraseña incorrecta.")
                        else:
                            st.error("Usuario no encontrado.")

# --- PANTALLA PRINCIPAL (DASHBOARD) ---
else:
    usuario = st.session_state['usuario_logueado']
    
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <div style="width: 80px; height: 80px; background-color: #f1f5f9; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 30px;">
                👤
            </div>
            <h3 style="margin-top: 10px; margin-bottom: 0;">{usuario['nombre']}</h3>
            <p style="color: #64748b; font-size: 0.9em;">{usuario['rol']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        menu = st.radio("Menú Principal", 
            ["🏠 Inicio", "📝 Realizar Ensayo", "📊 Mis Resultados", "⚙️ Configuración"],
            captions=["Resumen general", "Simulador oficial", "Estadísticas", "Ajustes de cuenta"]
        )
        
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['usuario_logueado'] = None
            st.rerun()

    # --- CONTENIDO DE LAS PÁGINAS ---
    
    if menu == "🏠 Inicio":
        st.title(f"Hola, {usuario['nombre']} 👋")
        st.markdown("Bienvenido al panel de control del **Preuniversitario PAC**.")
        
        # Métricas rápidas
        col1, col2, col3 = st.columns(3)
        col1.metric("Ensayos Realizados", "12", "+2 esta semana")
        col2.metric("Promedio Matemáticas", "650", "+15 pts")
        col3.metric("Días para la PAES", "120", "¡Ánimo!")
        
        st.info("📢 **Aviso:** Se ha cargado un nuevo ensayo de Ciencias para este fin de semana.")

    elif menu == "📝 Realizar Ensayo":
        # Aquí cargamos el componente React
        mostrar_simulador_pro()

    elif menu == "📊 Mis Resultados":
        st.header("📊 Tus Estadísticas")
        st.write("Visualiza tu progreso en el tiempo.")
        
        # Datos de ejemplo (Fake)
        chart_data = pd.DataFrame({
            'Ensayo': ['Marzo', 'Abril', 'Mayo', 'Junio'],
            'Matemáticas': [500, 550, 610, 640],
            'Lenguaje': [600, 610, 590, 620]
        })
        st.line_chart(chart_data.set_index('Ensayo'))
        
    elif menu == "⚙️ Configuración":
        st.header("Configuración de Cuenta")
        st.text_input("Correo Electrónico", value="alumno@ejemplo.com", disabled=True)
        st.button("Cambiar Contraseña")

