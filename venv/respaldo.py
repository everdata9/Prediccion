import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from streamlit_option_menu import option_menu
import locale
import io  # Para la descarga del gráfico

# Configurar la localización en español para los meses
#locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

# Variable de fecha de actualización
FECHA_ACTUALIZACION = "2025-01-31"

# Ruta del archivo Excel para uso global
EXCEL_FILE_PATH = "20241221 Cronograma IT v3 - copia (1).xlsx"

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

def mostrar_informacion_proyecto():
    st.title("📄 Información del Proyecto")
    st.write("Este proyecto permite la visualización de una línea del tiempo en formato de barras, basado en un archivo Excel con fechas de inicio y fin de tareas.")
    st.write("### Características principales:")
    st.write("- Carga automática de un archivo Excel con información de tareas desde la carpeta del sistema.")
    st.write("- Conversión de fechas y limpieza de datos.")
    st.write("- Filtro de tareas por año de inicio o fin.")
    st.write("- Visualización de tareas en formato de barras con etiquetas de nombre y fechas.")
    st.write("- Interfaz interactiva con Streamlit.")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")

def mostrar_recursos():
    st.title("👥 Recursos Humanos del Proyecto")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")
    st.write("Lista de los recursos humanos asignados al proyecto:")
    recursos_humanos = [
        "Juan Pérez - Gerente de Proyecto",
        "María López - Desarrolladora Backend",
        "Carlos Ramírez - Diseñador UX/UI",
        "Ana Torres - Analista de Datos",
        "Luis Gómez - Ingeniero DevOps"
    ]
    for recurso in recursos_humanos:
        st.write(f"- {recurso}")

def mostrar_grafico():
    st.title("📅 Visualización de la Línea del Tiempo")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")
    
    df = cargar_datos()
    if df is not None:
        years = sorted(set(df['Year Start'].dropna().astype(int)).union(set(df['Year Finish'].dropna().astype(int))))
        if 2025 not in years:
            years.append(2025)  
        years = ['Todos'] + sorted(set(years))

        selected_year = st.sidebar.selectbox("📅 Seleccione un año", years, index=0)

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
        
        st.write("### Línea del tiempo de los registros con Outline Level 1 y 2")
        fig, ax = plt.subplots(figsize=(18, 10))
        ax.set_facecolor('white')

        df_filtered = df_filtered.reset_index(drop=True)
        y_positions = range(len(df_filtered) - 1, -1, -1)
        
        bars = ax.barh(y_positions, df_filtered['Finish'] - df_filtered['Start'], left=df_filtered['Start'], color='green', height=0.6)
        
        for bar, (_, row) in zip(bars, df_filtered.iterrows()):
            start_text = row['Start'].strftime('%b %Y').capitalize() if pd.notnull(row['Start']) else ""
            finish_text = row['Finish'].strftime('%b %Y').capitalize() if pd.notnull(row['Finish']) else ""
            bar_center = bar.get_y() + bar.get_height() / 2
            
            ax.text(row['Start'], bar_center, start_text, verticalalignment='center', horizontalalignment='right', fontsize=11, color='black')
            ax.text(row['Finish'], bar_center, finish_text, verticalalignment='center', horizontalalignment='left', fontsize=11, color='black')
            ax.text(row['Start'] + (row['Finish'] - row['Start']) / 2, bar_center + 0.3, row['Name'], verticalalignment='bottom', horizontalalignment='center', fontsize=11, fontweight='bold', color='black')
        
        ax.set_xlabel("Fecha", fontsize=14, fontweight='bold')
        ax.set_ylabel("", fontsize=14, fontweight='bold')
        ax.set_title("Línea del tiempo de tareas nivel 1 y 2", fontsize=16, fontweight='bold')
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

        st.download_button(
            label="📥 Descargar gráfico",
            data=buffer,
            file_name="grafico_linea_tiempo.png",
            mime="image/png"
        )

def main():
    with st.sidebar:
        opcion = option_menu(
            "Menú",
            ["Información del Proyecto", "Visualización de la Línea del Tiempo", "Recursos Humanos"],
            icons=["house", "bar-chart", "people"],
            menu_icon="cast",
            default_index=0
        )
    
    if opcion == "Información del Proyecto":
        mostrar_informacion_proyecto()
    elif opcion == "Visualización de la Línea del Tiempo":
        mostrar_grafico()
    elif opcion == "Recursos Humanos":
        mostrar_recursos()

if __name__ == "__main__":
    main()
