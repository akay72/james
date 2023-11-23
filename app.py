import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import time 
import io
import csv

st.title('Yellow Pages Scraper')

search_terms = st.text_input('Enter search terms', value='', placeholder='Type search terms here...')
location = st.text_input('Enter location', value='', placeholder='Type location here...')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}




if st.button('Scrape Data'):

    if not search_terms or not location:
        # Display an error message
        st.error('Please fill in both fields.')
    else:

        with st.spinner('Scraping data... Please wait.'):
    

            session = requests.Session()
            session.headers.update(headers)

            domain = "https://www.yellowpages.com"
            # search_terms = "Christ Church Plano"
            # location = "Plano"

            # List to store scraped data
            business_data = []

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

        # Save the data to a CSV file
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Title', 'Phone', 'Website', 'Address', 'City', 'State', 'ZIP'])
        for item in business_data:
            writer.writerow(item)

        # Ensure we move back to the start of the StringIO object before reading it
        output.seek(0)
        csv_data = output.getvalue()  # Read the buffer's content as a string

        st.success('Scraping finished! Download your CSV below.')
        # Use the `st.download_button` to offer the CSV for download
        st.download_button(
            label="Download data as CSV",
            data=csv_data,
            file_name=f'{search_terms.replace(" ", "_")}_data.csv',
            mime='text/csv',
        )