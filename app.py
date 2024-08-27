import streamlit as st
import requests
import json

# Configuración de las API
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

def get_ai_recommendations(user_input):
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": f"Basado en la siguiente información: {user_input}, recomienda 3 colegios en la ciudad de Guatemala que se ajusten a estos criterios. Proporciona una breve descripción de cada colegio y por qué lo recomiendas.",
        "max_tokens": 500,
        "temperature": 0.7,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['output']['choices'][0]['text']

def search_schools(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "gl": "gt"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

st.title("Buscador de Colegios en Guatemala")

st.write("Por favor, responde las siguientes preguntas para ayudarte a encontrar el colegio ideal para tu hijo/a en la ciudad de Guatemala.")

sexo = st.selectbox("Sexo del estudiante:", ["Masculino", "Femenino"])
edad = st.number_input("Edad del estudiante:", min_value=3, max_value=18, value=6)
presupuesto = st.slider("Presupuesto anual (en Quetzales):", 5000, 100000, 25000, step=1000)
ubicacion = st.text_input("Ubicación preferida en la ciudad de Guatemala:")
bilingue = st.checkbox("¿Buscas un colegio bilingüe?")

if st.button("Buscar Colegios"):
    user_input = f"Sexo: {sexo}, Edad: {edad}, Presupuesto anual: Q{presupuesto}, Ubicación: {ubicacion}, Bilingüe: {'Sí' if bilingue else 'No'}"
    
    with st.spinner("Buscando recomendaciones..."):
        ai_recommendations = get_ai_recommendations(user_input)
        st.subheader("Recomendaciones de la IA:")
        st.write(ai_recommendations)
    
    with st.spinner("Buscando información adicional..."):
        search_query = f"Mejores colegios en {ubicacion}, Guatemala para estudiantes de {edad} años"
        search_results = search_schools(search_query)
        
        st.subheader("Resultados de búsqueda adicionales:")
        for result in search_results.get('organic', [])[:3]:
            st.write(f"**{result['title']}**")
            st.write(result['snippet'])
            st.write(f"[Más información]({result['link']})")
            st.write("---")

st.write("Nota: Esta aplicación proporciona recomendaciones basadas en la información proporcionada. Te recomendamos investigar más a fondo y contactar directamente a los colegios para obtener información más precisa y actualizada.")
