import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
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

        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = pd.Series([0] * len(df_grouped_ano['Anno'].unique()), index=df_grouped_ano['Anno'].unique())
        for nombre, group in df_grouped_ano.groupby('Funcionario'):
            bars = ax.bar(group['Anno'].astype(str), group['Horas'], label=nombre, bottom=bottom[group['Anno']].values)
            bottom[group['Anno']] += group['Horas'].values

            for bar in bars:
                height = bar.get_height()
                bar_center = bar.get_y() + height / 2
                ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, bar_center),
                            xytext=(0, 0), textcoords="offset points",
                            ha='center', va='center', fontsize=10, color='white')

        ax.set_title('Sumatoria de Horas por Año', fontsize=16, fontweight='bold')
        ax.set_xlabel('Año', fontsize=14)
        ax.set_ylabel('Horas', fontsize=14)
        ax.legend(title='Recurso')
        st.pyplot(fig)

        st.write("### Sumatoria de horas por mes")
        df_grouped_mes = df_recursos.groupby(['Funcionario', 'Mes'])['Horas'].sum().reset_index()
        df_grouped_mes = ordenar_meses(df_grouped_mes)

        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = pd.Series([0] * len(df_grouped_mes['Mes'].unique()), index=df_grouped_mes['Mes'].unique())
        for nombre, group in df_grouped_mes.groupby('Funcionario'):
            bars = ax.bar(group['Mes'], group['Horas'], label=nombre, bottom=bottom[group['Mes']].values)
            bottom[group['Mes']] += group['Horas'].values

            for bar in bars:
                height = bar.get_height()
                bar_center = bar.get_y() + height / 2
                ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, bar_center),
                            xytext=(0, 0), textcoords="offset points",
                            ha='center', va='center', fontsize=10, color='white')

        ax.set_title('Sumatoria de Horas por Mes', fontsize=16, fontweight='bold')
        ax.set_xlabel('Mes', fontsize=14)
        ax.set_ylabel('Horas', fontsize=14)
        ax.legend(title='Recurso')
        plt.xticks(rotation=45)
        st.pyplot(fig)


def mostrar_grafico():
    st.title("�헏️ Visualización de la Línea del Tiempo")
    st.write(f"🔄 Última actualización: {FECHA_ACTUALIZACION}")

    df = cargar_datos()
    if df is not None:
        st.dataframe(df)


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

                if selected_year != 'Todos':
                    meses = extraer_meses(df_recursos, selected_year)
                    meses.insert(0, 'Todos')
                    selected_month = st.selectbox("Seleccione un mes del proyecto", meses)

    if opcion == "Información del Proyecto":
        mostrar_informacion_proyecto()
    elif opcion == "Visualización de la Línea del Tiempo":
        mostrar_grafico()
    elif opcion == "Recurso Humano":
        mostrar_recurso_humano(selected_nombre, selected_year, selected_month)


if __name__ == "__main__":
    main()
