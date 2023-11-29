import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
import time

if 'business_data' not in st.session_state:
    st.session_state['business_data'] = []




def contains_all_search_terms(title, search_term):
    # Convert to lowercase for case-insensitive comparison
    title_lower = title.lower()
    search_terms_lower = search_term.lower().split()

    # Check if all words in the search term are in the title
    return all(word in title_lower for word in search_terms_lower)

# Streamlit page configuration
st.set_page_config(page_title='Yellow Pages Scraper', layout='wide')

# st.markdown("""
#     <style>
#         /* Other styles ... */
        
#         /* Style for full width DataFrame */
#         .stDataFrame{
#             width: 100% !important;
#         }
#     </style>
# """, unsafe_allow_html=True)
# Custom CSS to inject into the Streamlit app
st.markdown("""
    <style>
        .instructions-container, .sidebar .sidebar-content {
            background-color: #fff2cc; /* Light yellow background */
            border-left: 5px solid #ffe600; /* Dark yellow border */
        }
        .instructions-container h3, .sidebar-header, h1.title {
            color: #d4a007; /* Yellow color similar to the border */
            font-weight: bold;
        }
        .instructions-container ul {
            list-style-type: none; /* Removes default bullets */
            padding: 0;
        }
        .instructions-container li::before {
            content: "•"; /* Custom bullet */
            color: #d4a007; /* Yellow bullet */
            font-weight: bold; /* Bold bullet */
            display: inline-block; 
            width: 1em; /* Fixed width for alignment */
            margin-left: -1em; /* Negative margin for indent */
        }
        .instructions-container {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# App title with custom style
with st.sidebar:
    # ... [existing inputs and scrape button] ...
    # Add radio buttons for result type
    result_type = st.radio(
        "Choose Result Type",
        ('Get All Results', 'Get Similar Results')
    )

# Sidebar for inputs and scrape button
with st.sidebar:
    st.markdown('<h1 class="title">Yellow Pages Scraper</h1>', unsafe_allow_html=True)
    search_terms = st.text_input('Enter search terms', value='', placeholder='Type search terms here...')
    location = st.text_input('Enter location', value='', placeholder='Type location here...')
    scrape_button = st.button('Scrape Data')

    # Sidebar instructions with custom style
st.markdown('<h2 class="sidebar-header">How to Use This App 📖</h2>', unsafe_allow_html=True)
info_expander = st.expander('👉 Click here for instructions')
with info_expander:
    st.markdown(
        """
        <div class="instructions-container">
            <h3>Easy Steps to Get Started:</h3>
            <ul>
                <li><strong>Enter Search Details:</strong> Fill in the 'Enter search terms' and 'Enter location' fields with your desired business search criteria.</li>
                <li><strong>Choose Result Type:</strong> Select 'Get All Results' for a comprehensive search or 'Get Similar Results' for a more focused, similarity-based search.</li>
                <li><strong>Start Scraping:</strong> Hit the 'Scrape Data' button to initiate the search process.</li>
                <li><strong>View Results:</strong> After scraping, the results will be displayed on the main page. The content will depend on your chosen result type.</li>
                <li><strong>Download Data:</strong> You can download the scraped data in CSV format by clicking the 'Download data as CSV' button.</li>
                <li><strong>Review Latest Data:</strong> The most recent search results will always be visible on the main page for your review.</li>
            </ul>
            <p>This app helps you scrape business information from Yellow Pages, providing details like business names, phone numbers, and addresses. Choose between a broad or targeted search approach based on your needs.</p>
        </div>
        """,
        unsafe_allow_html=True
    )



# Main page placeholder for displaying data
data_display = st.empty()

# ... [Rest of your code, including scraping logic and functions, remains unchanged] ...

# To run this Streamlit app, save the code in a Python file (e.g., app.py) and run it using the command: streamlit run app.py
def scrape_yellow_pages(search_terms, location):
    # ... [Your scraping logic here] ...
    # Return a list of tuples with the scraped dat
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    business_data = []


    if not search_terms or not location:
        # Display an error message
        st.warning('Please fill in both search terms and location.')
        return business_data
    else:

        
    

        session = requests.Session()
        session.headers.update(headers)

        domain = "https://www.yellowpages.com"
        # search_terms = "Christ Church Plano"
        # location = "Plano"

        # List to store scraped data
        
        # Start at page 1 and increment for each loop
        page = 1

        while True:
            # Update the base URL to include the page number
            base_url = f"https://www.yellowpages.com/search?search_terms={search_terms}&geo_location_terms={location}&page={page}"
            
            response = session.get(base_url)
            time.sleep(2)
            
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                results = soup.find_all(class_="result")

                
                
                # If no results on the page, break the loop
                if not results:
                    print(f"No results on page {page}. Ending pagination.")
                    break

                for result in results:
                    title = phone_number = full_address = website_url= city = state = zip_code = None
                    try:
                        url_section = result.find("div", class_="info-section info-primary")
                        secondary_section = result.find("div", class_="info-section info-secondary") 
                        
                        title_tag = url_section.find("a", class_="business-name")
                        title = title_tag.text.strip() if title_tag else None

                        phone_tag = secondary_section.find("div", class_="phones phone primary")
                        phone_number = phone_tag.text.strip() if phone_tag else None

                        address_tag = secondary_section.find("div", class_="street-address")
                        full_address = address_tag.text.strip() if address_tag else None

                        try:
                            website_tag = url_section.find("a", class_="track-visit-website")
                            website_url = website_tag['href'] if website_tag else None
                        except Exception as e:
                            website_url=None

                        locality=secondary_section.find('div',class_='locality')
                        if locality:
                            locality_text = locality.text.strip()
                            # Assuming the format is always "City, State ZIP"
                            locality_parts = locality_text.split(',')
                            city = locality_parts[0].strip() if len(locality_parts) > 0 else None
                            state_and_zip = locality_parts[1].strip().split(' ') if len(locality_parts) > 1 else [None, None]
                            state = state_and_zip[0] if len(state_and_zip) > 0 else None
                            zip_code = state_and_zip[1] if len(state_and_zip) > 1 else None
                    

                        print(title)

                        # Check if all details are found; if not, go to the detail page
                        if not (title and phone_number and full_address):
                            link = url_section.find("a", class_="business-name")['href']
                            full_url = urllib.parse.urljoin(domain, link)
                            description_response = session.get(full_url)
                            if description_response.status_code == 200:
                                description_content = description_response.text
                                description_soup = BeautifulSoup(description_content, 'html.parser')
                                description_results = description_soup.find("div", id="listing-card")
                                if description_results:
                                    if not title:
                                        try:
                                            title_element = description_results.find("h1", class_="business-name")
                                            title = title_element.text.strip() if title_element else None
                                        except:
                                            title = None          
                                            
                                    if not phone_number:
                                        try:
                                            phone_element = description_results.find("a", class_="phone")
                                            phone_number = phone_element.text.strip() if phone_element else None
                                        except:
                                            phone_number=None

                                    if not full_address:
                                        try:
                                            address_element = description_results.find("span", class_="address").find('span')
                                            full_address = address_element.text.strip() if address_element else None
                                        except:
                                            full_address=None  
                                    if not city or state or zip_code:  
                                        
                                        try:
                                            address_tag = description_results.find("span", class_="address")
                                            if address_tag:
                                                # Extract the inner text from the first span which is the street address
                                                street_address_span = address_tag.find("span")
                                                if street_address_span:
                                                    street_address = street_address_span.text.strip()
                                                    # Replace the street address with an empty string to get the city, state, ZIP
                                                    locality_info = address_tag.text.replace(street_address, '').strip()
                                                else:
                                                    locality_info = address_tag.text.strip()
                                                
                                                # Assuming the format is always "City, State ZIP"
                                                locality_parts = locality_info.split(',')
                                                city = locality_parts[0].strip() if len(locality_parts) > 0 else None
                                                state_and_zip = locality_parts[1].strip().split(' ') if len(locality_parts) > 1 else [None, None]
                                                state = state_and_zip[0] if len(state_and_zip) > 0 else None
                                                zip_code = state_and_zip[1] if len(state_and_zip) > 1 else None
                                        except Exception as e:
                                            print(f"An error occurred while trying to get the locality information: {e}")
                                            city = None
                                            state = None
                                            zip_code = None

                                    print("Getting from description page", title)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    
                    # Append the data to the list only once per result
                    business_data.append((title, phone_number, website_url,full_address, city, state, zip_code))
                
                print(f"Finished scraping page {page}.")
                page += 1
            else:
                print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                break

    return business_data

def scrape_yellow_pages_similer(search_terms, location):
    # ... [Your scraping logic here] ...
    # Return a list of tuples with the scraped dat
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    business_data = []


    if not search_terms or not location:
        # Display an error message
        st.warning('Please fill in both search terms and location.')
        return business_data
    else:

        
    

        session = requests.Session()
        session.headers.update(headers)

        domain = "https://www.yellowpages.com"
        # search_terms = "Christ Church Plano"
        # location = "Plano"

        # List to store scraped data
        
        # Start at page 1 and increment for each loop
        page = 1

        while True:
            # Update the base URL to include the page number
            base_url = f"https://www.yellowpages.com/search?search_terms={search_terms}&geo_location_terms={location}&page={page}"
            
            response = session.get(base_url)
            time.sleep(2)
            
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                results = soup.find_all(class_="result")

                
                
                # If no results on the page, break the loop
                if not results:
                    print(f"No results on page {page}. Ending pagination.")
                    break

                for result in results:
                    title = phone_number = full_address = website_url= city = state = zip_code = None
                    try:
                        url_section = result.find("div", class_="info-section info-primary")
                        secondary_section = result.find("div", class_="info-section info-secondary") 
                        
                        title_tag = url_section.find("a", class_="business-name")
                        title = title_tag.text.strip() if title_tag else None

                        phone_tag = secondary_section.find("div", class_="phones phone primary")
                        phone_number = phone_tag.text.strip() if phone_tag else None

                        address_tag = secondary_section.find("div", class_="street-address")
                        full_address = address_tag.text.strip() if address_tag else None

                        try:
                            website_tag = url_section.find("a", class_="track-visit-website")
                            website_url = website_tag['href'] if website_tag else None
                        except Exception as e:
                            website_url=None

                        locality=secondary_section.find('div',class_='locality')
                        if locality:
                            locality_text = locality.text.strip()
                            # Assuming the format is always "City, State ZIP"
                            locality_parts = locality_text.split(',')
                            city = locality_parts[0].strip() if len(locality_parts) > 0 else None
                            state_and_zip = locality_parts[1].strip().split(' ') if len(locality_parts) > 1 else [None, None]
                            state = state_and_zip[0] if len(state_and_zip) > 0 else None
                            zip_code = state_and_zip[1] if len(state_and_zip) > 1 else None
                    

                        print(title)

                        # Check if all details are found; if not, go to the detail page
                        if not (title and phone_number and full_address):
                            link = url_section.find("a", class_="business-name")['href']
                            full_url = urllib.parse.urljoin(domain, link)
                            description_response = session.get(full_url)
                            if description_response.status_code == 200:
                                description_content = description_response.text
                                description_soup = BeautifulSoup(description_content, 'html.parser')
                                description_results = description_soup.find("div", id="listing-card")
                                if description_results:
                                    if not title:
                                        try:
                                            title_element = description_results.find("h1", class_="business-name")
                                            title = title_element.text.strip() if title_element else None
                                        except:
                                            title = None          
                                            
                                    if not phone_number:
                                        try:
                                            phone_element = description_results.find("a", class_="phone")
                                            phone_number = phone_element.text.strip() if phone_element else None
                                        except:
                                            phone_number=None

                                    if not full_address:
                                        try:
                                            address_element = description_results.find("span", class_="address").find('span')
                                            full_address = address_element.text.strip() if address_element else None
                                        except:
                                            full_address=None  
                                    if not city or state or zip_code:  
                                        
                                        try:
                                            address_tag = description_results.find("span", class_="address")
                                            if address_tag:
                                                # Extract the inner text from the first span which is the street address
                                                street_address_span = address_tag.find("span")
                                                if street_address_span:
                                                    street_address = street_address_span.text.strip()
                                                    # Replace the street address with an empty string to get the city, state, ZIP
                                                    locality_info = address_tag.text.replace(street_address, '').strip()
                                                else:
                                                    locality_info = address_tag.text.strip()
                                                
                                                # Assuming the format is always "City, State ZIP"
                                                locality_parts = locality_info.split(',')
                                                city = locality_parts[0].strip() if len(locality_parts) > 0 else None
                                                state_and_zip = locality_parts[1].strip().split(' ') if len(locality_parts) > 1 else [None, None]
                                                state = state_and_zip[0] if len(state_and_zip) > 0 else None
                                                zip_code = state_and_zip[1] if len(state_and_zip) > 1 else None
                                        except Exception as e:
                                            print(f"An error occurred while trying to get the locality information: {e}")
                                            city = None
                                            state = None
                                            zip_code = None

                                    print("Getting from description page", title)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    
                    # Append the data to the list only once per result
                    if contains_all_search_terms(title, search_terms):
                        business_data.append((title, phone_number, website_url, full_address, city, state, zip_code))
                
                print(f"Finished scraping page {page}.")
                page += 1
            else:
                print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                break

    return business_data



# Function to download data as CSV
def download_data(business_data):
    # Convert the scraped data to a pandas DataFrame
    df = pd.DataFrame(business_data, columns=['Title', 'Phone', 'Website', 'Address', 'City', 'State', 'ZIP'])

    # Convert the DataFrame to CSV
    csv_data = df.to_csv(index=False).encode('utf-8')

    # Create a download button in the sidebar
    with st.sidebar:
        st.download_button(
            label="Download data as CSV",
            data=csv_data,
            file_name=f'{search_terms.replace(" ", "_")}_data.csv',
            mime='text/csv',
        )

    # Display the DataFrame on the main page
    # data_display.dataframe(df)

    st.session_state['business_data'] = business_data

    # Display the DataFrame on the main page
    if business_data:
        df = pd.DataFrame(business_data, columns=['Title', 'Phone', 'Website', 'Address', 'City', 'State', 'ZIP'])
        df.index = range(1, len(df) + 1)
        data_display.dataframe(df,width=5000)

# If the scrape button is clicked
if scrape_button:
    
    with st.spinner('Scraping data... Please wait.'):
        # Call the scrape function
        if result_type == 'Get All Results':
            scraped_data = scrape_yellow_pages(search_terms, location)
        elif result_type == 'Get Similar Results':
           scraped_data= scrape_yellow_pages_similer(search_terms, location)

        # Check if data was returned from the scrape function
        if scraped_data:
            st.success('Scraping finished!')
            download_data(scraped_data)
        else:
            st.error('No data was scraped. Please check your input and try again.')

# To run this Streamlit app, save the code in a Python file (e.g., app.py) and run it using the command: streamlit run app.py
if st.session_state['business_data']:
    df = pd.DataFrame(st.session_state['business_data'], columns=['Title', 'Phone', 'Website', 'Address', 'City', 'State', 'ZIP'])
    df.index = range(1, len(df) + 1)
    data_display.dataframe(df,width=5000)
