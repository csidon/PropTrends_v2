from scrapingbee import ScrapingBeeClient
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
# import pandas as pd
import re
from pathlib import Path
from datetime import datetime, date, timedelta
from random import randint
from time import sleep
import winsound
from proptrends import db
from proptrends.models import Listing, Suburb_key, Proptype_key
import os       # For file handling
import urllib.parse

#======================================================================================================
# This function can be used to scrape data from an individual listing from RealEstate.co.nz
# Note: These are not generic functions. The pages are rather different so I haven't looked into
# abstracting these functions yet.
#-----------------------------------------------------------------------------------------------------

def scrape_indiv(mainurl,suburl,listid):
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
    temp_uniquelisting = os.path.join(current_dir, 'output', listing_filename)
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
        ## Get key from ScrapingBee - Needs to be changed every 200 scrapes or so
        key = 'OHTOEP2LT6AHUOXL7IOJDL6U6MS6HFFULTAST41I3VZWQWSG5AOJI4QFYO6NTM7GTO6JLDGF4QHBXII9'
        client = ScrapingBeeClient(api_key=key)
        response = client.get(source)
        page = BeautifulSoup(response.content, "html.parser")
        with open(temp_uniquelisting, 'w') as file:
            file.write(page)
        file.close()

    # Now open the temp html file created
    with open(temp_uniquelisting, "r") as f:
        page = BeautifulSoup(f, "html.parser")

    # GETTING THE LISTING DATE AND FORMATTING IT INTO A DATETIME FORMAT
    datemess = page.find_all(attrs={"data-test": "description__listed-date"})
    for tag in datemess:        # There should only be one description__listed-date, but just in case..
        tag_str = tag.text.strip().split()
        print(tag_str)
        tag_date = tag_str[2] + " " + tag_str[3] + " 2022"
        datet = datetime.strptime(tag_date, "%d %B %Y")
        print(datet)
        listing.list_date = datet


    # COLLECTING SUMMARY DATA (IF AVAILABLE) FOR THE LISTING
    # This is the portion of the page beside the icons
    # all_tags = page.find_all('span', class_='leading-[-1]')
    # all_tags = page.select("span.leading-none")
    all_tags = page.find_all(attrs={"data-test": "features-icons"})

    for tag in all_tags:
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
            floor = floor[:-2]
            print("Got the floor area!")
            print("Floor area = " + str(floor))
            listing.floor_m2 = floor
        find_landarea = tag.find('title', text=re.compile(r'Land area', re.IGNORECASE))
        print("find_landarea is " + str(find_landarea))
        if find_landarea:
            land = find_landarea.find_next('span').text.strip()
            land = land[:-2]
            print("Got the land area!")
            print("land area = " + str(land))
            listing.land_m2 = land
        find_garage = tag.find('title', text=re.compile(r'Garage', re.IGNORECASE))
        if find_garage:
            garage = int(find_garage.find_next('span').text.strip())
            print("Got the garage num!")
            print("garage area = " + str(garage))
            listing.garage = garage
        find_park = tag.find('title', text=re.compile(r'Covered park', re.IGNORECASE))
        if find_park:
            park = int(find_park.find_next('span').text.strip())
            print("Got the park num!")
            print("park num = " + str(park))
            listing.other_parks = park
        find_ensuite = tag.find('title', text=re.compile(r'Ensuite', re.IGNORECASE))
        if find_ensuite:
            ensuite = int(find_ensuite.find_next('span').text.strip())
            print("Got the ensuite num!")
            print("ensuite = " + str(ensuite))
            listing.ensuite = ensuite
        is_section = tag.find('title', text=re.compile(r'Section', re.IGNORECASE))
        if is_section:
            section = int(is_section.find_next('span').text.strip())
            print("Got the section num!")
            print("section = " + str(section))
            listing.prop_type = section
        find_titletype = tag.find('title', text=re.compile(r'Title type', re.IGNORECASE))
        if find_titletype:
            titletype = int(find_titletype.find_next('span').text.strip())
            print("Got the title type!")
            print("title = " + str(titletype))
            listing.title_type = titletype
        is_multiprop = tag.find('title', text=re.compile(r'Multiple properties', re.IGNORECASE))
        if is_multiprop:
            proptype = int(is_multiprop.find_next('span').text.strip())
            print("Got the prop type!")
            print("proptype = " + str(proptype))
            listing.prop_type = proptype
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
    add_count = 0
    source = mainurl + suburl
    encoded_url = urllib.parse.quote(source, safe="/:")
    print("The encoded_url source is: ", encoded_url)
    # We are going to store the page as a temp file so that we don't need to scrape it again.
    # ==== DEFINING PLACES TO READ AND STORE DATA (Regardless of source) ====
    # Get the current working directory
    current_dir = os.getcwd()
    # Define a relative path and filename of my HTML files (used to store temp data to reduce need to scrape
    temp_main_html = os.path.join(current_dir, 'output', 'temp_main_html.html')
    beescraps = os.path.join(current_dir, 'output', 'rawbeescraps.html')

    # # ==== SCRAPING PURE SOURCE CODE: LIVE - USING SCRAPING BEE ==========
    # Get key from ScrapingBee - Needs to be changed every 200 scrapes or so
    key = 'OHTOEP2LT6AHUOXL7IOJDL6U6MS6HFFULTAST41I3VZWQWSG5AOJI4QFYO6NTM7GTO6JLDGF4QHBXII9'
    client = ScrapingBeeClient(api_key=key)
    response = client.get(encoded_url, params={'block_ads': 'true'})
    page = BeautifulSoup(response.content, "html.parser")
    sleep(8)

    print('Response HTTP Status Code: ', response.status_code)
    print('Response HTTP Response Body: ', response.content)

    # # ===== USED TO CAPTURE PAGES' HTML FOR FORMATTING TESTING ===========
    # print("STARTING PAGE HTML.........")
    # print(page)
    # print("-------------------MAIN PAGE HTML ENDS HERE-------------------")
    # First save this data to a temp file
    soup_string = page.prettify()
    with open(beescraps, 'w', encoding="utf-8") as file:
        file.write(str(soup_string))
    file.close()
    print("Soup page written to bee scrapings and file closed")
    # Now reopen the raw file again
    with open(beescraps, "r") as f:
        rawsoup = BeautifulSoup(f, "html.parser")
    print("Retrieving soup from beescraps...")

    # # ==== GETTING PURE SOURCE CODE: FOR FORMATTING TESTING ONLY ==========
    # # Uncomment this and comment out the above code to test formatting via saved HTML pages
    # The test formatting page should contain the full page's source code, not just the outerhtml.
    # with open("C:/Users/Chris/Desktop/Yoobee/CS201_take2_PyWithIbrahim_part2/propTrends_v02/proptrends/scraper/testFormatMainsearchBerhampore.html", "r") as f:
    #     page = BeautifulSoup(f, "html.parser")


    # From the main listing page data, just get the source data for the listings.
    # Ignore everything else, and store that source data in a temp html file
    # so that there's no need to rescrape the site (for whatever reason)
    # maindiv = rawsoup.find('div', class_='lg:w-2/3 lg:pr-8')
    # outer_html = str(maindiv)
    outer_html = rawsoup.find('div', class_='lg:w-2/3 lg:pr-8')
    print("The outer html is :" + str(outer_html) + "with datatype " + str(type(outer_html)))
    #
    # # Open temp html file to store the outer_html (prevents the need to scrape more than once)
    # with open(temp_main_html, 'w') as file:
    #     file.write(outer_html)
    # file.close()
    # print("Soup page written to temp_main_html and file closed")
    #
    # # Create a BeautifulSoup object from the HTML content,
    # # making sure that it's reading from the temp html file
    # with open(temp_main_html, "r") as f:
    #     soup = BeautifulSoup(f, "html.parser")
    # print("Retrieving soup from temp_main_html...")

    # ===== REMOVING RESPONSIVE ELEMENT DUPLICATES ======
    # This is necessary so that we aren't trying to process repeated copies of the same property
    # which are generated to accommodate different viewport sizes
    # -------------------------------------------------
    # Find all div elements with class swiper-side relative
    slides = outer_html.find_all('div', class_='swiper-slide relative')

    # Remove all responsive attributes generated but the first slide
    for slide in slides[1:]:
        slide.decompose()

    # Get the reduced HTML
    reduced_html = str(outer_html)
    print("The reduced_html is :" + reduced_html)

    # Reducing the html further to only get tile__listing-details
    reduced_soup = BeautifulSoup(reduced_html, 'html.parser')

    for one_listing in reduced_soup.find_all('a', class_='text-slateGrey-500'):
        # Capture one_listing details as a soup object
        one_listing_file = (one_listing.prettify())
        # with open( r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\mainpageonelistonly.html',
        #     'a') as file:
        #     file.write(one_listing_file)
        #     file.close()
        # print(one_listing_file)
        # print("One_listing dataype is :" + str(type(one_listing)))
        # print("One_listing_file dataype is :" + str(type(one_listing_file)))
        one_listing_object = BeautifulSoup(one_listing_file, 'html.parser')

        # First check if listing exists
        # Capture listing's href (because that is unique)
        prop_href = one_listing['href']
        print("Do I get a url? :" + str(prop_href))

        # Check if the listing exists in the Listings db table
        listing_exists = db.session.query(Listing.query.filter_by(prop_url=prop_href).exists()).scalar()
        print("Does the listing exist? " + str(listing_exists))
        # If it exists, carry on?
        if listing_exists:
            print("Move along")
        else:
            # COLLECT AND CREATE RECORD WITH ALL THE CONDENSED INFO FROM THE MAIN PAGE'S LISTING
            # Extract address using regex:
            address = one_listing_object.find('h3').text.strip()
            suburb_pattern = '(?<=\s)(\w+)$'
            if match := re.search(suburb_pattern, address):
                suburb = match.group(1)
                print("the address is: " + address + " with suburb: " + suburb)

                # Check to see if suburb exists in suburb table
                # The suburb table associates suburbs with int ids so that it's cheaper, and more efficient to store/call
                suburb_exists = db.session.query(Suburb_key.query.filter_by(suburb_name=suburb).exists()).scalar()
                if suburb_exists:
                    # Get suburb id
                    suburb_id = Suburb_key.query.filter_by(suburb_name=suburb).first().id
                    print("existing suburb id is " + str(suburb_id))
                else:
                    # Create a new suburb record and grab the new record's id
                    new_suburb = Suburb_key(
                        suburb_name=suburb
                    )
                    db.session.add(new_suburb)
                    db.session.commit()
                    db.session.refresh(new_suburb)
                    suburb_id = new_suburb.id  # getting new suburb id
                    print("new suburb id is " + str(suburb_id))
            print("the address is : " + address)

            # Extract price
            price = one_listing_object.find('div', class_='font-semibold').text.strip()
            print('Price:', price)
            # Remove all , in pricing to get digits

            price = int(str(re.search('\d{2,},?\d{3}', price).group(0)).replace(',',''))
            print("the price is: " + str(price) + " with datatype " + str(type(price)))

            # Extract bedrooms
            bedrooms = int(one_listing_object.select_one('div[data-test="bedroom"]').text.strip())
            # ind_proptype = tag.select_one('div[data-test="features-icons"] span[class="leading-[-1]"]')
            print('Bedrooms:', str(bedrooms))

            # Extract bathrooms
            bathrooms = int(one_listing_object.select_one('div[data-test="bathroom"]').text.strip())
            print('Bathrooms:', str(bathrooms))

            # Extract property type
            property_type_str = one_listing_object.select_one('div[data-test="tile__search-result__content__features__divider"]').text.strip()
            print('Property Type:', property_type_str)
            # Check to see if the property_type exists in property_type table
            # The proptype_key associates types with int ids so that it's cheaper, and more efficient to store/call
            proptype_exists = db.session.query(Proptype_key.query.filter_by(type=property_type_str).exists()).scalar()
            if proptype_exists:
                # Get property type's id
                proptype_id = Proptype_key.query.filter_by(type=property_type_str).first().id
                print("existing proptype id is " + str(proptype_id))
            else:
                # Create a new property type record and grab the new record's id
                new_proptype = Proptype_key(
                    type=property_type_str
                )
                db.session.add(new_proptype)
                db.session.commit()
                db.session.refresh(new_proptype)
                proptype_id = new_proptype.id  # getting new suburb id
                print("new proptype id is " + str(proptype_id))

            # ADDING ALL EXTRACTED INFO TO LISTING DB TABLE
            new_list = Listing(
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
            sleep(randint(1, 3))  # Adding a sleep time to make sure this doesn't flood the site with too many requests
            # Now go into the actual listing (using the prop_href) and scrape details of the actual listing
            values = scrape_indiv(mainurl, prop_href, listing_id)
            print(values)
            add_count += 1
    file.close()
    winsound.Beep(1000, 100)
    winsound.Beep(2000, 100)
    winsound.Beep(3000, 100)

    return add_count
