import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Preu PAC", page_icon="🎓", layout="wide")

# --- 1. CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("BaseDatos_Preu")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def obtener_usuario(username):
    sheet = conectar_google_sheets()
    if sheet:
        try:
            worksheet = sheet.worksheet("usuarios")
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            usuario = df[df['usuario'] == username]
            if not usuario.empty:
                return usuario.iloc[0]
        except:
            pass
    return None

# --- 2. EL SIMULADOR PRO (REACT + HTML) ---
def mostrar_simulador_pro():
    # Intentamos obtener API Key para IA, si no hay, no pasa nada
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
    except:
        gemini_key = ""

    # Este es el código de tu Google Lab, adaptado para recibir la API Key
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
            /* Ajustes para que se vea bien dentro del iframe de Streamlit */
            #root { padding-bottom: 50px; }
        </style>
        <script type="importmap">
        {
          "imports": {
            "react": "https://esm.sh/react@18.2.0",
            "react-dom/client": "https://esm.sh/react-dom@18.2.0/client",
            "@google/genai": "https://esm.sh/@google/genai@0.1.1",
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
          import { Play, Pause, Check, XCircle, Clock, Save } from 'lucide-react';
          import { GoogleGenAI } from '@google/genai';

          // --- CONFIGURACIÓN BÁSICA ---
          const OPTIONS = ['A', 'B', 'C', 'D', 'E'];
          const EXAM_DURATIONS = { 'math': 140*60, 'leng': 150*60, 'ciencias': 160*60 };

          const App = () => {
            const [phase, setPhase] = useState('SETUP'); // SETUP, TAKING, REVIEW
            const [config, setConfig] = useState({ name: 'Ensayo', count: 65, type: 'math' });
            const [answers, setAnswers] = useState({});
            const [timeLeft, setTimeLeft] = useState(0);
            const [isPaused, setIsPaused] = useState(false);

            // Timer
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

            const finishExam = () => {
                setPhase('REVIEW');
                // Aquí podríamos enviar los datos de vuelta a Python en el futuro
            };

            // --- PANTALLA 1: CONFIGURACIÓN ---
            if (phase === 'SETUP') return (
                <div className="max-w-xl mx-auto mt-10 p-8 bg-white rounded-2xl border border-slate-200 shadow-lg text-center">
                    <h1 className="text-3xl font-bold text-slate-800 mb-2">Nuevo Ensayo</h1>
                    <p className="text-slate-500 mb-8">Configura tu simulación</p>
                    
                    <div className="grid grid-cols-3 gap-4 mb-6">
                        {['math', 'leng', 'ciencias'].map(type => (
                            <button 
                                key={type}
                                onClick={() => setConfig({...config, type})}
                                className={`p-4 rounded-xl border-2 font-bold capitalize transition-all ${config.type === type ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-slate-100 text-slate-400 hover:border-slate-300'}`}
                            >
                                {type === 'math' ? 'Matemática' : type === 'leng' ? 'Lenguaje' : 'Ciencias'}
                            </button>
                        ))}
                    </div>
                    
                    <div className="mb-8">
                        <label className="block text-sm font-bold text-slate-700 mb-2">Cantidad de Preguntas</label>
                        <input 
                            type="number" 
                            value={config.count} 
                            onChange={(e) => setConfig({...config, count: parseInt(e.target.value)})}
                            className="w-full p-3 border border-slate-300 rounded-lg text-center font-bold text-lg"
                        />
                    </div>

                    <button onClick={startExam} className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition shadow-lg flex items-center justify-center gap-2">
                        <Play size={20} /> Comenzar
                    </button>
                </div>
            );

            // --- PANTALLA 2: TOMANDO EL ENSAYO ---
            if (phase === 'TAKING') return (
                <div className="max-w-5xl mx-auto p-4">
                    <div className="sticky top-0 bg-white/90 backdrop-blur border-b border-slate-200 p-4 flex justify-between items-center mb-6 z-10 rounded-xl shadow-sm">
                        <div>
                            <h2 className="font-bold text-slate-800 capitalize">{config.type}</h2>
                            <span className="text-xs text-slate-500">{Object.keys(answers).length}/{config.count} Respondidas</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="font-mono text-xl font-bold text-slate-700">{formatTime(timeLeft)}</span>
                            <button onClick={() => setIsPaused(!isPaused)} className="p-2 bg-slate-100 rounded-full hover:bg-slate-200">
                                {isPaused ? <Play size={20}/> : <Pause size={20}/>}
                            </button>
                            <button onClick={finishExam} className="px-4 py-2 bg-red-600 text-white rounded-lg font-bold text-sm hover:bg-red-700">Terminar</button>
                        </div>
                    </div>

                    {isPaused ? (
                        <div className="text-center py-20 text-slate-400">
                            <Pause size={64} className="mx-auto mb-4 opacity-20"/>
                            <h2 className="text-2xl font-bold">Pausado</h2>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
                            {Array.from({length: config.count}, (_, i) => i + 1).map(num => (
                                <div key={num} className="bg-white border border-slate-100 p-3 rounded-lg flex flex-col items-center shadow-sm hover:shadow-md transition">
                                    <span className="text-xs font-bold text-slate-400 mb-2">Pregunta {num}</span>
                                    <div className="flex gap-1 justify-center w-full">
                                        {OPTIONS.map(opt => (
                                            <button
                                                key={opt}
                                                onClick={() => setAnswers({...answers, [num]: opt})}
                                                className={`w-8 h-8 rounded-full text-sm font-bold border flex items-center justify-center transition-all ${
                                                    answers[num] === opt 
                                                    ? 'bg-slate-900 text-white border-slate-900 scale-110' 
                                                    : 'bg-white text-slate-400 border-slate-200 hover:border-slate-400'
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

            // --- PANTALLA 3: REVISIÓN (PLACEHOLDER) ---
            return (
                <div className="max-w-2xl mx-auto mt-10 text-center p-10 bg-white rounded-3xl shadow-xl">
                    <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Check size={40} strokeWidth={3} />
                    </div>
                    <h2 className="text-3xl font-bold text-slate-900 mb-2">¡Ensayo Terminado!</h2>
                    <p className="text-slate-500 mb-6">Has respondido {Object.keys(answers).length} preguntas.</p>
                    <div className="p-4 bg-yellow-50 text-yellow-800 rounded-xl text-sm mb-6">
                        ⚠️ <b>Nota:</b> En esta versión integrada, los resultados aún no se guardan en tu base de datos automáticamente. Toma una captura si necesitas guardar tus respuestas.
                    </div>
                    <button onClick={() => setPhase('SETUP')} className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold">Volver al Inicio</button>
                </div>
            );
          };

          const root = ReactDOM.createRoot(document.getElementById('root'));
          root.render(<App />);
        </script>
      </body>
    </html>
    """
    final_html = HTML_TEMPLATE.replace("REPLACE_WITH_API_KEY", gemini_key)
    components.html(final_html, height=800, scrolling=True)

# --- 3. INTERFAZ PRINCIPAL DE STREAMLIT ---

# --- LOGIN ---
if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

if st.session_state['usuario_logueado'] is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🎓 Preu PAC")
        st.subheader("Inicia sesión para comenzar")
        with st.form("login_form"):
            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                datos_usuario = obtener_usuario(user)
                if datos_usuario is not None and str(datos_usuario['password']) == str(password):
                    st.session_state['usuario_logueado'] = datos_usuario
                    st.success("¡Bienvenido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

else:
    # --- USUARIO LOGUEADO ---
    usuario = st.session_state['usuario_logueado']
    
    # BARRA LATERAL (MENÚ)
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
        st.write(f"Hola, **{usuario['nombre']}** 👋")
        st.write(f"_{usuario['rol']}_")
        st.divider()
        
        menu = st.radio("Navegación", ["🏠 Inicio", "📝 Realizar Ensayo", "📊 Mis Resultados", "🚪 Cerrar Sesión"])
        
        if menu == "🚪 Cerrar Sesión":
            st.session_state['usuario_logueado'] = None
            st.rerun()

    # CONTENIDO SEGÚN MENÚ
    if menu == "🏠 Inicio":
        st.title(f"Bienvenido al Preuniversitario, {usuario['nombre']}")
        st.info("📢 **Noticia del día:** Recuerda que el ensayo nacional es este sábado.")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Días para la PAES", value="120")
        with col2:
            st.metric(label="Ensayos Realizados", value="3")

    elif menu == "📝 Realizar Ensayo":
        st.header("Simulador de Hoja de Respuestas")
        st.caption("Usa esta herramienta para simular el tiempo y formato real de la prueba.")
        # AQUÍ LLAMAMOS A TU APP DE GOOGLE LAB
        mostrar_simulador_pro()

    elif menu == "📊 Mis Resultados":
        st.header("Tu Progreso")
        st.write("Aquí verás tus puntajes históricos (Próximamente conectado a la base de datos).")
        # Ejemplo de gráfico simple
        datos_fake = pd.DataFrame({'Ensayo': ['E1', 'E2', 'E3'], 'Puntaje': [550, 610, 680]})
        st.line_chart(datos_fake.set_index('Ensayo'))
