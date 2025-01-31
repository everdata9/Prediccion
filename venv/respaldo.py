import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from streamlit_option_menu import option_menu
import io  # For downloading the chart

# Update date variable
LAST_UPDATE_DATE = "2025-01-31"

# Global Excel file path
EXCEL_FILE_PATH = "20241221 Cronograma IT v3 - copia (1).xlsx"

def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, engine="openpyxl")
        df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
        df['Finish'] = pd.to_datetime(df['Finish'], errors='coerce')
        df['Duration'] = df['Duration'].astype(str).str.replace('hrs', '', regex=True).str.replace(',', '', regex=True).astype(int)
        df['Year Start'] = df['Start'].dt.year
        df['Year Finish'] = df['Finish'].dt.year
        return df
    except Exception as e:
        st.error(f"Error loading the Excel file: {e}")
        return None

def show_project_info():
    st.title("📄 Project Information")
    st.write("This project allows visualization of a timeline using a bar chart based on an Excel file with task start and end dates.")
    st.write("### Key Features:")
    st.write("- Automatic loading of an Excel file with task data from the system folder.")
    st.write("- Date conversion and data cleaning.")
    st.write("- Task filtering by start or end year.")
    st.write("- Task visualization in a bar format with labels.")
    st.write("- Interactive interface with Streamlit.")
    st.write(f"🔄 Last update: {LAST_UPDATE_DATE}")

def show_human_resources():
    st.title("👥 Project Human Resources")
    st.write(f"🔄 Last update: {LAST_UPDATE_DATE}")
    st.write("List of human resources assigned to the project:")
    human_resources = [
        "John Smith - Project Manager",
        "Maria Lopez - Backend Developer",
        "Carlos Ramirez - UX/UI Designer",
        "Anna Torres - Data Analyst",
        "Luis Gomez - DevOps Engineer"
    ]
    for resource in human_resources:
        st.write(f"- {resource}")

def show_chart():
    st.title("📅 Timeline Visualization")
    st.write(f"🔄 Last update: {LAST_UPDATE_DATE}")
    
    df = load_data()
    if df is not None:
        years = sorted(set(df['Year Start'].dropna().astype(int)).union(set(df['Year Finish'].dropna().astype(int))))
        if 2025 not in years:
            years.append(2025)  
        years = ['All'] + sorted(set(years))

        selected_year = st.sidebar.selectbox("📅 Select a Year", years, index=0)

        df_filtered = df[df['Outline Level'] == 1].copy()
        
        if selected_year != 'All':
            df_filtered = df_filtered[(df_filtered['Year Start'] == selected_year) | (df_filtered['Year Finish'] == selected_year)]
        
        df_filtered = df_filtered.sort_values(by='Start', ascending=True)

        selected_task = None
        if selected_year != 'All':
            task_names = ['All'] + df_filtered['Name'].unique().tolist()
            selected_task = st.sidebar.selectbox("📋 Select a Task", task_names, index=0)

            if selected_task != "All":
                task_outline_level_1 = df_filtered[df_filtered['Name'] == selected_task]
                if not task_outline_level_1.empty:
                    task_start = task_outline_level_1.iloc[0]['Start']
                    task_finish = task_outline_level_1.iloc[0]['Finish']
                    
                    df_filtered = df[
                        (df['Outline Level'].isin([1, 2])) &
                        (df['Start'] >= task_start) &
                        (df['Finish'] <= task_finish)
                    ]
        
        st.write("### Timeline for Tasks with Outline Level 1 and 2")
        fig, ax = plt.subplots(figsize=(18, 10))
        ax.set_facecolor('white')

        df_filtered = df_filtered.reset_index(drop=True)
        y_positions = range(len(df_filtered) - 1, -1, -1)
        
        bars = ax.barh(y_positions, df_filtered['Finish'] - df_filtered['Start'], left=df_filtered['Start'], color='green', height=0.6)
        
        for bar, (_, row) in zip(bars, df_filtered.iterrows()):
            start_text = row['Start'].strftime('%b %Y') if pd.notnull(row['Start']) else ""
            finish_text = row['Finish'].strftime('%b %Y') if pd.notnull(row['Finish']) else ""
            bar_center = bar.get_y() + bar.get_height() / 2
            
            ax.text(row['Start'], bar_center, start_text, verticalalignment='center', horizontalalignment='right', fontsize=11, color='black')
            ax.text(row['Finish'], bar_center, finish_text, verticalalignment='center', horizontalalignment='left', fontsize=11, color='black')
            ax.text(row['Start'] + (row['Finish'] - row['Start']) / 2, bar_center + 0.3, row['Name'], verticalalignment='bottom', horizontalalignment='center', fontsize=11, fontweight='bold', color='black')
        
        ax.set_xlabel("Date", fontsize=14, fontweight='bold')
        ax.set_ylabel("", fontsize=14, fontweight='bold')
        ax.set_title("Timeline of Tasks with Outline Level 1 and 2", fontsize=16, fontweight='bold')
        ax.set_yticks(y_positions)
        ax.set_yticklabels([])

        if selected_year == 'All':
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
            label="📥 Download Chart",
            data=buffer,
            file_name="timeline_chart.png",
            mime="image/png"
        )

def main():
    with st.sidebar:
        option = option_menu(
            "Menu",
            ["Project Information", "Timeline Visualization", "Human Resources"],
            icons=["house", "bar-chart", "people"],
            menu_icon="cast",
            default_index=0
        )
    
    if option == "Project Information":
        show_project_info()
    elif option == "Timeline Visualization":
        show_chart()
    elif option == "Human Resources":
        show_human_resources()

if __name__ == "__main__":
    main()
