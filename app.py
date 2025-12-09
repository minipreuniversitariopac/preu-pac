import streamlit as st

st.title("¡Hola Mundo! 🌍")
st.header("Mi primera plataforma de Preu está naciendo")
st.write("Si estás leyendo esto, significa que configuré todo exitosamente.")

if st.button("¡Presióname para celebrar!"):
    st.balloons()
    st.success("¡Funciona! Eres oficialmente un programador de Streamlit.")
