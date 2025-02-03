import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from streamlit_option_menu import option_menu
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
    st.title("📄 Información del Proyecto")
    st.write("Este proyecto permite la visualización de una línea del tiempo en formato de barras, basado en un archivo Excel con fechas de inicio y fin de tareas.")
    st.write("### Características principales:")
    st.write("- Carga automática de un archivo Excel con información de tareas desde la carpeta del sistema.")
    st.write("- Conversión de fechas y limpieza de datos.")
    st.write("- Filtro de tareas por año de inicio o fin.")
    st.write("- Visualización de tareas en formato de barras con etiquetas de nombre y fechas.")
    st.write("- Interfaz interactiva con Streamlit.")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")


def mostrar_recurso_humano(selected_nombre, selected_year, selected_month): 
    st.title("👥 Recurso Humano del Proyecto")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")

    df_recursos = cargar_recursos()
    if df_recursos is not None:
        if selected_year != 'Todos':
            df_recursos = df_recursos[df_recursos['Anno'] == selected_year]
        if selected_month != 'Todos':
            df_recursos = df_recursos[df_recursos['Mes'] == selected_month]

        df_grouped_ano = df_recursos.groupby(['Funcionario', 'Anno'])['Horas'].sum().reset_index()
        if selected_nombre != 'Todos':
            df_grouped_ano = df_grouped_ano[df_grouped_ano['Funcionario'] == selected_nombre]

        # Definir paleta de colores consistente
        unique_names = df_recursos['Funcionario'].unique()
        material_colors =  ['#4285F4', '#DB4437', '#F4B400', '#0F9D58', '#AB47BC', '#5F6368', '#FF7043', '#9E9D24']
        color_mapping = {name: material_colors[i % len(material_colors)] for i, name in enumerate(unique_names)}

        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = pd.Series([0] * len(df_grouped_ano['Anno'].unique()), index=df_grouped_ano['Anno'].unique())
        for nombre, group in df_grouped_ano.groupby('Funcionario'):
            bars = ax.bar(group['Anno'].astype(str), group['Horas'], label=nombre, bottom=bottom[group['Anno']].values, color=color_mapping[nombre])
            bottom[group['Anno']] += group['Horas'].values

            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    bar_center = bar.get_y() + height / 2
                    ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, bar_center), xytext=(0, 0), textcoords="offset points", ha='center', va='center', fontsize=10, color='white')

        ax.set_title('Sumatoria de Horas por Año', fontsize=16, fontweight='bold')
        ax.set_xlabel('Año', fontsize=14)
        ax.set_ylabel('Horas', fontsize=14)
        ax.legend(title='Recurso')
        st.pyplot(fig)

        if selected_year != 'Todos':
            st.write("### Sumatoria de horas por mes")
            df_grouped_mes = df_recursos.groupby(['Funcionario', 'Mes'])['Horas'].sum().reset_index()
            df_grouped_mes = ordenar_meses(df_grouped_mes)

            fig, ax = plt.subplots(figsize=(12, 6))
            bottom = pd.Series([0] * len(df_grouped_mes['Mes'].unique()), index=df_grouped_mes['Mes'].unique())
            for nombre in unique_names:
                group = df_grouped_mes[df_grouped_mes['Funcionario'] == nombre]
                bars = ax.bar(group['Mes'], group['Horas'], label=nombre, bottom=bottom[group['Mes']].values, color=color_mapping.get(nombre, 'gray'))
                bottom[group['Mes']] += group['Horas'].values

                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        bar_center = bar.get_y() + height / 2
                        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, bar_center), xytext=(0, 0), textcoords="offset points", ha='center', va='center', fontsize=10, color='white')
            ax.set_title('Sumatoria de Horas por Mes', fontsize=16, fontweight='bold')
            ax.set_xlabel('Mes', fontsize=14)
            ax.set_ylabel('Horas', fontsize=14)
            ax.legend(title='Recurso')
            plt.xticks(rotation=45)
            st.pyplot(fig)

            st.write("### Porcentaje de carga laboral mensual")
            df_grouped_carga = df_grouped_mes.copy()
            df_grouped_carga['Porcentaje'] = ((df_grouped_carga['Horas'] / 160) * 100).astype(int)

            fig, ax = plt.subplots(figsize=(12, 6))
            bottom = pd.Series([0] * len(df_grouped_carga['Mes'].unique()), index=df_grouped_carga['Mes'].unique())
            for nombre in unique_names:
                group = df_grouped_carga[df_grouped_carga['Funcionario'] == nombre]
                if not group.empty:
                    bars = ax.bar(group['Mes'], group['Porcentaje'], label=nombre, bottom=bottom[group['Mes']].values, color=color_mapping.get(nombre, 'gray'))
                    bottom[group['Mes']] += group['Porcentaje'].values

                    for bar, (_, row) in zip(bars, group.iterrows()):
                        height = bar.get_height()
                        if height > 0:
                            bar_center = bar.get_y() + height / 2
                            ax.annotate(f'{row["Porcentaje"]}%', xy=(bar.get_x() + bar.get_width() / 2, bar_center), xytext=(0, 0), textcoords="offset points", ha='center', va='center', fontsize=10, color='white')

            ax.set_title('Porcentaje de Carga Laboral Mensual', fontsize=16, fontweight='bold')
            ax.set_xlabel('Mes', fontsize=14)
            ax.set_ylabel('Porcentaje (%)', fontsize=14)
            ax.legend(title='Recurso')
            plt.xticks(rotation=45)
            st.pyplot(fig)

def mostrar_grafico():
    st.title("🿕️ Visualización de la Línea del Tiempo")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")

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

        st.write("### Línea del tiempo de los registros con Outline Level 1 y 2")
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
            label="👅 Descargar gráfico",
            data=buffer,
            file_name="grafico_linea_tiempo.png",
            mime="image/png"
        )



def main():
    with st.sidebar:
        opcion = option_menu(
            "Menú",
            ["Información del Proyecto", "Visualización de la Línea del Tiempo", "Recurso Humano"],
            icons=["house", "bar-chart", "people"],
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



    if opcion == "Información del Proyecto":
        mostrar_informacion_proyecto()
    elif opcion == "Visualización de la Línea del Tiempo":
        mostrar_grafico()
    elif opcion == "Recurso Humano":
        mostrar_recurso_humano(selected_nombre, selected_year, selected_month)


if __name__ == "__main__":
    main()

