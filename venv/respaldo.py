import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from streamlit_option_menu import option_menu
from PIL import Image
import locale
import io  # Para la descarga del gráfico

# Configurar la localización en español para los meses
# locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

# Variable de fecha de actualización
FECHA_ACTUALIZACION = "2025-01-31"

# Rutas de los archivos Excel para uso global
EXCEL_FILE_PATH = "20241221 Cronograma IT v3 - copia (1).xlsx"
EXCEL_RECURSO_PATH = "Estimacion_RecursosIT.xlsx"


def cargar_datos():
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, engine="openpyxl")
        df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
        df['Finish'] = pd.to_datetime(df['Finish'], errors='coerce')
        df['Duration'] = df['Duration'].astype(str).str.replace('hrs', '', regex=True).str.replace(',', '', regex=True).astype(int)
        df['Year Start'] = df['Start'].dt.year
        df['Year Finish'] = df['Finish'].dt.year
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None

def cargar_recursos():
    try:
        df_recursos = pd.read_excel(EXCEL_RECURSO_PATH, engine="openpyxl").fillna(0)
        df_recursos.columns = ['Funcionario', 'Mes', 'Anno', 'Horas']
        return df_recursos
    except Exception as e:
        st.error(f"Error al cargar el archivo de recursos: {e}")
        return None


def extraer_anios(df):
    anios = sorted(df['Anno'].unique())
    return anios


def extraer_meses(df, anio_seleccionado):
    meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    meses = sorted(df[df['Anno'] == anio_seleccionado]['Mes'].unique(), key=lambda x: meses_ordenados.index(x))
    return meses


def ordenar_meses(df):
    meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df['Mes'] = pd.Categorical(df['Mes'], categories=meses_ordenados, ordered=True)
    return df.sort_values('Mes')


def mostrar_informacion_proyecto():
    # Estilo global para un diseño uniforme y moderno
    st.markdown("""
        <style>
            .main {
                max-width: 750px;
                margin: 0 auto;
            }
            .header-section {
                background-color: #E8F5E9;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
                text-align: center;
            }
            .header-section h1 {
                color: #007A33;
                font-size: 40px;
                margin-bottom: 5px;
            }
            .header-section p {
                color: #555;
                font-size: 16px;
                margin: 0;
                letter-spacing: 1px;
            }
            .section {
                background-color: #F5F5F5;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .section h3 {
                color: #007A33;
                margin-bottom: 15px;
            }
            .update-info {
                background-color: #E3F2FD;
                padding: 10px;
                border-radius: 8px;
                color: #0D47A1;
                font-weight: bold;
                display: inline-block;
            }
            /* Estilo para la nueva visualización de Metodología */
            .method-card {
                display: flex;
                align-items: center;
                background-color: #E8F5E9;
                padding: 15px 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
                border-left: 5px solid #007A33;
            }
            .method-card:nth-child(even) {
                background-color: #F1F8E9;
            }
            .method-icon {
                font-size: 24px;
                color: #007A33;
                margin-right: 15px;
            }
            .method-text {
                font-size: 18px;
                color: #333;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # Contenedor principal
    st.markdown('<div class="main">', unsafe_allow_html=True)

    # Encabezado del Proyecto
    st.markdown("""
        <div class='header-section'>
            <h1>🚍 Modernización Tecnológica de la<br>Intendencia de Transporte</h1>
            <p>AUTORIDAD REGULADORA DE LOS SERVICIOS PÚBLICOS</p>
        </div>
    """, unsafe_allow_html=True)

    # Última actualización
    st.markdown("<div class='update-info'>📅 Última actualización: 2025-01-31</div>", unsafe_allow_html=True)
    st.write("")
    # Objetivo
    st.markdown("""
        <div class='section'>
            <h3>🎯 Objetivo</h3>
            <p style='text-align: justify;'>
                Implementar soluciones tecnológicas modernas y eficientes que fortalezcan la capacidad de la Intendencia de Transporte para regular y supervisar los servicios públicos de transporte,
                facilitando la gestión de datos, la autogestión de usuarios, el cálculo tarifario y la integración con sistemas estratégicos.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Metas
    st.markdown("""
        <div class='section'>
            <h3>📌 Metas</h3>
            <ul>
                <li>Actualizar y desarrollar 40 ingresadores tecnológicos.</li>
                <li>Implementar un sistema de autogestión de usuarios.</li>
                <li>Optimizar el cálculo tarifario para el servicio de autobús.</li>
                <li>Desarrollar un módulo de consultas para la base de datos SIR.</li>
                <li>Integrar previsiones para la conexión con sistemas de pago electrónico.</li>
                <li>Generar herramientas de análisis y datos abiertos.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

            # Título de la sección del equipo
    st.markdown("""
        <h2 style='color:#007A33;'>👥 Equipo de Proyecto</h2>
        <hr style='border:1px solid #007A33;'>
    """, unsafe_allow_html=True)

    # Definición del equipo
    equipo = [
        {"rol": "DTT PM/Analista", "nombre": "Ever Alfaro"},
        {"rol": "DTT Analista", "nombre": "Eddie Leal"},
        {"rol": "DTT Base de Datos", "nombre": "Roberto Campos"},
        {"rol": "DTT Implementador", "nombre": "Gabriel Fuentes"},
        {"rol": "DTT QA", "nombre": "Por Asignar"},
        {"rol": "IT Dueño de Negocio", "nombre": "Sofía Arburola"}
    ]

    # Estilo para las tarjetas
    st.markdown("""
        <style>
            .card {
                background-color: #F5F5F5;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            .card h4 {
                margin: 0;
                color: #007A33;
            }
            .card p {
                margin: 5px 0 0;
                color: #333;
            }
        </style>
    """, unsafe_allow_html=True)

    # Mostrar el equipo en dos columnas
    col1, col2 = st.columns(2)

    for index, miembro in enumerate(equipo):
        with (col1 if index % 2 == 0 else col2):
            st.markdown(f"""
                <div class='card'>
                    <h4>{miembro['rol']}</h4>
                    <p><strong>{miembro['nombre']}</strong></p>
                </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    # Nueva visualización de la Metodología de Trabajo
    st.markdown("""
        <div class='section'>
            <h3>🛠️ Metodología de Trabajo</h3>
            <div class='method-card'>
                <div class='method-icon'>📊</div>
                <div class='method-text'>Análisis</div>
            </div>
            <div class='method-card'>
                <div class='method-icon'>💻</div>
                <div class='method-text'>Desarrollo</div>
            </div>
            <div class='method-card'>
                <div class='method-icon'>🧪</div>
                <div class='method-text'>QAT</div>
            </div>
            <div class='method-card'>
                <div class='method-icon'>✅</div>
                <div class='method-text'>UAT</div>
            </div>
            <div class='method-card'>
                <div class='method-icon'>📄</div>
                <div class='method-text'>Documentación</div>
            </div>
            <div class='method-card'>
                <div class='method-icon'>🎓</div>
                <div class='method-text'>Capacitación</div>
            </div>
            <div class='method-card'>
                <div class='method-icon'>🚀</div>
                <div class='method-text'>Implementación</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Cerrar el contenedor principal
    st.markdown("</div>", unsafe_allow_html=True)


def mostrar_recurso_humano(selected_nombre, selected_year, selected_month):
    # Estilos modernos
    st.markdown("""
        <style>
            .main {
                max-width: 750px;
                margin: 0 auto;
            }
            .section {
                background-color: #F5F5F5;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .section h2 {
                color: #007A33;
                font-size: 34px;
                text-align: center;
                margin-bottom: 10px;
            }
            .update-info {
                background-color: #E3F2FD;
                padding: 10px;
                border-radius: 8px;
                color: #0D47A1;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }
            .stSelectbox label {
                color: #007A33;
                font-weight: bold;
            }
            .stPlotlyChart, .stPyplot {
                border-radius: 12px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
                padding: 10px;
                background-color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    # Encabezado moderno
    st.markdown("""
        <div class='main'>
            <div class='section'>
                <h2>👥 Recurso Humano del Proyecto</h2>                
            </div>
        </div>
    """, unsafe_allow_html=True)

    df_recursos = cargar_recursos()
    if df_recursos is not None:
        if selected_year != 'Todos':
            df_recursos = df_recursos[df_recursos['Anno'] == selected_year]
        if selected_month != 'Todos':
            df_recursos = df_recursos[df_recursos['Mes'] == selected_month]

        df_grouped_ano = df_recursos.groupby(['Funcionario', 'Anno'])['Horas'].sum().reset_index()
        if selected_nombre != 'Todos':
            df_grouped_ano = df_grouped_ano[df_grouped_ano['Funcionario'] == selected_nombre]

        # Paleta de colores moderna
        unique_names = df_recursos['Funcionario'].unique()
        material_colors = ['#4285F4', '#DB4437', '#F4B400', '#0F9D58', '#AB47BC', '#5F6368', '#FF7043', '#9E9D24']
        color_mapping = {name: material_colors[i % len(material_colors)] for i, name in enumerate(unique_names)}

        # Gráfico de Horas por Año
        st.markdown("<div class='section'><h3 style='text-align:center;'>📊 Sumatoria de Horas por Año</h3>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = pd.Series([0] * len(df_grouped_ano['Anno'].unique()), index=df_grouped_ano['Anno'].unique())
        
        for nombre, group in df_grouped_ano.groupby('Funcionario'):
            bars = ax.bar(group['Anno'].astype(str), group['Horas'], label=nombre, 
                          bottom=bottom[group['Anno']].values, color=color_mapping[nombre])
            bottom[group['Anno']] += group['Horas'].values

            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    bar_center = bar.get_y() + height / 2
                    ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, bar_center),
                                ha='center', va='center', fontsize=10, color='white')

        ax.set_xlabel('Año', fontsize=14)
        ax.set_ylabel('Horas', fontsize=14)
        ax.legend(title='Recurso')
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

        if selected_year != 'Todos':
            # Gráfico de Horas por Mes
            st.markdown("<div class='section'><h3 style='text-align:center;'>📈 Sumatoria de Horas por Mes</h3>", unsafe_allow_html=True)
            df_grouped_mes = df_recursos.groupby(['Funcionario', 'Mes'])['Horas'].sum().reset_index()
            df_grouped_mes = ordenar_meses(df_grouped_mes)

            fig, ax = plt.subplots(figsize=(12, 6))
            bottom = pd.Series([0] * len(df_grouped_mes['Mes'].unique()), index=df_grouped_mes['Mes'].unique())
            
            for nombre in unique_names:
                group = df_grouped_mes[df_grouped_mes['Funcionario'] == nombre]
                bars = ax.bar(group['Mes'], group['Horas'], label=nombre,
                              bottom=bottom[group['Mes']].values, color=color_mapping.get(nombre, 'gray'))
                bottom[group['Mes']] += group['Horas'].values

                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        bar_center = bar.get_y() + height / 2
                        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, bar_center),
                                    ha='center', va='center', fontsize=10, color='white')
                        
            ax.set_xlabel('Mes', fontsize=14)
            ax.set_ylabel('Horas', fontsize=14)
            ax.legend(title='Recurso')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)

            # Gráfico de Porcentaje de Carga Laboral Mensual
            st.markdown("<div class='section'><h3 style='text-align:center;'>📌 Porcentaje de Carga Laboral Mensual</h3>", unsafe_allow_html=True)
            df_grouped_carga = df_grouped_mes.copy()
            df_grouped_carga['Porcentaje'] = ((df_grouped_carga['Horas'] / 160) * 100).astype(int)

            fig, ax = plt.subplots(figsize=(12, 6))
            bottom = pd.Series([0] * len(df_grouped_carga['Mes'].unique()), index=df_grouped_carga['Mes'].unique())
            
            for nombre in unique_names:
                group = df_grouped_carga[df_grouped_carga['Funcionario'] == nombre]
                if not group.empty:
                    bars = ax.bar(group['Mes'], group['Porcentaje'], label=nombre,
                                  bottom=bottom[group['Mes']].values, color=color_mapping.get(nombre, 'gray'))
                    bottom[group['Mes']] += group['Porcentaje'].values

                    for bar, (_, row) in zip(bars, group.iterrows()):
                        height = bar.get_height()
                        if height > 0:
                            bar_center = bar.get_y() + height / 2
                            ax.annotate(f'{row["Porcentaje"]}%', xy=(bar.get_x() + bar.get_width() / 2, bar_center),
                                        ha='center', va='center', fontsize=10, color='white')

            ax.set_xlabel('Mes', fontsize=14)
            ax.set_ylabel('Porcentaje (%)', fontsize=14)
            ax.legend(title='Recurso')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)

def mostrar_grafico():

    st.markdown("""
        <style>
            .main {
                max-width: 900px;
                margin: 0 auto;
            }
            .section {
                background-color: #F5F5F5;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .section h2 {
                color: #007A33;
                font-size: 34px;
                text-align: center;
                margin-bottom: 10px;
            }
            .stSelectbox label {
                color: #007A33;
                font-weight: bold;
            }
            .download-btn .css-1aumxhk {
                background-color: #D32F2F !important;
                color: white !important;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
            }
            .download-btn .css-1aumxhk:hover {
                background-color: #B71C1C !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Encabezado moderno
    st.markdown("""
        <div class='main'>
            <div class='section'>
                <h2>🗓️ Cronograma del Proyecto</h2>                
            </div>
        </div>
    """, unsafe_allow_html=True)

    df = cargar_datos()
    if df is not None:
        years = sorted(set(df['Year Start'].dropna().astype(int)).union(set(df['Year Finish'].dropna().astype(int))))
        if 2025 not in years:
            years.append(2025)
        years = ['Todos'] + sorted(set(years))
        selected_year = st.sidebar.selectbox("🿕️ Seleccione un año", years, index=0)

        df_filtered = df[df['Outline Level'] == 1].copy()

        if selected_year != 'Todos':
            df_filtered = df_filtered[(df_filtered['Year Start'] == selected_year) | (df_filtered['Year Finish'] == selected_year)]

        df_filtered = df_filtered.sort_values(by='Start', ascending=True)

        selected_task = None
        if selected_year != 'Todos':
            task_names = ['Todas'] + df_filtered['Name'].unique().tolist()
            selected_task = st.sidebar.selectbox("📋 Seleccione una tarea", task_names, index=0)
            if selected_task != "Todas":
                task_outline_level_1 = df_filtered[df_filtered['Name'] == selected_task]
                if not task_outline_level_1.empty:
                    task_start = task_outline_level_1.iloc[0]['Start']
                    task_finish = task_outline_level_1.iloc[0]['Finish']

                    df_filtered = df[
                        (df['Outline Level'].isin([1, 2])) &
                        (df['Start'] >= task_start) &
                        (df['Finish'] <= task_finish)
                    ]

        # Mostrar el título del Gantt según la selección de año
        #st.markdown("<div class='section'>", unsafe_allow_html=True)
        if selected_year == 'Todos':
            st.markdown("### 📊Gantt de actividades para **todos los años**", unsafe_allow_html=True)
        else:
            st.markdown(f"### 📊 Gantt de actividades para el año **{selected_year}**", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(18, 10))
        ax.set_facecolor('white')
        df_filtered = df_filtered.reset_index(drop=True)
        y_positions = range(len(df_filtered) - 1, -1, -1)

        bars = ax.barh(y_positions, df_filtered['Finish'] - df_filtered['Start'], left=df_filtered['Start'], color='#0F9D58', height=0.6)

        for bar, (_, row) in zip(bars, df_filtered.iterrows()):
            start_text = row['Start'].strftime('%d/%m/%y') if pd.notnull(row['Start']) else ""
            finish_text = row['Finish'].strftime('%d/%m/%y') if pd.notnull(row['Finish']) else ""
            bar_center = bar.get_y() + bar.get_height() / 2

            ax.text(row['Start'], bar_center, start_text, verticalalignment='center', horizontalalignment='right', fontsize=11, color='#4285F4')
            ax.text(row['Finish'], bar_center, finish_text, verticalalignment='center', horizontalalignment='left', fontsize=11, color='#4285F4')
            ax.text(row['Start'] + (row['Finish'] - row['Start']) / 2, bar_center + 0.3, row['Name'], verticalalignment='bottom', horizontalalignment='center', fontsize=11, fontweight='bold', color='black')

        ax.set_xlabel("Fecha", fontsize=14, fontweight='bold')
        ax.set_ylabel("", fontsize=14, fontweight='bold')
        ax.set_title(f"Gantt de actividades para el año {selected_year}", fontsize=16, fontweight='bold')
        ax.set_yticks(y_positions)
        ax.set_yticklabels([])

        if selected_year == 'Todos':
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.set_xlim(left=pd.Timestamp(year=2025, month=1, day=1))
        else:
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

            today = datetime.today()
            if today.year == selected_year:
                ax.axvline(today, color='red', linestyle='--', linewidth=2)

        ax.grid(False)
        plt.xticks(fontsize=14, fontweight='bold', color='black', rotation=0)

        st.pyplot(fig)
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)

        # Botón de descarga con estilo moderno
        st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
        st.download_button(
            label="📁 Descargar gráfico",
            data=buffer,
            file_name="grafico_linea_tiempo.png",
            mime="image/png"
        )
        st.markdown("</div>", unsafe_allow_html=True)



def main():
    with st.sidebar:
        opcion = option_menu(
            "Menú",
            ["Ficha del Proyecto", "Cronograma", "Recurso Humano"],
            icons=["house", "calendar-range", "people"],
            menu_icon="cast",
            default_index=0
        )

        selected_nombre = 'Todos'
        selected_year = 'Todos'
        selected_month = 'Todos'

        if opcion == "Recurso Humano":
            df_recursos = cargar_recursos()
            if df_recursos is not None:
                nombres = df_recursos['Funcionario'].unique().tolist()
                nombres.insert(0, 'Todos')
                selected_nombre = st.selectbox("Seleccione un recurso humano", nombres, index=0)

                anios = extraer_anios(df_recursos)
                anios.insert(0, 'Todos')
                selected_year = st.selectbox("Seleccione un año del proyecto", anios)



    if opcion == "Ficha del Proyecto":
        mostrar_informacion_proyecto()
    elif opcion == "Cronograma":
        mostrar_grafico()
    elif opcion == "Recurso Humano":
        mostrar_recurso_humano(selected_nombre, selected_year, selected_month)


if __name__ == "__main__":
    main()

