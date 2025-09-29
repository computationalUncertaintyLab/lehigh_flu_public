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
from pages import landing_page

def main():
    """Main app with multi-page navigation."""
    
    # Sidebar navigation
    st.sidebar.title("🦠 Flu Forecast Dashboard")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Landing Page"]
    )
    
    # Route to appropriate page
    if page == "🏠 Landing Page":
        landing_page.show()

if __name__ == "__main__":
    main()

