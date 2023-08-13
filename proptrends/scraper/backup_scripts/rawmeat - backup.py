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
from proptrends.models import Listing, Suburb_key

#======================================================================================================
# This function can be used to scrape data from an individual listing from RealEstate.co.nz
# Note: These are not generic functions. The pages are rather different so I haven't looked into
# abstracting these functions yet.
#-----------------------------------------------------------------------------------------------------

def scrape_indiv(mainurl,suburl,listid):
    source = mainurl + suburl
    print("Listing id is: " + str(listid) + ". Getting the record...")
    listing = Listing.query.get_or_404(listid)

    # # Get key from ScrapingBee - Needs to be changed every 200 scrapes or so
    # key = 'OHTOEP2LT6AHUOXL7IOJDL6U6MS6HFFULTAST41I3VZWQWSG5AOJI4QFYO6NTM7GTO6JLDGF4QHBXII9'
    # client = ScrapingBeeClient(api_key=key)
    # response = client.get(source)
    # page = BeautifulSoup(response.content, "html.parser")
    # print(page)

    #=== FOR FORMATTING TESTING ONLY ==========
    # To reduce number of scrapes on site (and number of credits used), comment out print(page)
    # above and run script, then copy resulting HTML into a html file.
    # Comment out section above and uncomment the 2 lines below.
    #------
    with open("C:/Users/Chris/Desktop/Yoobee/CS201_take2_PyWithIbrahim_part2/propTrends_v02/proptrends/scraper/testFormatIndivListing.html", "r") as f:
        page = BeautifulSoup(f, "html.parser")


    # DECLARING VARIABLES TO COLLECT
    listdate, br, bath, land, floor, gr, op, nbs, bodycorp, rates, title, ensuite = "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    agent_ret, agency_ret = "", ""


    # GETTING THE LISTING DATE AND FORMATTING IT INTO A DATETIME FORMAT
    datemess = page.find_all(attrs={"data-test": "description__listed-date"})
    for tag in datemess:        # There should only be one description__listed-date, but just in case..
        tag_str = tag.text.strip().split()
        print(tag_str)
        tag_date = tag_str[2] + " " + tag_str[3] + " 2022"
        datet = datetime.strptime(tag_date, "%d %B %Y")
        print(datet)
        # db.session.add(listing)
        strlistdate = datet.strftime("%Y-%m-%d")
        listdate = datetime.strptime(strlistdate, "%Y-%m-%d")
        # # Checking if the listing date is from 2021
        # if tag_str[-1] == "2021":
        #     # First get and format the date
        #     tag_date = tag_str[2] + " " + tag_str[3] + " 2021"
        #     datet = datetime.strptime(tag_date, "%d %B %Y")
        #     strlistdate = datet.strftime("%Y-%m-%d")
        #     listdate = datetime.strptime(strlistdate, "%Y-%m-%d")
        # else:
        #     tag_date = tag_str[2] + " " + tag_str[3] + " 2022"
        #     datet = datetime.strptime(tag_date, "%d %B %Y")
        #     strlistdate = datet.strftime("%Y-%m-%d")
        #     listdate = datetime.strptime(strlistdate, "%Y-%m-%d")
        # # print("The listdate is:", listdate, " type ", type(listdate))
        listing.list_date = datet


    # COLLECTING SUMMARY DATA (IF AVAILABLE) FOR THE LISTING
    # This is the portion of the page beside the icons
    # all_tags = page.find_all('span', class_='leading-[-1]')
    # all_tags = page.select("span.leading-none")
    all_tags = page.find_all(attrs={"data-test": "features-icons"})

    for tag in all_tags:
        print('the tag is :' + str(tag))
        find_proptype = tag.select_one('div[data-test="features-icons"] span[class="leading-[-1]"]')
        if find_proptype:
            proptype = find_proptype.get_text()
            print(proptype)
        find_br = tag.find('title', text='Bedroom')
        print("find_br is " + str(find_br))
        if find_br:
            br_qty = find_br.find_next('span').text.strip()
            print("There is a bedroom")
            print("Num bedrooms = " + str(br_qty))
            listing.beds = br_qty
        find_bath = tag.find('title', text='Bathroom')
        print("find_br is " + str(find_br))
        if find_bath:
            bath_qty = find_bath.find_next('span').text.strip()
            print("There is a bathroom")
            print("Num baths = " + str(bath_qty))
            listing.bath = bath_qty
        find_floorarea = tag.find('title', text='Floor area')
        print("find_br is " + str(find_br))
        if find_floorarea:
            floor = find_floorarea.find_next('span').text.strip()
            floor = floor[:-2]
            print("Got the floor area!")
            print("Floor area = " + str(floor))
            listing.floor_m2 = floor
        db.session.commit()



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
    # winsound.Beep(340, 100)
    # return br, bath, land, floor, gr, op, nbs, bodycorp, rates, title, listdate, ensuite, agent_ret, agency_ret

#======================================================================================================
# This function can be used to scrape any URL from RealEstate.co.nz with the main search page format
#-----------------------------------------------------------------------------------------------------
def scrape_main(mainurl, suburl, pagenum):
    source = mainurl + suburl
    # print("The source is: ", source)
    # # Get key from ScrapingBee - Needs to be changed every 200 scrapes or so
    # key = 'OHTOEP2LT6AHUOXL7IOJDL6U6MS6HFFULTAST41I3VZWQWSG5AOJI4QFYO6NTM7GTO6JLDGF4QHBXII9'
    # client = ScrapingBeeClient(api_key=key)
    # response = client.get(source)
    # page = BeautifulSoup(response.content, "html.parser")
    #
    # # ===== USED TO CAPTURE PAGES' HTML FOR FORMATTING TESTING ===========
    # print("STARTING PAGE HTML.........")
    # print(page)
    # print("-------------------MAIN PAGE HTML ENDS HERE-------------------")

    # # ==== FOR FORMATTING TESTING ONLY ==========
    # # Uncomment this and comment out the above code to test formatting via saved HTML pages
    with open("C:/Users/Chris/Desktop/Yoobee/CS201_take2_PyWithIbrahim_part2/propTrends_v02/proptrends/scraper/testFormatMainsearchBerhampore.html", "r") as f:
        page = BeautifulSoup(f, "html.parser")


    # ==== PATHS TO READ AND STORE DATA ====
    # The script reads the data from readdata_path and stores it into a DataFrame (data_in_store)
    # It compares the unique property URLs with the scraped data.
    # If the URL doesn't exist, it continues to get information about the property
    # and stores this into an add_output DataFrame that writes to the datastore_path.
    # Finally, it merges both dataframes and writes data back to readdata_path
    # readdata_path = "propertyDataKapiti.csv"
    # datastore_path = "propertyDataNewTest.csv"
    # backup_path = "scrapeInProgressData.csv"
    # data_in_store = pd.read_csv(readdata_path, parse_dates=['ListDate'], dayfirst=True)
    # print(data_in_store)

    # GETTING ALL UNIQUE PROPERTY URLS THAT HAVE ALREADY BEEN SCRAPED AND STORING
    # TO A LIST FOR COMPARISON (Prevents double-scraping)
    # listings_href = data_in_store['PropURL'].tolist()

    # DECLARING VARIABLES TO CAPTURE AND ADD
    add_date, add_href, add_br, add_bath, add_land, add_floor = [], [], [], [], [], []
    add_gr, add_op, add_nbs, add_bc, add_rates, add_title = [], [], [], [], [], []
    add_types, add_size, add_address, add_price, add_ensuite = [], [], [], [], []
    add_agents, add_agency = [], []

    # # Logs for debugging output
    # print("Listings href list is: ", listings_href)
    # total_listings = len(listings_href)
    # print("Total listings in store: ", total_listings)

    add_count = 0


    maindiv = page.find('div', class_='lg:w-2/3 lg:pr-8')
    outer_html = str(maindiv)

    with open(r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\rubbishsorting.html', 'w') as file:
        file.write(outer_html)
    file.close()

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(outer_html, 'html.parser')

    # Find all div elements with class swiper-side relative
    slides = soup.find_all('div', class_='swiper-slide relative')

    # Remove all responsive attributes generated but the first slide
    for slide in slides[1:]:
        slide.decompose()

    # Get the reduced HTML
    reduced_html = str(soup)
    #
    # print(reduced_html)


    # with open(r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\rubbishsortingshrink.html', 'w') as file:
    #     file.write(reduced_html)
    # file.close()

    # Reducing the html further to only get tile__listing-details
    reduced_soup = BeautifulSoup(reduced_html, 'html.parser')

    for one_listing in reduced_soup.find_all('a', class_='text-slateGrey-500'):
        # Capture one_listing details
        one_listing_file = (one_listing.prettify())
        with open( r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\mainpageonelistonly.html',
            'a') as file:
            file.write(one_listing_file)
            file.close()
        print(one_listing_file)
        print("One_listing dataype is :" + str(type(one_listing)))
        print("One_listing_file dataype is :" + str(type(one_listing_file)))
        one_listing_object = BeautifulSoup(one_listing_file, 'html.parser')

        # First check if listing exists
        # Capture listing's href (because that is unique)
        prop_href = one_listing['href']
        print("Do I get a url? :" + str(prop_href))

        # Extract address:
        address = one_listing_object.find('h3').text.strip()
        suburb_pattern = '(?<=\s)(\w+)$'
        if match := re.search(suburb_pattern, address):
            suburb = match.group(1)
            print("the address is: " + suburb)

            # Check to see if suburb exists in suburb table
            suburb_exists = db.session.query(Suburb_key.query.filter_by(suburb_name=suburb).exists()).scalar()
            if suburb_exists:
                # Get suburb id
                suburb_id = Suburb_key.query.filter_by(suburb_name=suburb).first().id
                print("existing suburb id is " + str(suburb_id))
            else:
                # Create a new record
                new_suburb = Suburb_key(
                    suburb_name=suburb
                )
                db.session.add(new_suburb)
                db.session.commit()
                suburb_id = db.session.refresh(new_suburb)  # getting new suburb id
                print("new suburb id is " + str(suburb_id))
        print("the address is : " + address)

        # Extract price
        price = one_listing_object.find('div', class_='font-semibold').text.strip()
        print('Price:', price)
        # Remove all , in pricing to get digits

        price = int(str(re.search('\d{2,},?\d{3}', price).group(0)).replace(',',''))
        print("the price is: " + str(price) + " with datatype " + str(type(price)))

        # Extract bedrooms
        bedrooms = one_listing_object.select_one('div[data-test="bedroom"]').text.strip()
        # ind_proptype = tag.select_one('div[data-test="features-icons"] span[class="leading-[-1]"]')
        print('Bedrooms:', bedrooms)

        # Extract bathrooms
        bathrooms = one_listing_object.select_one('div[data-test="bathroom"]').text.strip()
        print('Bathrooms:', bathrooms)

        # Extract property type
        property_type = one_listing_object.select_one('div[data-test="tile__search-result__content__features__divider"]').text.strip()
        print('Property Type:', property_type)

        # Now to add this to the database. Check if listing exists

        listing_exists = db.session.query(Listing.query.filter_by(prop_url=prop_href).exists()).scalar()
        print("Does the listing exist? " + str(listing_exists))
        # If it exists, carry on?
        if listing_exists:
            print("Move along")
        else:

            # # Find the right block to get the house type
            # proptype = i.find_next('data-test').text.strip()
            # print("Did I get the proptype? :" + str(proptype))
            new_list = Listing(
                prop_url=prop_href,
                address=address,
                suburb=suburb_id
            )
            db.session.add(new_list)
            db.session.commit()
            db.session.refresh(new_list)
            listing_id = new_list.id
            print("The listing id is :" + str(listing_id))
            sleep(randint(1, 3))  # Adding a sleep time to make sure this doesn't flood the site with too many requests
            values = scrape_indiv(mainurl, prop_href, listing_id)
            print(values)


        # if isinstance(one_tile, NavigableString):
        #     continue
        # if isinstance(one_tile, Tag):
        #     # Extract listing_details_only
        #     main_details = one_tile.prettify()
        #     print(main_details)
        #     # Search for bedroom and bathroom details
        #     reduced_soup
        #     with open(r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\mainpagelistdetailsonly.html', 'a') as file:
        #         file.write(listing_details_only)
        #     file.close()


    # # Split srcset value into individual URLs
    # urls = srcset.split(',')
    #
    # # Extract the URL with the largest width
    # largest_url = max(urls, key=lambda url: int(re.search(r'(\d+)w', url).group(1)))
    #
    # # Extract the URL itself from the srcset value
    # final_url = re.search(r'^(.+)\s\d+w$', largest_url).group(1)
    #
    # print(final_url)
    #
    # with open(r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\rubbishsortingshrinkfinalURL.html', 'w') as file:
    #     file.write(final_url)
    # file.close()
    # # for findaddress in outer_html.find_all('absolute inset-0 overflow-hidden', class_=):

    # Within Outerhtml, a new address appears once every 8 x "absolute inset-0 overflow-hidden" classes

    # pattern = '(?:(sale\/))(.*)'
    # # result = re.match(pattern, outer_html)
    # if match := re.search(pattern, outer_html, re.IGNORECASE):
    #     result = match.group(2)
    # print("the result is: " + result)
    #
    #
    # with open(r'C:\Users\Chris\Desktop\Yoobee\CS201_take2_PyWithIbrahim_part2\propTrends_v02\rubbishsorting.html', 'w') as file:
    #     file.write(result)
    # file.close()
    # # # for findaddress in outer_html.find_all('absolute inset-0 overflow-hidden', class_=):
    # #
    #
    #
    #
    # for i in page.find_all('a', class_='ember-view block h-full'):
    #     print("You're looking for property URLs")
    #     print(" I is... " + str(i))
    #     prop_href = (i['href'])
    #     print(prop_href)
    #     add_pattern = '(?:(sale\/))(.*)'
    #     suburb_id = 0
    #     # result = re.match(pattern, outer_html)
    #     if match := re.search(add_pattern, prop_href):
    #         result = match.group(2)
    #         address = result.replace('-', ' ')
    #         print("the address is: " + address)
    #         suburb_pattern = '(?<=\s)(\w+)$'
    #         if match := re.search(suburb_pattern, address):
    #             suburb = match.group(1)
    #             print("the address is: " + suburb)
    #
    #             # Check to see if suburb exists in suburb table
    #             suburb_exists = db.session.query(Suburb_key.query.filter_by(suburb_name=suburb).exists()).scalar()
    #             if suburb_exists:
    #                 # Get suburb id
    #                 suburb_id = Suburb_key.query.filter_by(suburb_name=suburb).first().id
    #                 print("existing suburb id is " + str(suburb_id))
    #             else:
    #                 # Create a new record
    #                 new_suburb = Suburb_key(
    #                     suburb_name=suburb
    #                 )
    #                 db.session.add(new_suburb)
    #                 db.session.commit()
    #                 suburb_id = db.session.refresh(new_suburb)  # getting new suburb id
    #                 print("new suburb id is " + str(suburb_id))

        #
        # # RESTARTING FROM SCRATCH TESTING------
        # # This only works for houses that are "large format"
        # listing_exists = db.session.query(Listing.query.filter_by(prop_url=prop_href).exists()).scalar()
        # print("Does the listing exist? " + str(listing_exists))
        #     # If it exists, carry on?
        # if listing_exists:
        #     print("Move along")
        # else:
        #
        #     # # Find the right block to get the house type
        #     # proptype = i.find_next('data-test').text.strip()
        #     # print("Did I get the proptype? :" + str(proptype))
        #     new_list = Listing(
        #         prop_url=prop_href,
        #         address=address,
        #         suburb=suburb_id
        #     )
        #     db.session.add(new_list)
        #     db.session.commit()
        #     db.session.refresh(new_list)
        #     listing_id = new_list.id
        #     print("The listing id is :" + str(listing_id))
        #     sleep(randint(1, 3))  # Adding a sleep time to make sure this doesn't flood the site with too many requests
        #     values = scrape_indiv(mainurl, prop_href, listing_id)
        #     print(values)
        #
        #
        #
        # # Appending the listing index to the indexes_scraped list. This allows for scraping listings that are non-consecutive
        # #         # Note: Each property's URL appears 2 times in this format per listing, therefore listing_index/2
        # # Write condition that checks if property URL already exists. If exists, get that listing.id, otherwise
        # # create a new listing and get listing id
        # # indexes_scraped.append(int(listing_index / 2))
        # # print("The prop href is not in the listings href or add_href list.\
        # #         Adding this to Listing database and getting the id")
        # # new_list = Listing(
        # #     prop_url=prop_href
        # # )
        # # db.session.add(new_list)
        # # db.session.commit()
        # # db.session.refresh(new_list)
        # # listing_id = new_list.id
        # # print("The listing id is :" + str(listing_id))
        # #
        # # add_href.append(prop_href)
        # # print("Add_href list is: ", add_href)
        # # sleep(randint(1, 3))        # Adding a sleep time to make sure this doesn't flood the site with too many requests
        # # values = scrape_indiv(mainurl, prop_href, listing_id)
        # add_br.append(values[0])
        # add_bath.append(values[1])
        # add_land.append(values[2])
        # add_floor.append(values[3])
        # add_gr.append(values[4])
        # add_op.append(values[5])
        # add_nbs.append(values[6])
        # add_bc.append(values[7])
        # add_rates.append(values[8])
        # add_title.append(values[9])
        # add_date.append(values[10])
        # add_ensuite.append(values[11])
        # add_agents.append(values[12])
        # add_agency.append(values[13])
        # add_count += 1
        # return values

    #     if not prop_href in listings_href and not prop_href in add_href:
    #         # Appending the listing index to the indexes_scraped list. This allows for scraping listings that are non-consecutive
    #         # Note: Each property's URL appears 2 times in this format per listing, therefore listing_index/2
    #         indexes_scraped.append(int(listing_index / 2))
    #         print("The prop href is not in the listings href or add_href list")
    #         add_href.append(prop_href)
    #         print("Add_href list is: ", add_href)
    #         sleep(randint(1, 3))        # Adding a sleep time to make sure this doesn't flood the site with too many requests
    #         values = scrape_indiv(mainurl, prop_href)
    #         add_br.append(values[0])
    #         add_bath.append(values[1])
    #         add_land.append(values[2])
    #         add_floor.append(values[3])
    #         add_gr.append(values[4])
    #         add_op.append(values[5])
    #         add_nbs.append(values[6])
    #         add_bc.append(values[7])
    #         add_rates.append(values[8])
    #         add_title.append(values[9])
    #         add_date.append(values[10])
    #         add_ensuite.append(values[11])
    #         add_agents.append(values[12])
    #         add_agency.append(values[13])
    #         add_count += 1
    #     listing_index += 1
    # print("The list of houses (index) to be scraped are: ", indexes_scraped)
    #
    # #=============================================================================================
    # # [COLLAPSED FORMAT] After the 15th listing in page 5, the listings appear in a different (collapsed) format.
    # # This script is used to capture that information.
    # if pagenum > 5:
    #     for i in page.find_all('a', class_='ember-view absolute inset-x-0 bottom-0 z-10 pt-8 bg-gradient-to-t from-fade-dark'):
    #         print("You're looking for property URLs past page 5")
    #         prop_href = (i['href'])
    #         print(prop_href)
    #         if not prop_href in listings_href and not prop_href in add_href:
    #             # Appending the listing index to the indexes_scraped list. This allows for scraping listings that are non-consecutive
    #             # Note: When there's a collapsed listing, the expanded property's URL appears 3 times,
    #             # while the collapsed listing URLs only appear once in this format
    #             indexes_scraped.append(int((listing_index / 3) + collapsedlist_index))
    #             print("[collapsed] The prop href is not in the listings href or add_href list")
    #             add_href.append(prop_href)
    #             print("Add_href list is: ", add_href)
    #             sleep(randint(1, 5))  # Adding a sleep time to make sure this doesn't flood the site with too many requests
    #             values = scrape_indiv(mainurl, prop_href)
    #             add_br.append(values[0])
    #             add_bath.append(values[1])
    #             add_land.append(values[2])
    #             add_floor.append(values[3])
    #             add_gr.append(values[4])
    #             add_op.append(values[5])
    #             add_nbs.append(values[6])
    #             add_bc.append(values[7])
    #             add_rates.append(values[8])
    #             add_title.append(values[9])
    #             add_date.append(values[10])
    #             add_ensuite.append(values[11])
    #             add_agents.append(values[12])
    #             add_agency.append(values[13])
    #             add_count += 1
    #             print("Add_count is now: ", add_count)
    #         collapsedlist_index += 1
    #         print("collapsedlist_index is now: ", collapsedlist_index)
    #     print("The list of houses (index) to be scraped are: ", indexes_scraped)
    #
    # # Saving scraped data so far to a backup CSV file so that not all data is lost if scrape fails halfway
    # # *** Needs to be refined ***
    # with open(backup_path, 'w') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=',')
    #     wr.writerow(add_date)
    #     wr.writerow(add_br)
    #     wr.writerow(add_bath)
    #     wr.writerow(add_floor)
    #     wr.writerow(add_land)
    #     wr.writerow(add_gr)
    #     wr.writerow(add_op)
    #     wr.writerow(add_ensuite)
    #     wr.writerow(add_rates)
    #     wr.writerow(add_bc)
    #     wr.writerow(add_nbs)
    #     wr.writerow(add_href)
    #     wr.writerow(add_agents)
    #     wr.writerow(add_agency)
    # myfile.close()
    #
    #
    # if collapsedlist_index > 0:
    #     ## [COLLAPSED FORMAT] TAG FOR ADDRESSES ON PAGE
    #     addcoladd_count = listing_index / 3
    #     listing_add = page.find_all(attrs={"data-test": "standard-tile__search-result__address"})
    #     for tag in listing_add:
    #         print("Listing address is ", tag)
    #         if addcoladd_count in indexes_scraped:
    #             add_address.append(tag.text.strip())
    #         addcoladd_count += 1
    #
    #     ## [COLLAPSED FORMAT] TAG FOR ALL PRICES ON PAGE
    #     listing_price = page.find_all(attrs={"data-test": "price-display__price-method"})
    #     addpx_count = 0
    #     # For each listing price only
    #     for each in listing_price:
    #         if addpx_count in indexes_scraped:
    #             just_text = each.text.strip()
    #             # print(just_text)
    #             match = re.search(r'\$(\d[\d.,]*\d)', just_text)
    #             if match:
    #                 #     print(match.group(0))
    #                 add_price.append(str(match.group(0)))
    #             else:
    #                 # print(just_text)
    #                 add_price.append(just_text)
    #         addpx_count += 1
    #
    # else:
    #     ## TAG FOR ALL PRICES ON PAGE
    #     listing_price = page.find_all(attrs={"data-test": "price-display__price-method"})
    #     addpx_count = 0
    #     # For each listing price only
    #     for each in listing_price:
    #         if addpx_count in indexes_scraped:
    #             just_text = each.text.strip()
    #             # print(just_text)
    #             match = re.search(r'\$(\d[\d.,]*\d)', just_text)
    #             if match:
    #                 #     print(match.group(0))
    #                 add_price.append(str(match.group(0)))
    #             else:
    #                 add_price.append(just_text)
    #         addpx_count += 1
    #
    #     ## TAG FOR ALL ADDRESSES ON PAGE
    #     addadd_count = 0
    #     listing_add = page.find_all(attrs={"data-test": "standard-tile__search-result__address"})
    #     print("We got listing address ", listing_add)
    #     for tag in listing_add:
    #         print("Listing address tag is ", tag)
    #         if addadd_count in indexes_scraped:
    #             add_address.append(tag.text.strip())
    #         addadd_count += 1
    #
    #     ## TAG FOR ALL ADDRESSES ON PAGE
    #     addadd_count = 0
    #     # For most cases, attrs works better, but the first couple of pages might have premium posts so finding the
    #     # h3 class actually works better for listing addresses before page 5
    #     listing_add = page.find_all('h3', class_='mb-1 pr-3 text-base font-semibold capitalize text-black')
    #     print("We got listing address ", listing_add)
    #     for tag in listing_add:
    #         print("Listing address tag is ", tag)
    #         if addadd_count in indexes_scraped:
    #             add_address.append(tag.text.strip())
    #         addadd_count += 1
    #
    # # GETTING SUMMARY VALUES FROM THE MAIN PAGE (slightly more efficient than scraping from each individuallisting)
    # # Note: SAME FOR EXPANDED AND COLLAPSED FORMAT
    # all_property_types = page.find_all(attrs={"data-test": "tile__search-result__content__features__divider"})
    # addtypes_count = 0
    # for tag in all_property_types:
    #     # Check if the listing index was scraped
    #     if addtypes_count in indexes_scraped:
    #         prop_types = tag.text.strip()
    #         print("Property type is: ", prop_types, " and type is ", type(prop_types))
    #         add_types.append(str(prop_types))
    #         print("I have added proptype ", tag.text.strip())
    #     addtypes_count += 1
    #
    # all_specifications = page.find_all('div', class_="flex items-center")
    # addsize_count = 0
    # for tag in all_specifications[2::3]:
    #     if addsize_count in indexes_scraped:
    #         prop_specs = tag.text.strip().split()
    #         print("Prop specs are: ", prop_specs)
    #         # print(prop_specs[::2])
    #         if prop_specs == []:
    #             add_size.append(0)
    #         elif not prop_specs[0].isnumeric():
    #             add_size.append(str(prop_specs.pop()))
    #         # print("This property type is a section")
    #         else:  # Values should be convertible to int
    #             if len(prop_specs) == 2:
    #                 add_size.append(0)
    #             else:
    #                 add_size.append(str(prop_specs[2:3:3].pop()))
    #     addsize_count += 1
    #
    # # Extremely useful for log output
    # print(add_count)
    # print(len(add_address))
    # print(len(add_price))
    # print(add_price)
    # print(len(add_br))
    # print(len(add_bath))
    # print(len(add_floor))
    # print(len(add_land))
    # print(len(add_nbs))
    # print(len(add_gr))
    # print(len(add_op))
    # print(len(add_rates))
    # print(len(add_bc))
    # print(len(add_types))
    # print(len(add_href))
    # print(len(add_agents))
    # print(len(add_agency))
    #
    # # Saving lists to a backup CSV in case the list lengths are not equal (something not scraped due to wrong format),
    # # before saving to DF. Needs to be optimised.
    # with open(backup_path, 'a') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=',')
    #     wr.writerow(add_address)
    #     wr.writerow(add_price)
    #     wr.writerow(add_size)
    #     wr.writerow(add_types)
    # myfile.close()
    #
    #
    # print("Storing lists to dataframe....")
    # add_output = pd.DataFrame({'ListDate': add_date,
    #                        'Address': add_address,
    #                        'ListPrice': add_price,
    #                        'Beds': add_br,
    #                        'Baths': add_bath,
    #                        'Size': add_size,
    #                        'FloorArea': add_floor,
    #                        'LandArea': add_land,
    #                        'Garage': add_gr,
    #                        'OtherParks': add_op,
    #                        'Ensuite': add_ensuite,
    #                        'Rates': add_rates,
    #                        'BodyCorp': add_bc,
    #                        'NBS': add_nbs,
    #                        'ProppyTypes': add_types,
    #                        'PropURL': add_href,
    #                        'Agents': add_agents,
    #                        'Agency': add_agency})
    # print(add_output)
    # print("Output in dataframe. Merging with historical records...")
    # data_in_store['ListDate'] = pd.to_datetime(data_in_store['ListDate'], format="%Y-%m-%d")
    # add_output['ListDate'] = pd.to_datetime(add_output['ListDate'], format="%Y-%m-%d")
    # print("data_in_store type: ", data_in_store['ListDate'].dtypes)
    # print("add_output type: ", add_output['ListDate'].dtypes)
    # data_merge = pd.concat([data_in_store, add_output])
    # print(data_merge)
    # sorted = data_merge.sort_values(by='ListDate', ascending=False)
    # print(sorted)
    # print("Data sorted, now storing to CSV...")
    # sorted.to_csv(readdata_path, index=False)
    # print("Output stored in csv")
    winsound.Beep(1000, 100)
    winsound.Beep(2000, 100)
    winsound.Beep(3000, 100)


    return add_count