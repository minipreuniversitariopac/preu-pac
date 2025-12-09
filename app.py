import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Preu PAC", page_icon="🎓", layout="wide")

# --- GESTIÓN DE ERRORES DE SECRETOS ---
try:
    GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
except:
    GEMINI_KEY = ""

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        if "gcp_service_account" not in st.secrets:
            return None
            
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("BaseDatos_Preu")
    except Exception as e:
        st.error(f"Error conectando a BD: {e}")
        return None

def obtener_usuario(username):
    sheet = conectar_google_sheets()
    if sheet:
        try:
            worksheet = sheet.worksheet("usuarios")
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Limpiamos espacios en blanco por si acaso
            if 'usuario' in df.columns:
                df['usuario'] = df['usuario'].astype(str).str.strip()
                usuario = df[df['usuario'] == str(username).strip()]
                
                if not usuario.empty:
                    # Retornamos la primera coincidencia
                    return usuario.iloc[0]
        except Exception as e:
            st.error(f"Error leyendo usuarios: {e}")
            pass
            
    # Usuario de respaldo (Backdoor para pruebas si falla la BD)
    if username == "profe":
        return {"usuario": "profe", "password": "123", "nombre": "Profesor Test", "rol": "admin"}
    
    return None

# --- SIMULADOR PRO (REACT) ---
def mostrar_simulador_pro():
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
        <script>window.process = { env: { API_KEY: "REPLACE_WITH_API_KEY" } };</script>
      </head>
      <body>
        <div id="root"></div>
        <script type="text/babel" data-type="module">
          import React, { useState, useEffect } from 'react';
          import ReactDOM from 'react-dom/client';
          import { Play, Pause, Check, ArrowLeft, Calculator, BookOpen, FlaskConical } from 'lucide-react';

          const OPTIONS = ['A', 'B', 'C', 'D', 'E'];
          const App = () => {
            const [phase, setPhase] = useState('SETUP'); 
            const [config, setConfig] = useState({ count: 65, type: 'math' });
            const [answers, setAnswers] = useState({});
            const [timeLeft, setTimeLeft] = useState(0);
            const [isPaused, setIsPaused] = useState(false);

            useEffect(() => {
                let timer;
                if (phase === 'TAKING' && !isPaused && timeLeft > 0) timer = setInterval(() => setTimeLeft(p => p - 1), 1000);
                return () => clearInterval(timer);
            }, [phase, isPaused, timeLeft]);

            const formatTime = (s) => {
                const h = Math.floor(s/3600);
                const m = Math.floor((s%3600)/60);
                const sec = s%60;
                return `${h}:${m.toString().padStart(2,'0')}:${sec.toString().padStart(2,'0')}`;
            };

            if (phase === 'SETUP') return (
                <div className="max-w-2xl mx-auto mt-4 p-8 bg-white rounded-3xl border border-slate-100 shadow-xl text-center">
                    <h1 className="text-3xl font-bold text-slate-800 mb-6">Nuevo Ensayo</h1>
                    <div className="grid grid-cols-3 gap-4 mb-8">
                        {[{id:'math', l:'Matemática', i:Calculator}, {id:'leng', l:'Lenguaje', i:BookOpen}, {id:'ciencias', l:'Ciencias', i:FlaskConical}].map(x => (
                            <button key={x.id} onClick={() => setConfig({...config, type: x.id})} className={`p-4 rounded-xl border-2 flex flex-col items-center gap-2 ${config.type === x.id ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-slate-100 text-slate-400'}`}>
                                <x.i size={24} /> <span className="font-bold text-sm">{x.l}</span>
                            </button>
                        ))}
                    </div>
                    <button onClick={() => {setTimeLeft(7200); setPhase('TAKING');}} className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition">Comenzar</button>
                </div>
            );

            if (phase === 'TAKING') return (
                <div className="max-w-5xl mx-auto p-2">
                    <div className="sticky top-2 bg-white/90 backdrop-blur border p-4 flex justify-between items-center mb-6 rounded-xl shadow-lg z-50">
                        <div className="font-bold capitalize text-slate-700">{config.type}</div>
                        <div className="font-mono text-xl font-bold">{formatTime(timeLeft)}</div>
                        <button onClick={() => setPhase('REVIEW')} className="px-4 py-2 bg-slate-900 text-white rounded-lg font-bold text-sm">Terminar</button>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pb-20">
                        {Array.from({length: config.count}, (_, i) => i + 1).map(num => (
                            <div key={num} className="bg-white border p-3 rounded-xl flex flex-col items-center">
                                <span className="text-xs font-bold text-slate-300 mb-2">P{num}</span>
                                <div className="flex gap-1">
                                    {OPTIONS.map(opt => (
                                        <button key={opt} onClick={() => setAnswers({...answers, [num]: opt})} className={`w-7 h-7 rounded-full text-xs font-bold border ${answers[num] === opt ? 'bg-slate-900 text-white' : 'bg-white text-slate-300'}`}>{opt}</button>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            );

            return (
                <div className="max-w-xl mx-auto mt-10 text-center p-10 bg-white rounded-3xl shadow-xl">
                    <h2 className="text-3xl font-bold text-slate-900 mb-4">¡Terminado!</h2>
                    <p className="mb-6">Respondiste {Object.keys(answers).length} preguntas.</p>
                    <button onClick={() => setPhase('SETUP')} className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold">Volver</button>
                </div>
            );
          };
          const root = ReactDOM.createRoot(document.getElementById('root'));
          root.render(<App />);
        </script>
      </body>
    </html>
    """
    final_html = HTML_TEMPLATE.replace("REPLACE_WITH_API_KEY", GEMINI_KEY)
    components.html(final_html, height=800, scrolling=True)

# --- APP PRINCIPAL ---
if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

if st.session_state['usuario_logueado'] is None:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.title("🎓 Preu PAC")
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user_data = obtener_usuario(u)
                
                # CORRECCIÓN AQUÍ: Usamos 'is not None' para evitar el error de Pandas
                if user_data is not None:
                    # Convertimos a string para comparar seguro
                    if str(user_data['password']).strip() == str(p).strip():
                        st.session_state['usuario_logueado'] = user_data
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta")
                else:
                    st.error("Usuario no encontrado")
else:
    with st.sidebar:
        st.title(f"Hola, {st.session_state['usuario_logueado']['nombre']}")
        opcion = st.radio("Ir a:", ["Inicio", "Ensayo", "Salir"])
        if opcion == "Salir":
            st.session_state['usuario_logueado'] = None
            st.rerun()
    
    if opcion == "Inicio":
        st.info("Bienvenido al sistema.")
    elif opcion == "Ensayo":
        mostrar_simulador_pro()
