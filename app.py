import streamlit as st
import requests
import json

# Configuración de las API
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

# Lista de municipios del departamento de Guatemala
MUNICIPIOS = [
    "Guatemala", "Santa Catarina Pinula", "San José Pinula", "San José del Golfo", 
    "Palencia", "Chinautla", "San Pedro Ayampuc", "Mixco", "San Pedro Sacatepéquez", 
    "San Juan Sacatepéquez", "San Raymundo", "Chuarrancho", "Fraijanes", "Amatitlán", 
    "Villa Nueva", "Villa Canales", "San Miguel Petapa"
]

def get_ai_recommendations(user_input):
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": f"Basado en la siguiente información: {user_input}, recomienda 3 colegios en el departamento de Guatemala que se ajusten a estos criterios. Presta especial atención a la ubicación preferida y proporciona opciones cercanas o en esa área. Para cada colegio, proporciona una breve descripción, su ubicación específica dentro del departamento, su orientación religiosa (si aplica), y por qué lo recomiendas.",
        "max_tokens": 800,
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

st.title("Buscador de Colegios en el Departamento de Guatemala")

st.write("Por favor, responde las siguientes preguntas para ayudarte a encontrar el colegio ideal para tu hijo/a en el departamento de Guatemala.")

sexo = st.selectbox("Sexo del estudiante:", ["Masculino", "Femenino"])
edad = st.number_input("Edad del estudiante:", min_value=3, max_value=18, value=6)
presupuesto = st.slider("Presupuesto anual (en Quetzales):", 5000, 100000, 25000, step=1000)

# Mejora en la selección de ubicación
ubicacion_tipo = st.radio("Tipo de ubicación:", ["Municipio específico", "Área general"])
if ubicacion_tipo == "Municipio específico":
    ubicacion = st.selectbox("Selecciona el municipio:", MUNICIPIOS)
else:
    ubicacion = st.text_input("Describe el área general (ej. 'zona 10', 'cerca de Carretera a El Salvador', etc.):")

# Opción para especificar múltiples ubicaciones
otras_ubicaciones = st.multiselect("Otras ubicaciones de interés (opcional):", MUNICIPIOS)

distancia_maxima = st.slider("Distancia máxima aceptable (en km):", 0, 50, 10)

bilingue = st.checkbox("¿Buscas un colegio bilingüe?")
transporte = st.checkbox("¿Necesitas servicio de transporte escolar?")
religion = st.selectbox("Orientación religiosa preferida:", [
    "No es un factor importante",
    "Laico (sin orientación religiosa)",
    "Católico",
    "Evangélico",
    "Otro cristiano",
    "Judío",
    "Otro"
])
if religion == "Otro":
    otra_religion = st.text_input("Especifica la orientación religiosa:")
actividades_extra = st.multiselect("Actividades extracurriculares de interés:", 
                                   ["Deportes", "Arte", "Música", "Tecnología", "Idiomas adicionales", "Otro"])

if st.button("Buscar Colegios"):
    ubicaciones = ", ".join([ubicacion] + otras_ubicaciones) if otras_ubicaciones else ubicacion
    user_input = f"""
    Sexo: {sexo}
    Edad: {edad}
    Presupuesto anual: Q{presupuesto}
    Ubicación principal: {ubicacion}
    Otras ubicaciones de interés: {', '.join(otras_ubicaciones) if otras_ubicaciones else 'Ninguna'}
    Distancia máxima aceptable: {distancia_maxima} km
    Bilingüe: {'Sí' if bilingue else 'No'}
    Transporte escolar: {'Sí' if transporte else 'No'}
    Orientación religiosa: {religion if religion != "Otro" else otra_religion}
    Actividades extracurriculares: {', '.join(actividades_extra)}
    """
    
    with st.spinner("Buscando recomendaciones..."):
        ai_recommendations = get_ai_recommendations(user_input)
        st.subheader("Recomendaciones de la IA:")
        st.write(ai_recommendations)
    
    with st.spinner("Buscando información adicional..."):
        search_query = f"Mejores colegios en {ubicaciones}, departamento de Guatemala para estudiantes de {edad} años"
        if religion != "No es un factor importante":
            search_query += f" {religion}"
        search_results = search_schools(search_query)
        
        st.subheader("Resultados de búsqueda adicionales:")
        for result in search_results.get('organic', [])[:3]:
            st.write(f"**{result['title']}**")
            st.write(result['snippet'])
            st.write(f"[Más información]({result['link']})")
            st.write("---")

st.write("Nota: Esta aplicación proporciona recomendaciones basadas en la información proporcionada. Te recomendamos investigar más a fondo y contactar directamente a los colegios para obtener información más precisa y actualizada.")

# Mapa del departamento de Guatemala
st.subheader("Mapa del Departamento de Guatemala")
st.write("Para ayudarte a visualizar las ubicaciones, aquí tienes un mapa del departamento de Guatemala:")

guatemala_map = """
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d123770.52750428112!2d-90.61540065!3d14.6417434!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8589a180655c3345%3A0x4a72c7815b867b25!2sDepartamento%20de%20Guatemala!5e0!3m2!1ses!2sgt!4v1661787672985!5m2!1ses!2sgt" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
"""
st.components.v1.html(guatemala_map, height=500)
