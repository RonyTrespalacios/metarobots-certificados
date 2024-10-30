import streamlit as st
import sqlite3
import pandas as pd
from fillpdf import fillpdfs
from io import BytesIO
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env solo en local
if not os.getenv("STREAMLIT_CLOUD"):
    load_dotenv()

# Diccionario para los nombres de los meses en español
MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

# Conectar a la base de datos SQLite
conn = sqlite3.connect("mi_base_de_datos.db")
cursor = conn.cursor()

# Ruta del archivo PDF con campos rellenables
template_pdf_path = 'CICI_Certificado.pdf'

# Función para obtener la fecha en formato español
def obtener_fecha_en_espanol():
    hoy = datetime.now()
    dia = hoy.day
    mes = MESES_ES[hoy.month]
    anio = hoy.year
    return f"Se expide a los ({dia}) días del mes de {mes} de {anio}"

# Función para generar el certificado y aplanar el PDF
def generar_certificado(documento, tipo_documento):
    cursor.execute("SELECT nombre, calidad, categoria FROM documentos WHERE documento = ?", (documento,))
    result = cursor.fetchone()
    
    if result:
        nombre, calidad, categoria = result
        nombre_mayus = nombre.strip().upper()
        tipo_documento_texto = f"{tipo_documento} Número {documento}"
        calidad_format = calidad.strip().capitalize()
        categoria_format = (categoria.strip().upper() if categoria else "").strip()
        calidad_categoria = f"{calidad_format} {categoria_format}".strip()

        # Formatear la fecha en español usando la función personalizada
        fecha_texto = obtener_fecha_en_espanol()

        # Campos a rellenar en el PDF
        fields = {
            "NOMBRE_PARTICIPANTE": nombre_mayus,
            "DOCUMENTO": tipo_documento_texto,
            "CALIDAD": calidad_categoria,
            "FECHA": fecha_texto,
        }
        
        # Rellenar y aplanar el PDF en memoria
        pdf_bytes = BytesIO()
        fillpdfs.write_fillable_pdf(template_pdf_path, pdf_bytes, fields, flatten=True)
        pdf_bytes.seek(0)  # Volver al inicio del archivo en memoria

        # Descargar el PDF aplanado
        st.download_button(
            label="📄 Descargar Certificado en PDF",
            data=pdf_bytes,
            file_name=f"{nombre_mayus}_Certificado.pdf",
            mime="application/pdf"
        )

    else:
        st.error("No encontramos tu documento en nuestra base de datos. 📧 Envía un correo a "
                 "ginvestigacioneysi@unillanos.edu.co con Asunto: Solicitud Certificado de Participación "
                 "e incluye tu nombre completo, número de documento y categorías en las que participaste.")

st.title("📜 Plataforma de Certificados METAROBOTS 2024")

# Función para buscar y generar el certificado
def buscar_y_generar_certificado(documento, tipo_documento):
    cursor.execute("SELECT nombre, calidad, categoria FROM documentos WHERE documento = ?", (documento,))
    result = cursor.fetchone()

    if result:
        generar_certificado(documento, tipo_documento)
    else:
        st.error("No encontramos tu documento en nuestra base de datos. 📧 Envía un correo a "
                 "ginvestigacioneysi@unillanos.edu.co con Asunto: Solicitud Certificado de Participación "
                 "e incluye tu nombre completo, número de documento y categorías en las que participaste.")

        
# Función para autenticación
def autenticar_usuario(username, password):
    # Obtener credenciales desde variables de entorno
    usuario_correcto = os.getenv("STREAMLIT_USER")
    contrasena_correcta = os.getenv("STREAMLIT_PASSWORD")
    
    # Comparar las credenciales ingresadas con las almacenadas
    return username == usuario_correcto and password == contrasena_correcta

# Estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Función para generar certificados personalizados
def generar_certificado_personalizado(nombre, tipo_documento, documento, calidad):
    # Procesar los datos de entrada
    nombre_mayus = nombre.strip().upper()
    tipo_documento_texto = f"{tipo_documento} Número {documento}"
    calidad_format = calidad.strip().capitalize()
    
    # Formatear la fecha en español usando la función personalizada
    fecha_texto = obtener_fecha_en_espanol()

    # Campos a rellenar en el PDF
    fields = {
        "NOMBRE_PARTICIPANTE": nombre_mayus,
        "DOCUMENTO": tipo_documento_texto,
        "CALIDAD": calidad_format,
        "FECHA": fecha_texto,
    }
    
    # Rellenar y aplanar el PDF en memoria
    pdf_bytes = BytesIO()
    fillpdfs.write_fillable_pdf(template_pdf_path, pdf_bytes, fields, flatten=True)
    pdf_bytes.seek(0)  # Volver al inicio del archivo en memoria

    # Descargar el PDF personalizado
    st.download_button(
        label="📄 Descargar Certificado Personalizado",
        data=pdf_bytes,
        file_name=f"{nombre_mayus}_Certificado_Personalizado.pdf",
        mime="application/pdf"
    )

# Función para generar el certificado desde la tabla comite_organizador
def generar_certificado_logistica(documento):
    cursor.execute("SELECT nombre_completo FROM comite_organizador WHERE documento = ?", (documento,))
    result = cursor.fetchone()
    
    if result:
        nombre_completo = result[0]
        tipo_documento = "Cedula de Ciudadania"  # Tipo de documento por defecto
        tipo_documento_texto = f"{tipo_documento} Número {documento}"
        
        # Formatear la fecha en español
        fecha_texto = obtener_fecha_en_espanol()

        # Campos a rellenar en el PDF
        fields = {
            "NOMBRE_PARTICIPANTE": nombre_completo.upper(),
            "DOCUMENTO": tipo_documento_texto,
            "CALIDAD": "Miembro del Comité Organizador",
            "FECHA": fecha_texto,
        }
        
        # Rellenar y aplanar el PDF en memoria
        pdf_bytes = BytesIO()
        fillpdfs.write_fillable_pdf(template_pdf_path, pdf_bytes, fields, flatten=True)
        pdf_bytes.seek(0)  # Volver al inicio del archivo en memoria

        # Descargar el PDF aplanado
        st.download_button(
            label="📄 Descargar Certificado Logística",
            data=pdf_bytes,
            file_name=f"{nombre_completo}_Certificado_Logistica.pdf",
            mime="application/pdf"
        )
    else:
        st.error("No encontramos tu documento en la base de datos del comité organizador. 📧 Contacta con soporte.")

# Pestañas iniciales para descarga de certificados, iniciar sesión y logística
tab1, tab2, tab3 = st.tabs(["Descargar Certificado 📄", "Iniciar Sesión 🔒", "Logística 📋"])

with tab1:
    st.subheader("Descargar Certificado de Participación 📑")
    documento = st.text_input("Ingrese su Número de Documento")
    tipo_documento = st.selectbox("Seleccione el Tipo de Documento", ["Cedula de Ciudadania", "Tarjeta de Identidad"])

    if st.button("Generar Certificado 🖨️"):
        if documento:
            buscar_y_generar_certificado(documento, tipo_documento)
        else:
            st.error("Por favor, ingrese un número de documento. ⚠️")

with tab2:
    st.subheader("Iniciar Sesión 🔑")
    if not st.session_state["authenticated"]:
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar 🚪"):
            if autenticar_usuario(username, password):
                st.session_state["authenticated"] = True
                st.success("Autenticación exitosa 🎉")
                st.query_params = {"auth": "true"}
            else:
                st.error("Credenciales incorrectas ❌")
    elif st.session_state["authenticated"]:
        # Pestañas de administración de documentos
        st.subheader("Administración de Documentos 📂")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Agregar Documento ➕", "Modificar Documento ✏️", "Eliminar Documento ❌", 
            "Ver Documentos 📊", "Generar Certificado Personalizado 🎖️"
        ])

        # Agregar documentos
        with tab1:
            st.subheader("Agregar Documento 📝")
            documento = st.text_input("Documento", key="add_documento")
            nombre = st.text_input("Nombre", key="add_nombre")
            calidad = st.text_input("Calidad", key="add_calidad")
            categoria = st.text_input("Categoria", key="add_categoria")

            if st.button("Agregar ✅"):
                cursor.execute("INSERT INTO documentos (documento, nombre, calidad, categoria) VALUES (?, ?, ?, ?)",
                               (documento, nombre, calidad, categoria))
                conn.commit()
                st.success("Documento agregado exitosamente 🎉")

        # Modificar documentos
        with tab2:
            st.subheader("Modificar Documento ✏️")
            cursor.execute("SELECT id, documento FROM documentos")
            documentos = cursor.fetchall()
            doc_ids = {doc[1]: doc[0] for doc in documentos}
            
            doc_seleccionado = st.selectbox("Selecciona el Documento", options=doc_ids.keys())
            
            if doc_seleccionado:
                doc_id = doc_ids[doc_seleccionado]
                cursor.execute("SELECT nombre, calidad, categoria FROM documentos WHERE id = ?", (doc_id,))
                nombre, calidad, categoria = cursor.fetchone()
                
                # Formulario de edición
                nuevo_nombre = st.text_input("Nuevo Nombre", nombre)
                nueva_calidad = st.text_input("Nueva Calidad", calidad)
                nueva_categoria = st.text_input("Nueva Categoria", categoria)
                
                if st.button("Modificar 🛠️"):
                    cursor.execute("""
                        UPDATE documentos
                        SET nombre = ?, calidad = ?, categoria = ?
                        WHERE id = ?
                    """, (nuevo_nombre, nueva_calidad, nueva_categoria, doc_id))
                    conn.commit()
                    st.success("Documento modificado exitosamente ✔️")

        # Eliminar documentos
        with tab3:
            st.subheader("Eliminar Documento 🗑️")
            doc_seleccionado_eliminar = st.selectbox("Selecciona el Documento a Eliminar", options=doc_ids.keys())
            
            if st.button("Eliminar ❌"):
                doc_id_eliminar = doc_ids[doc_seleccionado_eliminar]
                cursor.execute("DELETE FROM documentos WHERE id = ?", (doc_id_eliminar,))
                conn.commit()
                st.success("Documento eliminado exitosamente ✔️")

        # Visualizar y filtrar documentos
        with tab4:
            st.subheader("Ver y Filtrar Documentos 📊")
            query = "SELECT * FROM documentos"
            df = pd.read_sql_query(query, conn)

            texto_busqueda = st.text_input("Buscar por nombre o categoría")
            if texto_busqueda:
                df = df[(df["nombre"].str.contains(texto_busqueda, case=False)) |
                        (df["categoria"].str.contains(texto_busqueda, case=False))]

            categorias = df["categoria"].unique()
            categoria_seleccionada = st.multiselect("Filtrar por Categoría", options=categorias)
            if categoria_seleccionada:
                df = df[df["categoria"].isin(categoria_seleccionada)]

            st.write("Resultados:")
            st.dataframe(df)

        # Generar certificado personalizado
        with tab5:
            st.subheader("Generar Certificado Personalizado 🎖️")
            nombre = st.text_input("Nombre del Participante", key="cert_nombre")
            tipo_documento = st.selectbox("Tipo de Documento", ["Cedula de Ciudadania", "Tarjeta de Identidad"], key="cert_tipo_documento")
            numero_documento = st.text_input("Número de Documento", key="cert_numero_documento")  # Nuevo campo para el número
            calidad = st.text_input("Calidad", key="cert_calidad")

            if st.button("Generar Certificado Personalizado 🖨️"):
                if nombre and tipo_documento and numero_documento and calidad:
                    generar_certificado_personalizado(nombre, tipo_documento, numero_documento, calidad)
                else:
                    st.error("Por favor, complete todos los campos necesarios. ⚠️")

        # Cerrar sesión
        if st.button("Cerrar sesión 🔓"):
            st.session_state["authenticated"] = False

# Tab "Logística"
with tab3:
    st.subheader("Certificado Comité Organizador (Logística) 📋")
    documento = st.text_input("Ingrese su Número de Documento", key="logistica_documento")

    if st.button("Generar Certificado Logística 🖨️"):
        if documento:
            # Llamar a la función que genera el certificado usando la tabla `comite_organizador`
            generar_certificado_logistica(documento)
        else:
            st.error("Por favor, ingrese un número de documento. ⚠️")

# Agregar imagen centrada al final del tab
st.markdown('''
    <style>
    .center-image {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .center-image img {
        max-width: 100%;
        height: auto;
    }
    </style>
''', unsafe_allow_html=True)

st.markdown('<div class="center-image">', unsafe_allow_html=True)
st.image("image.png", use_column_width=True)
st.markdown('</div>', unsafe_allow_html=True)