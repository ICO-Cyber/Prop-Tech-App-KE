
import pandas as pd
import streamlit as st
import numpy as np
# Set the page configuration

st.set_page_config(page_title="PropTech Dashboard", page_icon="🇰🇪", layout="wide")
st.title("🇰🇪 PropTech Dashboard")
st.markdown("An interactive dashboard for visualizing property technology data in Kenya.")
# Load data
@st.cache_data
def load_google_sheet():
    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgUQlOqS3lGhFkFNMd70uM37n7yszrwsMNKO6xkMzVIWGnVxSGCAttyIX8chSF2R-jSkUQce6NeEfP/pub?output=csv"
    try:
        df = pd.read_csv(google_sheet_url)
        
        #Clean price column(Remove commas and convert to number
        if 'Price' in df.columns:
            df['Price'] = df['Price'].replace({',': ''}, regex=True).astype(float)

            # Clean Size(Sqm) column (Remove commas and convert to number)
        if 'Size(Sqm)' in df.columns:
            df['Size(Sqm)'] = df['Size(Sqm)'].replace({',': ''}, regex=True).astype(float)

        #Add Calculate Price per Sqm column
        df['Price per Sqm'] = df['Price'] / df['Size(Sqm)']
        df['Price per Sqm'] = df['Price per Sqm'].round(0)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    
# Load the data
with st.spinner('Loading Nairobi properties...'):
    df = load_google_sheet()

    #Show data stats
if not df.empty:
    st.success(f"✅ Loaded {len(df)} properties from Google Sheets")

    #Quick stats
    col1, col2, col3,col4 = st.columns(4)
    with col1:
        st.metric("Total Properties", f"{len(df)}")

    with col2:
        avg_price = df['Price'].mean()
        st.metric("Average Price (KES)", f"{avg_price:,.0f}")
    with col3:
        avg_size = df['Size(Sqm)'].mean()
        st.metric("Average Size (Sqm)", f"{avg_size:,.0f}")
    with col4:
        avg_price_per_sqm = df['Price per Sqm'].mean()
        st.metric("Avg Price per Sqm (KES)", f"{avg_price_per_sqm:,.0f}")


else:
    st.warning("No data loaded. Using sample data.")
    # Create sample data for testing
    data = {
        'title': ['Property A', 'Property B', 'Property C'],
        'Price': [10000000, 15000000, 20000000],
        'Size(Sqm)': [100, 150, 200],
        'Location': ['Kilimani', 'Westlands', 'Kileleshwa']
        }   
    df = pd.DataFrame(data)

    # ---SIDEBAR FILTERS---
st.sidebar.header("🔍Filter Properties")

# Location filter
if 'Location' in df.columns:
    locations = sorted(df['Location'].dropna().unique())
    selected_locations = st.sidebar.multiselect(
        "Select Locations",
         locations,
        default=locations[:3] if len(locations) >= 3 else locations
        )
else:
    selected_locations = []

# Price range filter
if 'Price' in df.columns:
    min_price = int(df['Price'].min())
    max_price = int(df['Price'].max())
    price_range = st.sidebar.slider(
        "Select Price Range (KES)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=100000
    )
#Bedrooms filter
if 'Bedrooms' in df.columns:
    min_bedrooms = int(df['Bedrooms'].min())
    max_bedrooms = int(df['Bedrooms'].max())
    bedrooms_range = st.sidebar.slider(
        "Select Number of Bedrooms",
        min_value=min_bedrooms,
        max_value=max_bedrooms,
        value=(min_bedrooms, max_bedrooms),
        step=1
    )
# Size filter
if 'Size(Sqm)' in df.columns:
    min_size = int(df['Size(Sqm)'].min())
    max_size = int(df['Size(Sqm)'].max())
    size_range = st.sidebar.slider(
        "Select Size Range (Sqm)",
        min_value=min_size,
        max_value=max_size,
        value=(min_size, max_size),
        step=10
    )
else:
    size_range = (0, 10000)

# Apply filters to the dataframe
def filter_data(df):
    filtered_df = df.copy()
    if selected_locations:
        filtered_df = filtered_df[filtered_df['Location'].isin(selected_locations)]
    if 'Price' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Price'] >= price_range[0]) & (filtered_df['Price'] <= price_range[1])
        ]
    if 'Bedrooms' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Bedrooms'] >= bedrooms_range[0]) & (filtered_df['Bedrooms'] <= bedrooms_range[1])
        ]
    if 'Size(Sqm)' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Size(Sqm)'] >= size_range[0]) & (filtered_df['Size(Sqm)'] <= size_range[1])
        ]
    return filtered_df  

filtered_df = filter_data(df)

# ---DISPLAY RESULTS---
st.subheader(f"🏠 Found {len(filtered_df)} Filtered Properties")

if len(filtered_df) > 0:
    
    # Display as cards
    for index, row in filtered_df.iterrows():
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                if 'Image URL' in row and pd.notna(row['Image URL']):
                    st.image(row['Image URL'], width=150)
                else:
                    st.image("https://via.placeholder.com/150", width=150)
            with cols[1]:
                st.markdown(f"### {row['title'] if 'title' in row else 'No Title'}")
                st.markdown(f"**Location:** {row['Location'] if 'Location' in row else 'N/A'}")
                st.markdown(f"**Price:** KES {row['Price']:,.0f}" if 'Price' in row else "**Price:** N/A")
                st.markdown(f"**Size:** {row['Size(Sqm)']:,.0f} Sqm" if 'Size(Sqm)' in row else "**Size:** N/A")
                if 'Bedrooms' in row:
                    st.markdown(f"**Bedrooms:** {row['Bedrooms']}")
                if 'Price per Sqm' in row:
                    st.markdown(f"**Price per Sqm:** KES {row['Price per Sqm']:,.0f}")
            st.markdown("---")
            
            with col2:
                # Link to more details if available
                if 'Details URL' in row and pd.notna(row['Details URL']):
                    st.markdown(f"[More Details]({row['Details URL']})")

                # Contact button (dummy link for now)
                if 'Contact URL' in row and pd.notna(row['Contact URL']):
                    st.info(f"[Contact Seller]({row['Contact URL']})")

            st.divider()
else:
    st.warning("No properties match the selected filters. Please adjust your filters and try again.")


# ---DOWNLOAD DATA---
st.sidebar.header("💾 Download Data")
st.sidebar.subheader("  Export Data")    
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_properties.csv',
    mime='text/csv',
)

# ---ADD PROPERTY FORM---
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add New Property")
st.sidebar.markdown("Fill in the form below to add a new property listing.")
st.sidebar.text_input("Property Title", key="new_title")
st.sidebar.text_input("Location", key="new_location")
st.sidebar.number_input("Price", min_value=0, key="new_price")
st.sidebar.number_input("Size (SqM)", min_value=0, key="new_size")
st.sidebar.number_input("Bedrooms", min_value=0, key="new_bedrooms")
st.sidebar.text_input("Image URL (optional)", key="new_image_url")
st.sidebar.text_input("Details URL (optional)", key="new_details_url")
st.sidebar.text_input("Contact URL (optional)", key="new_contact_url")

if st.sidebar.button("Submit Property"):
   st.sidebar.success("✅ Property submitted successfully! (Note: This is a demo; data is not actually saved.)") 

# ---FOOTER---
st.markdown("---")
st.markdown("Developed by PropTech Enthusiasts 🇰🇪 | [GitHub Repository](https://github.com/yourusername/proptech-app)")

