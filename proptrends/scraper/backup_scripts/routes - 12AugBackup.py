# Contains all the routes specific to scraper routes

from flask import render_template, url_for, flash, Blueprint, jsonify, request
from proptrends.models import Listing, Region_key, City_key,Suburb_key,Proptype_key
from proptrends.scraper.rawmeat import *
from proptrends.scraper.forms import *
from proptrends import db
from flask_login import current_user, login_required
from datetime import datetime
from proptrends.main.utils import format_currency, format_area2, convert_to_id
from sqlalchemy import or_, and_




scraper = Blueprint('scraper', __name__)

@scraper.route("/scrapelist", methods=['GET', 'POST'])
# @login_required             # Needed for routes that can only be accessed after login
def list_scrapings():
    listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
                .join(City_key, Listing.city == City_key.id)\
                .join(Suburb_key, Listing.suburb == Suburb_key.id)\
                .join(Proptype_key, Listing.prop_type == Proptype_key.id)
    
    all_suburbs = Suburb_key.query.all()
    all_props = Proptype_key.query.all()
    listings = listings.all()
    print("Ze listings are: " + str(listings) + "with datatype : " + str(type(listings)))
    formatted_listings, avg_listing_price_psqm = process_listings(listings)
    
    
    form = ScrapeSuburbForm()
    if form.validate_on_submit():
        if form.suburb_to_scrape.data == 'Wellington':
            scraper_runner()
            print("Scraper runner has run")

        else:
            print("I Got Nothing.")
            pass # unknown
    
    return render_template('scrapelist.html', title='Scraped Listings', listings=formatted_listings, all_suburbs=all_suburbs,\
                            form=form, all_props=all_props, avg_listing_price_psqm=format_currency(avg_listing_price_psqm))


# def translate_to_key(selected_object):
#     selected_int_object = []
#     for key in selected_object:
#         print("Converting... " + key)
#         name_exists = db.session.query()


# def apply_filter_and_format(selected_filters):
#     selected_suburbs = selected_filters.get('suburbs', [])
#     selected_proptypes = selected_filters.get('prop_types', [])
#     print("apply_filter_and_format() started. selected_suburbs = " + str(selected_suburbs) + \
#           " selected_proptypes = " + str(selected_proptypes))

#     # Convert them to int (for Region, City, Suburbs, and Property Types only)
#     # Translating it to the table_key...
    # selected_int_suburbs = [convert_to_id(Suburb_key, 'suburb_name', suburb) for suburb in selected_suburbs]
    # selected_int_proptypes = [convert_to_id(Proptype_key, 'type', proptype) for proptype in selected_proptypes]
#     selected_int_suburbs = []
#     selected_int_proptypes = []
#     if selected_suburbs:    # Selected_suburbs list is not empty
#         for suburb in selected_suburbs:
#             suburb_id = convert_to_id(Suburb_key, 'suburb_name', suburb)
#             selected_int_suburbs.append(suburb_id)
#         print("suburb_ids filtered are: " + str(selected_int_suburbs))
#     selected_int_proptypes = [3]    
#     if selected_proptypes:
#         for proptype in selected_proptypes:
#             proptype_id = convert_to_id(Proptype_key, 'type', proptype)
#             selected_int_proptypes.append(proptype_id)
#         print("Proptype_ids filtered are: " + str(selected_int_proptypes))

#     # Query your database to filter by selected suburbs
#     unfiltered_listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
#                 .join(City_key, Listing.city == City_key.id)\
#                 .join(Suburb_key, Listing.suburb == Suburb_key.id)\
#                 .join(Proptype_key, Listing.prop_type == Proptype_key.id)
    
#     # Collating all the filter conditions
#     filter_conditions = []
#     filter_conditions2 = []
#     if selected_int_suburbs:
#         print("the Listing.suburb.in_(selected_int_suburbs) is " + str(Listing.suburb.in_(selected_int_suburbs)))
#         filter_conditions.append(Listing.suburb.in_(selected_int_suburbs))
    
#     if filter_conditions:
#         filtered_listings = set(unfiltered_listings.filter(or_(*filter_conditions)).all() )    # Gets a list of all items 

                                 
#     if selected_int_proptypes:
#         filter_conditions2.append(Listing.prop_type.in_(selected_int_proptypes))    # Should churn out list of prop ids, i.e. [3, 2]
    
#     if filter_conditions2:
#         filtered_listings2 = set(unfiltered_listings.filter(or_(*filter_conditions2)).all())    # Gets a list of all items
    
#     listings = list(filtered_listings.intersection(filtered_listings2))

#     print("The filtered listings through multi conditions are: " + str(listings))

#     return listings


def apply_filter_and_format(selected_filters):
    selected_suburbs = selected_filters.get('suburbs', [])
    selected_proptypes = selected_filters.get('prop_types', [])
    print("apply_filter_and_format() started. selected_suburbs = " + str(selected_suburbs) + \
          " selected_proptypes = " + str(selected_proptypes))

    # Convert them to int (for Region, City, Suburbs, and Property Types only)
    # Translating it to the table_key...
    if any(suburb.strip() for suburb in selected_suburbs):
        print("selected_suburbs>> I got here. How the heck did I get here??")
        selected_int_suburbs = [convert_to_id(Suburb_key, 'suburb_name', suburb) for suburb in selected_suburbs]
    else:
        selected_int_suburbs = []
    if any(props.strip() for props in selected_proptypes):
        print("I got here. I'm supposed to be here")
        selected_int_proptypes = [convert_to_id(Proptype_key, 'type', proptype) for proptype in selected_proptypes]
    else:
        selected_int_proptypes = []
    # selected_int_proptypes = [3]
    
    # Query your database to filter by selected suburbs
    unfiltered_listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
                .join(City_key, Listing.city == City_key.id)\
                .join(Suburb_key, Listing.suburb == Suburb_key.id)\
                .join(Proptype_key, Listing.prop_type == Proptype_key.id)
    
    # Constructing the filter conditions dynamically
    listings = []
    filter_conditions = []
    filtered_listings = []
    print("What does selected_int_suburbs look like atm? :" + str(selected_int_suburbs))
    print("What does selected_int_proptypes look like atm? :" + str(selected_int_proptypes))
    if selected_int_suburbs:
        filter_conditions.append(Listing.suburb.in_(selected_int_suburbs))
    if selected_int_proptypes:
        filter_conditions.append(Listing.prop_type.in_(selected_int_proptypes))
    print("The filter_conditions collected are..: " + str(filter_conditions))
    if filter_conditions:
        filtered_listings = unfiltered_listings.filter(and_(*filter_conditions))
    
    if filtered_listings:
        listings = filtered_listings.all()

    print("The filtered listings through multi conditions are: " + str(listings))

    return listings


@scraper.route("/filter-and-sort")
def filter_and_sort():
    selected_filter = request.args.to_dict()
    print("What is the selected filter right now? " + str(selected_filter) + " and it has datatype " + str(type(selected_filter)))
    selected_suburbs = request.args.get('suburbs').split(',')
    print("The selected_suburbs are: " + str(selected_suburbs) )
    selected_proptypes = request.args.get('prop_type').split(',')
    print("The selected_suburbs are: " + str(selected_proptypes) )

    combined_filters_dict = {
        'suburbs' : selected_suburbs,
        'prop_types' : selected_proptypes
    }
    # Translating it to the suburb_key...


    # print("What is the selected filter right now? " + str(selected_filter) + " and it has datatype " + str(type(selected_filter)))
    listings = apply_filter_and_format(combined_filters_dict)

    print("The listings retrieved from apply_filter.. are : " + str(listings) + " with datatype: " + str(type(listings)))
    # formatted 

    # print("The selected_suburbs are: " + str(selected_filter) )
    # # Translating it to the suburb_key...
    # selected_int_subs = []
    # for selected_sub in selected_suburbs:
    #     print("The selected_sub to convert is " + selected_sub)
    #     name_exists = db.session.query(Suburb_key.query.filter(Suburb_key.suburb_name == selected_sub).exists()).scalar()

    #     if name_exists:
    #         # Get Name id
    #         sub_id = Suburb_key.query.filter(Suburb_key.suburb_name == selected_sub).first().id
    #         print("existing suburb's id is " + str(sub_id))
    #         selected_int_subs.append(sub_id)
    #         print(selected_int_subs)
    #     else:
    #         print("Not found in Suburb_Key table. THIS SHOULD NOT HAPPEN!")

    # # Query your database to filter by selected suburbs
    # filtered_listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
    #             .join(City_key, Listing.city == City_key.id)\
    #             .join(Suburb_key, Listing.suburb == Suburb_key.id)\
    #             .join(Proptype_key, Listing.prop_type == Proptype_key.id).filter(Listing.suburb.in_(selected_int_subs))
    
    # # formatted_listings = process_listings(filtered_listings)
    # listings = filtered_listings.all()
    # print("filtered_listings are: " + str(listings) + "with datatype : " + str(type(listings)))
    formatted_listings = []
    if not any(listing.id for listing in listings):
        listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
                .join(City_key, Listing.city == City_key.id)\
                .join(Suburb_key, Listing.suburb == Suburb_key.id)\
                .join(Proptype_key, Listing.prop_type == Proptype_key.id)
        print("All filters have been removed. Show everything!")
    formatted_listings = process_listings(listings)
    # print("The formatted_listings after processing are : " + str(formatted_listings) + " with datatype : " + str(type(formatted_listings)))
  
    return jsonify(listings=formatted_listings)

# @scraper.route("/filter-and-sort")
# def filter_and_sort():
#     selected_suburbs = request.args.get('suburbs').split(',')

#     print("The selected_suburbs are: " + str(selected_suburbs) )
#     # Translating it to the suburb_key...
#     selected_int_subs = []
#     for selected_sub in selected_suburbs:
#         print("The selected_sub to convert is " + selected_sub)
#         name_exists = db.session.query(Suburb_key.query.filter(Suburb_key.suburb_name == selected_sub).exists()).scalar()

#         if name_exists:
#             # Get Name id
#             sub_id = Suburb_key.query.filter(Suburb_key.suburb_name == selected_sub).first().id
#             print("existing suburb's id is " + str(sub_id))
#             selected_int_subs.append(sub_id)
#             print(selected_int_subs)
#         else:
#             print("Not found in Suburb_Key table. THIS SHOULD NOT HAPPEN!")

#     # Query your database to filter by selected suburbs
#     filtered_listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
#                 .join(City_key, Listing.city == City_key.id)\
#                 .join(Suburb_key, Listing.suburb == Suburb_key.id)\
#                 .join(Proptype_key, Listing.prop_type == Proptype_key.id).filter(Listing.suburb.in_(selected_int_subs))
    
#     # formatted_listings = process_listings(filtered_listings)
#     listings = filtered_listings.all()
#     print("filtered_listings are: " + str(listings) + "with datatype : " + str(type(listings)))
#     formatted_listings = process_listings(listings)
  
#     return jsonify(listings=formatted_listings)



@scraper.route("/runscrape", methods=['GET','POST'])
def scraper_runner():
    url = "https://www.realestate.co.nz"
    # wgtn_suburb_list = ["crofton-downs", "glenside", "grenada-north", "grenada-village", "haitaitai", "highbury", "horokiwi",
    #            "houghton-bay", "johnsonville", "kaiwharawhara", "karaka-bays", "karori", "kelburn", "khandallah",
    #            "kilbirnie", "lyall-bay", "makara", "maupuia", "melrose", "miramar", "newlands", "ngaio", "ngauranga",
    #            "northland", "ohariu", "oriental-bay", "paparangi", "rongotai", "roseneath", "seatoun", "southgate",
    #            "strathmore-park", "tawa", "thorndon", "wadestown", "wellington-central", "wilton", "woodridge"]
    wgtn_suburb_list = ["owhiro-bay", "wadestown", "tawa", "thorndon"]
    for suburb in wgtn_suburb_list:
        print(">>>>>>>> STARTING SCRAPING FOR SUBURB: " + suburb)
        next_action = "start_scrape"
        pagenum = 1

        while next_action != "next_suburb":
            if next_action == "start_scrape": # This is a new scrape for this suburb. Scrape the main page.
                subdir = "/residential/sale/wellington/wellington-city/" + suburb
            elif next_action == "next_page":
                subdir = "/residential/sale/wellington/wellington-city/" + suburb + "?page=" + str(pagenum)
            next_action = scrape_main(url, subdir, pagenum)
            pagenum += 1
        print("next_action must have returned next_suburb. Moving on to next item in suburb_list...")
    print("We have run through the full suburb list")

    # Note, beeps only work when triggering script from a local machine, it will not work on a browser-based app
    winsound.Beep(1000, 100)
    winsound.Beep(1000, 50)
    winsound.Beep(1000, 50)
    winsound.Beep(3000, 300)

    return print("You have finished scraping")


def translate_to_icon(list_px, avg_list_px):
    px_percent_difference = (avg_list_px - list_px) / avg_list_px
    # If the listing's px_percent_difference < 0, it's more than the avg value (bad deal)
    # if > 0, it's less than the avg value (good deal!)
    if px_percent_difference < -0.2:
        return "5.png"
    elif -0.2 <= px_percent_difference < -0.05:
        return "4.png"
    elif -0.05 <= px_percent_difference < 0.05:
        return "3.png"
    elif 0.05 <= px_percent_difference < 0.2:
        return "2.png"
    elif px_percent_difference > 0.2:
        return "1.png"
    else:
        return ""   # Shouldn't get here


def process_listings(listings):
    formatted_listings = []
    total_listed_prices_with_area = 0
    total_listings = 0
    total_listings_with_prices_and_area = 0
    listing_price_psqm = 0
    total_listed_sqm_with_prices = 0

    # First, retrieve the listings with a valid list price and area
    # and calculate the average listing's price per sqm
    for listing in listings:
        print("the listing's list_price is :" + str(listing))
        if listing.list_price > 10:    # Should contain a valid listing price
            if listing.floor_m2 is not None:    # Use the floor_m2 to calc
                total_listed_prices_with_area += listing.list_price
                total_listed_sqm_with_prices += listing.floor_m2
            elif listing.size_m2 is not None:    # Use the size_m2 to calc
                total_listed_prices_with_area += listing.list_price
                total_listed_sqm_with_prices += listing.size_m2
            elif listing.land_m2 is not None:    # Use the size_m2 to calc
                total_listed_prices_with_area += listing.list_price
                total_listed_sqm_with_prices += listing.land_m2
        # Otherwise, ignore calcs and just display the listing on table
    # Then calculate the average listing_price_psqm
    avg_listing_price_psqm = total_listed_prices_with_area / total_listed_sqm_with_prices
    print("avg_listing_price_psqm is : " + str(avg_listing_price_psqm))

    # Now retrieve all the listings for display on the table
    for listing in listings:
        total_listings += 1
        formatted_listing = listing.serialize()
        if listing.list_price <= 10:     # This means that the listing didn't display an asking price
            # Ignore the calculation of avg price psqm and just get values
            # Method checks if the listing has a psqm value in either the floor_m2, size_m2, or land_m2 
            formatted_listing['compare_img'] = "na.png"
            formatted_listing['psqm'] = "N/A"
            def get_m2():
                if listing.floor_m2 is None:
                    # Check if size_m2 or land_m2 have values
                    if listing.size_m2 is not None:
                        area = format_area2(listing.size_m2)
                    elif listing.land_m2 is not None:
                        area = format_area2(listing.land_m2)
                    else:
                        area = ""
                else:
                    area = format_area2(listing.floor_m2)
                return area

            if listing.list_price==1:
                formatted_listing['list_price'] = "Auction"
                formatted_listing['floor_m2']  = get_m2()
            elif listing.list_price==2:
                formatted_listing['list_price'] = "Tender"
                formatted_listing['floor_m2']  = get_m2()
            elif listing.list_price==3:
                formatted_listing['list_price'] = "Negotiation"
                formatted_listing['floor_m2']  = get_m2()
            elif listing.list_price==4:
                formatted_listing['list_price'] = "POA"
                formatted_listing['floor_m2']  = get_m2()
            elif listing.list_price==5:
                formatted_listing['list_price'] = "Deadline Sale"
                formatted_listing['floor_m2']  = get_m2()
        else:   # Listing has an asking price. Retrieve asking price
            formatted_listing['list_price'] = format_currency(listing.list_price)
            # Then check if we have scraped a valid area from the listing and calculate psqm
            # formatted_listing['floor_m2'] = get_m2()
            if listing.floor_m2 is None:
                # Check if size_m2 or land_m2 have values
                if listing.size_m2 is not None:
                    formatted_listing['floor_m2'] = format_area2(listing.size_m2)
                    listing_price_psqm = listing.list_price / listing.size_m2
                    # total_listings_with_prices_and_area += 1
                    total_listed_prices_with_area += listing.list_price
                    total_listed_sqm_with_prices += listing.size_m2
                elif listing.land_m2 is not None:
                    formatted_listing['floor_m2'] = format_area2(listing.land_m2)
                    listing_price_psqm = listing.list_price / listing.land_m2
                    # total_listings_with_prices_and_area += 1
                    total_listed_prices_with_area += listing.list_price
                    total_listed_sqm_with_prices += listing.land_m2
                else:
                    formatted_listing['floor_m2'] = ""
                    # Cannot calc average. Show NA img
                    formatted_listing['compare_img'] = "na.png"
                    formatted_listing['psqm'] = "N/A"
                # formatted_listing['compare_img'] = listing_price_psqm # --- Compare and convrt this to an image!
                formatted_listing['compare_img'] = translate_to_icon(listing_price_psqm, avg_listing_price_psqm)
                formatted_listing['psqm'] = format_currency(listing_price_psqm)
            else:
                formatted_listing['floor_m2'] = format_area2(listing.floor_m2)
                listing_price_psqm = listing.list_price / listing.floor_m2
                # total_listings_with_prices_and_area += 1
                total_listed_prices_with_area += listing.list_price
                total_listed_sqm_with_prices += listing.floor_m2
                formatted_listing['compare_img'] = translate_to_icon(listing_price_psqm, avg_listing_price_psqm)
                formatted_listing['psqm'] = format_currency(listing_price_psqm)
                # print("For this listing >>> \n total_listings tally is: "+ str(total_listings))
                # print("total_listed_prices is : " + str(total_listed_prices_with_area))
                # print("total_listed_sqm_with_prices is : " + str(total_listed_sqm_with_prices))
                
                # print("icon to show is : " + formatted_listing['compare_img'])
                # print("<<< End of listing calcs")
                
        formatted_listings.append(formatted_listing)
    return formatted_listings, avg_listing_price_psqm