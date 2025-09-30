import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Flu Forecast Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import page modules
from pages import detailed_look, quick_look

def main():
    """Main app with multi-page navigation."""
    
    # Sidebar navigation
    st.sidebar.title("🦠 Flu Forecast Dashboard")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["Quick Look","Detailed Look"]
    )
    
    # Route to appropriate page
    if page == "Detailed Look":
        detailed_look.show()
    elif page =="Quick Look":
        quick_look.show()

if __name__ == "__main__":
    main()

