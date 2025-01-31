import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Lectura de archivo Excel con Pandas y Streamlit")
    
    # Subir archivo Excel
    uploaded_file = st.file_uploader("Sube un archivo Excel", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        # Leer archivo Excel
        try:
            df = pd.read_excel(uploaded_file)
            
            # Convertir columnas a tipos adecuados
            df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
            df['Finish'] = pd.to_datetime(df['Finish'], errors='coerce')
            df['Duration'] = df['Duration'].astype(str).str.replace('hrs', '', regex=True).str.replace(',', '', regex=True).astype(int)
            
            # Extraer años de Start y Finish
            df['Year Start'] = df['Start'].dt.year
            df['Year Finish'] = df['Finish'].dt.year
            
            # Obtener lista de años únicos para el filtro
            years = sorted(set(df['Year Start'].dropna().astype(int)).union(set(df['Year Finish'].dropna().astype(int))))
            years.insert(0, 'Todos')
            
            # Selección de año en Streamlit
            selected_year = st.selectbox("Seleccione un año", years)
            
            # Filtrar registros con "Outline Level" igual a 1
            df_filtered = df[df['Outline Level'] == 1].copy()
            
            # Aplicar filtro de año
            if selected_year != 'Todos':
                df_filtered = df_filtered[(df_filtered['Year Start'] == selected_year) | (df_filtered['Year Finish'] == selected_year)]
            
            df_filtered = df_filtered.sort_values(by='Start', ascending=True)  # Ordenar por fecha de inicio
            
            # Crear gráfico de barras en lugar de líneas
            st.write("### Línea del tiempo de los registros con Outline Level 1")
            fig, ax = plt.subplots(figsize=(14, 10))  # Aumentar tamaño de la figura
            
            # Invertir el índice para que las tareas aparezcan de arriba hacia abajo
            df_filtered = df_filtered.reset_index(drop=True)
            y_positions = range(len(df_filtered) - 1, -1, -1)  # Invertir posiciones Y
            
            ax.barh(y_positions, df_filtered['Finish'] - df_filtered['Start'], left=df_filtered['Start'], color='green', height=0.4)
            
            # Agregar etiquetas de tareas sobre las barras en lugar de al lado izquierdo
            for y, (_, row) in zip(y_positions, df_filtered.iterrows()):
                ax.text(row['Finish'], y, row['Name'], verticalalignment='center', horizontalalignment='left', fontsize=10, fontweight='bold', color='black', bbox=dict(facecolor='white', alpha=0.7))
            
            ax.set_xlabel("Fecha", fontsize=12, fontweight='bold')
            ax.set_ylabel("", fontsize=12, fontweight='bold')  # Eliminar etiqueta del eje Y
            ax.set_title("Línea del tiempo de tareas nivel 1", fontsize=14, fontweight='bold')
            ax.set_yticks(y_positions)
            ax.set_yticklabels([])  # Ocultar etiquetas del eje Y completamente
            
            plt.xticks(rotation=45, fontsize=10)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

if __name__ == "__main__":
    main()
