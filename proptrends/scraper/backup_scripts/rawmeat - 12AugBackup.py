from scrapingbee import ScrapingBeeClient
import requests
from bs4 import BeautifulSoup, NavigableString, Comment
# import pandas as pd
import re
from pathlib import Path
from datetime import datetime, date, timedelta
from random import randint, uniform
from time import sleep
import winsound
from proptrends import db
from proptrends.models import Listing, Suburb_key, Proptype_key, Region_key, City_key
from proptrends.main.utils import convert_to_id
import os       # For file handling
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#======================================================================================================
# This function does the actual scraping using Selenium
# Currently only useful for searching by CSS_SELECTOR
# Returns html_content
#-----------------------------------------------------------------------------------------------------

# def selenaScrapes(url_to_scrape, selector):
#     # Encode the URL
#     encoded_url = urllib.parse.quote(url_to_scrape, safe="/:")
#     print("The encoded_url source is: ", encoded_url)

#     # Configure Chrome options
#     service = Service(executable_path="C:\Program Files (x86)\Google\Chrome\Application")
#     options = webdriver.ChromeOptions()
#     options.add_argument('--ignore-certificate-errors')
#     driver = webdriver.Chrome(service=service, options=options)

#     # Load the page
#     driver.get(encoded_url)

#     # Wait for the desired element to appear
#     wait = WebDriverWait(driver, 10)
#     # element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "lg:w-2/3")))
#     element = driver.find_element(By.CSS_SELECTOR, '[class*="lg:w-2/3 lg:pr-8"]')
#     print("The element is " + str(element.text))

#     # Extract the HTML content of the element
#     html_content = element.get_attribute("innerHTML")

#     # Close the browser
#     driver.quit()

#     return html_content

# #======================================================================================================
# # This function checks if the data retrieved is in the format that the database expects 
# # (Sometimes, a listing might be put up with fields in the wrong place i.e. Garage = "Freehold".
# # This is to prevent that error from throwing off the system.)
# # Returns the name's id
# #-----------------------------------------------------------------------------------------------------
# def check_isString(value):
#     # 
#     res = isinstance(value, str)
#     if isinstance(value, str): # carry on, otherwise 
#     # The table associates the name that we want to convert with int ids so that it's cheaper, and more efficient to store/call
#     name_exists = db.session.query(Table_key.query.filter(getattr(Table_key, name_in_table) == name_to_convert).exists()).scalar()
#     if name_exists:
#         # Get Name id


#======================================================================================================
# This function can be used to scrape data from an individual listing from RealEstate.co.nz
# Note: These are not generic functions. The pages are rather different so I haven't looked into
# abstracting these functions yet.
#-----------------------------------------------------------------------------------------------------

def scrape_indiv(mainurl,suburl,listid):
    now = datetime.now()
    print("#### Starting to scrape a new LISTING. Time now is :" + now.strftime("%H:%M:%S"))
    source = mainurl + suburl
    print("Listing id is: " + str(listid) + ". Getting the record...")
    listing = Listing.query.get_or_404(listid)
    print("The listing address is : " + listing.address)
    # Composing a unique file name based on the listing's address without spaces
    listing_name = str(re.sub('[\W+]', "", listing.address))  # Removing spaces and commas
    print("the listing_name is: " + str(listing_name) + " with datatype " + str(type(listing_name)))
    listing_filename = "tempIndivScrapings\\" + listing_name + ".html"
    print("The listing_filename that we're opening/creating is : " + str(listing_filename))

    # ==== LOCATION OF TEMP CREATED HTML FILES WITH INDIV LISTINGS' DATA ====
    # Get the current working directory
    current_dir = os.getcwd()
    # Define the relative path and filename of my HTML files (used to store temp data to reduce need to scrape
    temp_uniquelisting = os.path.join(current_dir, 'proptrends\scraper\output', listing_filename)

    print("The temp_uniquelisting that we're opening is : " + str(temp_uniquelisting))

    ## Save the scrape into a unique temp listing file so that we're absolutely sure that it's not scraped multiple times
    # Open temp html file to store the listing temporarily (prevents the need to scrape more than once)
    # Doing this because I'm unsure if python tends to run scripts each time on load
    # ==== DETERMINING IF THE LISTING HAS BEEN SCRAPED BEFORE (or has been created for testing)
    # OR IF IT NEEDS TO BE SCRAPED AGAIN ===
    check_file = os.path.isfile(temp_uniquelisting)
    if check_file:
        # File already exists! Continue!
        print("This file already exists. Proceed with opening file")
    else:
        # Scrape listing and create temp file
        #--- FOR SCRAPINGBEE ONLY
        # ## Get key from ScrapingBee - Needs to be changed every 200 scrapes or so
        # key = 'OHTOEP2LT6AHUOXL7IOJDL6U6MS6HFFULTAST41I3VZWQWSG5AOJI4QFYO6NTM7GTO6JLDGF4QHBXII9'
        # client = ScrapingBeeClient(api_key=key)
        # --- END FOR SCRAPINGBEE
        # encoded_url = urllib.parse.quote(source, safe="/:")
        # print("The encoded_url source is: ", encoded_url)

        # Configure Chrome options
        service = Service(executable_path="C:\Program Files (x86)\Google\Chrome\Application")
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(service=service, options=options)

        # Load the page
        driver.get(source)
        delay = uniform(12.03, 121.87)
        sleep(delay)
        print("Just checking that this is properly random " + str(delay))

        page = BeautifulSoup(driver.page_source, "html.parser")
        # page = BeautifulSoup(response.content, "html.parser")
        soup_string = page.prettify()
        with open(temp_uniquelisting, 'w', encoding="utf-8") as file:
            file.write(str(soup_string))
        file.close()
        driver.quit()

    # Now open the temp html file created
    with open(temp_uniquelisting, "r", encoding="utf-8") as f:
        page = BeautifulSoup(f, "html.parser")

    # GETTING THE LISTING DATE AND FORMATTING IT INTO A DATETIME FORMAT
    datemess = page.find_all(attrs={"data-test": "description__listed-date"})
    for tag in datemess:        # There should only be one description__listed-date, but just in case..
        tag_str = tag.text.strip().split()
        print(tag_str)
        try:
            year = tag_str[4]
            tag_date = tag_str[2] + " " + tag_str[3] + year
        except IndexError:
            tag_date = tag_str[2] + " " + tag_str[3] + " 2023"
        datet = datetime.strptime(tag_date, "%d %B %Y")
        print(datet)
        listing.list_date = datet


    # COLLECTING SUMMARY DATA (IF AVAILABLE) FOR THE LISTING
    # This is the portion of the page beside the icons
    # all_tags = page.find_all('span', class_='leading-[-1]')
    # all_tags = page.select("span.leading-none")
    all_tags = page.find_all(attrs={"data-test": "features-icons"})

    for tag in all_tags:
        # Regex pattern for all listings that require stripping of i.e. m2
        decimal_only_pattern = '(\d+)'
        # print('the tag is :' + str(tag))
        # find_proptype = tag.select_one('div[data-test="features-icons"] span[class="leading-[-1]"]')
        # if find_proptype:
        #     proptype = find_proptype.get_text()
        #     print(proptype)
        # find_br = tag.find('title', text='Bedroom')
        # print("find_br is " + str(find_br))
        # if find_br:
        #     br_qty = find_br.find_next('span').text.strip()
        #     print("There is a bedroom")
        #     print("Num bedrooms = " + str(br_qty))
        #     listing.beds = br_qty
        # find_bath = tag.find('title', text='Bathroom')
        # print("find_br is " + str(find_br))
        # if find_bath:
        #     bath_qty = find_bath.find_next('span').text.strip()
        #     print("There is a bathroom")
        #     print("Num baths = " + str(bath_qty))
        #     listing.bath = bath_qty
        find_floorarea = tag.find('title', text=re.compile(r'Floor area', re.IGNORECASE))
        print("find_floorarea is " + str(find_floorarea))
        if find_floorarea:
            floor = find_floorarea.find_next('span').text.strip()
            print("Floor before strip = " + str(floor))
            # Using Regex to retrieve only the integers
            if match := re.search(decimal_only_pattern, floor):
                floor = match.group(1)
            print("Got the floor area in datatype:" + str(type(floor)))
            print("Floor area = " + str(floor))
            try:
                listing.floor_m2 = int(floor)
            except ValueError as err:
                print("floor_m2 cannot be converted to int")
                listing.floor_m2 = None
        find_landarea = tag.find('title', text=re.compile(r'Land area', re.IGNORECASE))
        print("find_landarea is " + str(find_landarea))
        if find_landarea:
            land = find_landarea.find_next('span').text.strip()
            # Using Regex to retrieve only the integers
            if match := re.search(decimal_only_pattern, land):
                land = match.group(1)
            print("Got the land area in datatype:" + str(type(land)))
            print("land area = " + str(land))
            try:
                listing.land_m2 = int(land)
            except ValueError as err:
                print("land_m2 cannot be converted to int")
                listing.land_m2 = None

        find_garage = tag.find('title', text=re.compile(r'Garage', re.IGNORECASE))
        if find_garage:
            try:
                garage = int(find_garage.find_next('span').text.strip())
                print("Got the garage num!")
                print("garage num = " + str(garage))
                listing.garage = garage
            except ValueError as err:
                print("garage cannot be converted to int")
                listing.garage = None

        find_park = tag.find('title', text=re.compile(r'Covered park', re.IGNORECASE))
        if find_park:
            try:
                park = int(find_park.find_next('span').text.strip())
                print("Got the park num!")
                print("park num = " + str(park))
                listing.other_parks = park
            except ValueError as err:
                print("other_parks cannot be converted to int")
                listing.other_parks = None

        find_ensuite = tag.find('title', text=re.compile(r'Ensuite', re.IGNORECASE))
        if find_ensuite:
            ensuite = find_ensuite.find_next('span').text.strip()
            # Using Regex to retrieve only the integers
            if match := re.search(decimal_only_pattern, ensuite):
                ensuite = match.group(1)
            print("Got the ensuite num!")
            print("ensuite = " + str(ensuite) + " with datatype " + str(type(ensuite)))
            listing.ensuite = ensuite
        # is_section = tag.find('title', text=re.compile(r'Section', re.IGNORECASE))
        # if is_section:
        #     print("This is a section! ")
        #     section = is_section.find_next('span')
        #     if section:
        #         section = int(section.text.strip())
        #         print("Got the section num!")
        #         print("section = " + str(section))
        #     elif int(land)>0:
        #         section = int(land)
        #         print("section equated to land area = " + str(section))
        #     else:
        #         print("Section raw retrieved is :" + str(section))
        #         section = 0
        #     listing.prop_type = section
        find_titletype = tag.find('title', text=re.compile(r'Title type', re.IGNORECASE))
        if find_titletype:
            titletype = find_titletype.find_next('span').text.strip()
            print("Got the title type!")
            print("title = " + str(titletype))
            listing.title_type = titletype
        # is_multiprop = tag.find('title', text=re.compile(r'Multiple properties', re.IGNORECASE))
        # if is_multiprop:
        #     proptype = int(is_multiprop.find_next('span').text.strip())
        #     print("Got the prop type!")
        #     print("proptype = " + str(proptype))
        #     listing.prop_type = proptype
        db.session.commit()

        # if " garage" in tag_str or "covered park" in tag_str:
    #         gr = ''.join(filter(str.isdigit, tag_str))
    #         # print("Num gars: ", gr)
    #     if " other park" in tag_str:
    #         op = ''.join(filter(str.isdigit, tag_str))
    #     if " ensuite" in tag_str:
    #         ensuite = ''.join(filter(str.isdigit, tag_str))
        # tag_str = tag.text.strip()
        # print(tag_str)
        # # Property type is captured in main listings
        # if "Bedrooms" in tag_str or "Bedroom" in tag_str:
        #     br = tag.find_next_sibling('span').text.strip()
        #     print("There is a bedroom")
        #
        #     print("Num bedrooms = " + br)
    # if " bedrooms" in tag_str or " bedroom" in tag_str:
    #     if " bedrooms" in tag_str or " bedroom" in tag_str:
    #         br = ''.join(filter(str.isdigit, tag_str))
    #     if " bathrooms" in tag_str or " bathroom" in tag_str:
    #         bath = ''.join(filter(str.isdigit, tag_str))
    #     if "land area" in tag_str:
    #         landed = ''.join(filter(str.isdigit, tag_str))
    #         land = int(landed[:-1])
    #         print(land)
    #     if "floor area" in tag_str:
    #         print(tag_str)
    #         floored = ''.join(filter(str.isdigit, tag_str))
    #         floor = (int(floored[:-1]))
    #     if " garage" in tag_str or "covered park" in tag_str:
    #         gr = ''.join(filter(str.isdigit, tag_str))
    #         # print("Num gars: ", gr)
    #     if " other park" in tag_str:
    #         op = ''.join(filter(str.isdigit, tag_str))
    #     if " ensuite" in tag_str:
    #         ensuite = ''.join(filter(str.isdigit, tag_str))
    #
    #
    # full_desc = page.find_all('p', class_="")
    # for tag in full_desc:
    #     tag_str = tag.text.strip()
    #     if "% NBS" in tag_str:
    #         n = ''.join(filter(str.isdigit, tag_str))
    #         if n.isnumeric():
    #             nbs = int(''.join(filter(str.isdigit, tag_str)))
    #         else:
    #             nbs = -1
    #         # print("Num BR: ", nbs)
    #     if "%" in tag_str:
    #         print(tag_str)
    #         n = ''.join(filter(str.isdigit, tag_str))
    #         if n.isnumeric():
    #             nbs = int(n)
    #         else:
    #             nbs = -2
    #         print(nbs)
    #     if "body corp" in tag_str:
    #         print(tag_str)
    #         n = ''.join(filter(str.isdigit, tag_str))
    #         if n.isnumeric():
    #             bodycorp = int(n)
    #         else:
    #             bodycorp = -1
    #         print(bodycorp)
    #
    # # NEED TO FIND A WAY TO HANDLE BULLET POINTS
    #
    # # CAPTURING THE RATES AND TITLE TYPE (if available) UNDER THE
    # # PROPERTY FEATURES SECTION
    # all_features = page.find_all('li', class_="m-0 mt-1 leading-normal")
    # for tag in all_features:
    #     feature = tag.text.strip().split()
    #     if "Rates:" in feature:
    #         print(feature[1])
    #         rates = feature[1]
    #     if "Title" in feature:
    #         print(feature[2])
    #         title = feature[2]
    #     print(feature)
    #
    # # Capturing the property agent and agency details in case this helps future analysis
    # agent = page.find_all('div', class_="font-semibold text-black")
    # for tag in agent:
    #     agent_deets = tag.text.strip()
    #     agent_ret = agent_ret + agent_deets
    #     print("Agent to return: ", agent_ret)
    #
    # agency = page.find_all(attrs={"data-test": "agent-info__listing-agent-office"})
    # for tag in agency:
    #     agency_deets = tag.text.strip().split()
    #     if 'Harcourts' in agency_deets:
    #         agency_ret = "Harcourts"
    #     if "Tommy's" in agency_deets:
    #         agency_ret = "Tommy's"
    #     if 'Redcoats' in agency_deets:
    #         agency_ret = "Professionals"
    #     if 'Ray White' in agency_deets:
    #         agency_ret = "Ray White"
    #     if 'Lowe' in agency_deets:
    #         agency_ret = "Lowe & Co"
    #     if 'Property Brokers Limited' in agency_deets:
    #         agency_ret = "Property Brokers"
    #     if 'Freear' in agency_deets:
    #         agency_ret = "Craig Freear - Independent"
    #     if 'Mills Gibbon' in agency_deets:
    #         agency_ret = "Collective First National"
    #     print(agency_ret)
    winsound.Beep(340, 100)
    print("Listing scrape complete. Moving on to next listing in main page")
    # return br, bath, land, floor, gr, op, nbs, bodycorp, rates, title, listdate, ensuite, agent_ret, agency_ret

#======================================================================================================
# This function can be used to scrape any URL from RealEstate.co.nz with the main search page format
#-----------------------------------------------------------------------------------------------------
def scrape_main(mainurl, suburl, pagenum):
    now = datetime.now()
    print("#### Starting to scrape a new SUBURB PAGE. Time now is :" + now.strftime("%H:%M:%S"))
    add_count = 0
    source = mainurl + suburl
    # Encode the URL - To use later for scraping
    # encoded_url = urllib.parse.quote(source, safe="/:")
    # print("The encoded_url source is: ", encoded_url)

    # # We are going to store the page as a temp file so that we don't need to scrape it again.
    # # ==== DEFINING PLACES TO READ AND STORE DATA (Regardless of source) ====
    # # Get the current working directory
    current_dir = os.getcwd()
    print("the current_dir is " + str(current_dir))
    # # Define a relative path and filename of my HTML files (used to store temp data to reduce need to scrape
    beescraps = os.path.join(current_dir, 'proptrends\scraper\output', 'rawbeescraps.html')
    print("Beescraps are: " + str(beescraps))

    # Configure Chrome options
    service = Service(executable_path="C:\Program Files (x86)\Google\Chrome\Application")
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=service, options=options)

    # Load the page
    driver.get(source)

    # Quick first check for sanity
    delay = uniform(5.03, 10.26)
    sleep(delay)
    check_page = BeautifulSoup(driver.page_source, "html.parser")
    check_valid = check_page.find('h3', class_='text-xl.25 font-semibold')
    if check_valid:
        check_valid = check_valid.text.strip()
        if check_valid == "Nothing to see here":
            print(
                "Check_valid is returning: " + check_valid + ". This means the search result is empty. Abort and move to next suburb.")
            return "next_suburb"

    # If valid, then wait for the desired element to appear
    delay = uniform(13.03, 129.79)
    sleep(delay)

    page = BeautifulSoup(driver.page_source, "html.parser")





    # I *really* want to reduce the amount I'm scraping/storing. Let's find and remove all the CSS comment blocks
    css_comments = page.find_all(text=lambda text: isinstance(text, str) and "<!---->" in text)
    for css_comment in css_comments:
        css_comment.extract()

    # And meta content..
    metas = page.find_all('meta')
    for meta_tag in metas:
        meta_tag.decompose()
    for metacontent in page(text=lambda text: isinstance(text, Comment)):
        if "<meta" in str(metacontent):
            metacontent.extract()

    # And path content..
    paths = page.find_all('path')
    for path_tag in paths:
        path_tag.decompose()
    for path_content in page(text=lambda text: isinstance(text, Comment)):
        if "<path" in str(path_content):
            path_content.extract()

    # And img content..
    imgs = page.find_all('img')
    for img_tags in imgs:
        img_tags.decompose()
    for img_content in page(text=lambda text: isinstance(text, Comment)):
        if "<img" in str(img_content):
            img_content.extract()

    # Now removing <style> tag and its contents
    styles = page.find_all("style")
    for style_tag in styles:
        style_tag.decompose()

    # Same for <script> tag and its contents
    jscripts = page.find_all("script")
    for script_tag in jscripts:
        script_tag.decompose()

    # Same for <noscript> (Facebook) tag and its contents
    noscripts = page.find_all("noscript")
    for script_tag in noscripts:
        script_tag.decompose()

    # Finally remove <iframes>
    iframes = page.find_all("iframe")
    for frame_tag in iframes:
        frame_tag.decompose()

    print(" Rubbish stuff should now be extracted. Let's save this into rawbeescraps...")

   
    # writing over beescraps with the reduced page (no rubbish)
    soup_string = page.prettify()
    with open(beescraps, 'w', encoding="utf-8") as file:
        file.write(str(soup_string))
    file.close()
    # Close the browser
    driver.quit()

    # Now open the temp html file created
    with open(beescraps, "r", encoding="utf-8") as f:
        page = BeautifulSoup(f, "html.parser")

    # Do I need a while condition here?

    #####################################################
    # Stuff to grab the page's main information
    #-----------------------------------------------
    # First grabbing the region and "district" (or city)
    region = page.select_one('a[data-test="current-region"]').text.strip()
    print('Region:', region)
    district_city = page.select_one('a[data-test="current-district"]').text.strip()
    print('District/City:', district_city)

    # Convert the region and district_city strings to ids for cheaper/more efficient parsing
    region_id = convert_to_id(Region_key, 'region_name', region)
    city_id = convert_to_id(City_key, 'city_name', district_city)

    # ===== REMOVING RESPONSIVE ELEMENT DUPLICATES ======
    # This is necessary so that we aren't trying to process repeated copies of the same property
    # which are generated to accommodate different viewport sizes
    # -------------------------------------------------
    # Find all div elements with class swiper-side relative
    slides = page.find_all('div', class_='swiper-slide relative')

    # Remove all responsive attributes generated but the first slide
    for slide in slides[1:]:
        slide.decompose()

    # Get the reduced HTML
    reduced_html = str(page)
    # print("The reduced_html is :" + reduced_html)
    print(">>>>>>>>> Retrieved reduced_html >>>>>>>>")

    # Reducing the html further to only get tile__listing-details for one (main) page
    reduced_soup = BeautifulSoup(reduced_html, 'html.parser')

    ####################################################################
    # Checking how many listings there are on the "reduced_html" page
    #------------------------------------------------------------------
    total_page_listings = 0
    scraped_listings_on_page = 0
    new_scrapes = 0

    # First, quickly count how many listings there are on the page:
    for one_listing in reduced_soup.find_all('a', class_='text-slateGrey-500'):
        total_page_listings += 1
    print ("Total listings on this page are: " + str(total_page_listings))
    
    #########################################################################
    # Actual listing sorting begins
    #------------------------------------------------------------------

    for one_listing in reduced_soup.find_all('a', class_='text-slateGrey-500'):
        # Capture one_listing details as a soup object
        one_listing_file = (one_listing.prettify())
        one_listing_object = BeautifulSoup(one_listing_file, 'html.parser')

        # First check if listing exists
        # Capture listing's href (because that is unique)
        prop_href = one_listing['href']
        print("Do I get a url? :" + str(prop_href))

        # Check if the listing exists in the Listings db table
        listing_exists = db.session.query(Listing.query.filter_by(prop_url=prop_href).exists()).scalar()
        print("Does the listing exist? " + str(listing_exists))
        # If it exists, add count to "scraped list" and carry on
        if listing_exists:
            scraped_listings_on_page += 1  # add a count to the list
            print("Move along")
        else:
            # First increase the new_scrape count
            new_scrapes += 1
            scraped_listings_on_page += 1
            # COLLECT AND CREATE RECORD WITH ALL THE CONDENSED INFO FROM THE MAIN PAGE'S LISTING
            # Extract address using regex:
            address = one_listing_object.find('h3').text.strip()
            suburb_pattern = r'[^,]*$'
            remove_leadspace_pattern = r'^\s+'
            if match := re.search(suburb_pattern, address):
                suburb = match.group(0)
                # Then remove the leading space
                suburb = re.sub(remove_leadspace_pattern,'', suburb)

                print("the address is: " + address + " with suburb: " + suburb)

                # Convert the region and district_city strings to ids for cheaper/more efficient parsing
                suburb_id = convert_to_id(Suburb_key, 'suburb_name', suburb)

            # Extract price
            price_test1 = one_listing_object.find('h4', class_='h-6 truncate text-sm')
            price_test2 = one_listing_object.find('div', class_='font-semibold leading-tight')
            price_test3 = one_listing_object.select_one('div[data-test="price-display__price-method"]')
            if price_test1:
                price = price_test1.text.strip()
                print('Found Price:', price)
                if price=="Auction":
                    price = 1
                elif price=="Tender":
                    price = 2
                elif price=="Negotiation":
                    price = 3
                elif price=="POA":
                    price = 4
                elif price=="Deadline Sale":
                    price = 5
                else:
                    # Remove all , in pricing to get digits
                    try:
                        price = int(str(re.search('\d{1,},?\d{2,},?\d{3}', price).group(0)).replace(',',''))
                        print("the price is: " + str(price) + " with datatype " + str(type(price)))
                    except ValueError as err:
                        print("price cannot be converted to int")
                        price = None
            elif price_test2:
                price = price_test2.text.strip()
                print('Found Price using test2:', price)
                if price=="Auction":
                    price = 1
                elif price=="Tender":
                    price = 2
                elif price=="Negotiation":
                    price = 3
                elif price=="POA":
                    price = 4
                elif price=="Deadline Sale":
                    price = 5
                else:
                    try:
                        # Remove all , in pricing to get digits
                        price = int(str(re.search('\d{2,},?\d{3}', price).group(0)).replace(',', ''))
                        print("the test2 price is: " + str(price) + " with datatype " + str(type(price)))
                    except ValueError as err:
                        print("price cannot be converted to int")
                        price = None
            elif price_test3:
                price = price_test3.text.strip()
                print('Found Price using test2:', price)
                if price=="Auction":
                    price = 1
                elif price=="Tender":
                    price = 2
                elif price=="Negotiation":
                    price = 3
                elif price=="POA":
                    price = 4
                elif price=="Deadline Sale":
                    price = 5
                else:
                    try:
                        # Remove all , in pricing to get digits
                        price = int(str(re.search('\d{2,},?\d{3}', price).group(0)).replace(',', ''))
                        print("the test3 price is: " + str(price) + " with datatype " + str(type(price)))
                    except ValueError as err:
                        print("price cannot be converted to int")
                        price = None
            else:
                price = 9
                print("price not found for this listing")

            # Extract bedrooms
            bedrooms = one_listing_object.select_one('div[data-test="bedroom"]')
            if bedrooms:
                try:
                    bedrooms = int(bedrooms.text.strip())
                except ValueError as err:
                        print("bedrooms cannot be converted to int")
                        bedrooms = None
            # ind_proptype = tag.select_one('div[data-test="features-icons"] span[class="leading-[-1]"]')
            else:
                bedrooms = 0
            print('Bedrooms:', str(bedrooms))

            # Extract bathrooms
            bathrooms = one_listing_object.select_one('div[data-test="bathroom"]')
            if bathrooms:
                try:
                    bathrooms = int(bathrooms.text.strip())
                except ValueError:
                        print("bathrooms cannot be converted to int")
                        bathrooms = None
            else:
                bathrooms = 0
            print('Bathrooms:', str(bathrooms))

            # Extract property type
            property_type = one_listing_object.select_one('div[data-test="tile__search-result__content__features__divider"]')
            if property_type:
                property_type_str = property_type.text.strip()

            else:
                property_type_str = 0
            print('Property Type:', property_type_str)
            # Convert proptype to int ids so that it's cheaper, and more efficient to store/call
            proptype_id = convert_to_id(Proptype_key, "type", property_type_str)
            print("new proptype id is " + str(proptype_id))

            # ADDING ALL EXTRACTED INFO TO LISTING DB TABLE
            new_list = Listing(
                region=region_id,
                city=city_id,
                prop_url=prop_href,
                address=address,
                suburb=suburb_id,
                prop_type=proptype_id,
                list_price=price,
                beds=bedrooms,
                baths=bathrooms
            )
            db.session.add(new_list)
            db.session.commit()
            db.session.refresh(new_list)
            listing_id = new_list.id
            print("The listing id is :" + str(listing_id))
            delay = uniform(7.03, 111.87)
            sleep(delay)   # Adding a sleep time to make sure this doesn't flood the site with too many requests
            # Now go into the actual listing (using the prop_href) and scrape details of the actual listing
            values = scrape_indiv(mainurl, prop_href, listing_id)
            print(values)

        # Break out of for loop if the numbre of scraped listings are equal to the total listings on page
        print("Listings that we've scraped on this page are: " + str(scraped_listings_on_page))
        print("Total listings detected on this page are: " + str(total_page_listings))
        if scraped_listings_on_page == total_page_listings:
            # We have scraped this page. We can now either choose to:
            # 1) Move to the next page and carry on scraping (let's say if there are more than 10 new scrapes)
            # 2) If there are less than 10 new scrapes, we're done with this suburb. Move to the next suburb
            if new_scrapes >= 10:
                next_action = "next_page"
                winsound.Beep(1000, 100)
                winsound.Beep(2000, 100)
                winsound.Beep(1000, 100)
                return next_action
            else:
                next_action = "next_suburb"
                winsound.Beep(1000, 100)
                winsound.Beep(2000, 100)
                winsound.Beep(3000, 100)
                return next_action

    # If we reach this stage, something went wrong. Send error message.
    next_action = "Uh oh. Something bad happened"

    return "next_page"
