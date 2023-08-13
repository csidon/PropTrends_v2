# Contains all the routes specific to scraper routes

from flask import render_template, url_for, flash, Blueprint, jsonify, request
from proptrends.models import Listing, Region_key, City_key,Suburb_key,Proptype_key
from proptrends.scraper.rawmeat import *
from proptrends.scraper.forms import *
from proptrends import db
from flask_login import login_required
from datetime import datetime
from proptrends.main.utils import format_currency, format_area2, convert_to_id, update_region
from sqlalchemy import or_, and_
from proptrends.scraper.all_region_lists import get_list
import logging


# logging.basicConfig(level=logging.DEBUG)

scraper = Blueprint('scraper', __name__)

@scraper.route("/scrapelist", methods=['GET', 'POST'])
@login_required             # Needed for routes that can only be accessed after login
def list_scrapings():
    listings = db.session.query(Listing).join(Region_key, Listing.region == Region_key.id)\
                .join(City_key, Listing.city == City_key.id)\
                .join(Suburb_key, Listing.suburb == Suburb_key.id)\
                .join(Proptype_key, Listing.prop_type == Proptype_key.id)
    
    all_suburbs = db.session.query(Suburb_key).all()
    all_props = db.session.query(Proptype_key).all()
    listings = listings.all()
    # print("Ze listings are: " + str(listings) + "with datatype : " + str(type(listings)))
    formatted_listings, avg_listing_price_psqm = process_listings(listings)
    
    
    form = ScrapeSuburbForm()
    if form.validate_on_submit():
        print("someone submitted a scrape request")
        if form.suburb_to_scrape.data == 'Wellington':
            print("Sending request to scraper_runner")
            scraper_runner('wellington')
            print("Scraper runner has run")

        else:
            print("I Got Nothing.")
            pass # unknown
    
    return render_template('scrapelist.html', title='Scraped Listings', listings=formatted_listings, all_suburbs=all_suburbs,\
                            form=form, all_props=all_props, avg_listing_price_psqm=format_currency(avg_listing_price_psqm))

@scraper.route("/scrapertool", methods=['GET', 'POST'])
@login_required             # Needed for routes that can only be accessed after login
def scrapertool():

    form = ScrapeSuburbForm()
    if request.method=='POST' and form.validate_on_submit():
            print("someone submitted a scrape request")
            if form.suburb_to_scrape.data == 'Wellington':
                print("Sending request to scraper_runner")

                # Would like to display some scraping progress information here.. 
                # but not for submission.
                scraper_runner('wellington')
                print("Scraper runner has run")

            else:
                print("I Got Nothing.")
                pass # unknown
    
    return render_template('scrapertool.html', title='Scraped Listings', form=form)




def apply_filter_and_format(selected_filters):
    selected_suburbs = selected_filters.get('suburbs', [])
    selected_proptypes = selected_filters.get('prop_types', [])
    # print("apply_filter_and_format() started. selected_suburbs = " + str(selected_suburbs) + \
    #       " selected_proptypes = " + str(selected_proptypes))

    # Convert them to int (for Region, City, Suburbs, and Property Types only)
    # Translating it to the table_key...
    if any(suburb.strip() for suburb in selected_suburbs):
        selected_int_suburbs = [convert_to_id(Suburb_key, 'suburb_name', suburb) for suburb in selected_suburbs]
    else:
        selected_int_suburbs = []
    if any(props.strip() for props in selected_proptypes):
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

    if selected_int_suburbs:
        filter_conditions.append(Listing.suburb.in_(selected_int_suburbs))
    if selected_int_proptypes:
        filter_conditions.append(Listing.prop_type.in_(selected_int_proptypes))
    # print("The filter_conditions collected are..: " + str(filter_conditions))
    if filter_conditions:
        filtered_listings = unfiltered_listings.filter(and_(*filter_conditions))
    
    if filtered_listings:
        listings = filtered_listings.all()

    # print("The filtered listings through multi conditions are: " + str(listings))

    return listings


@scraper.route("/filter-and-sort")
def filter_and_sort():
    selected_filter = request.args.to_dict()
    # print("What is the selected filter right now? " + str(selected_filter) + " and it has datatype " + str(type(selected_filter)))
    selected_suburbs = request.args.get('suburbs').split(',')
    # print("The selected_suburbs are: " + str(selected_suburbs) )
    selected_proptypes = request.args.get('prop_type').split(',')
    # print("The selected_suburbs are: " + str(selected_proptypes) )

    combined_filters_dict = {
        'suburbs' : selected_suburbs,
        'prop_types' : selected_proptypes
    }
    # Translating it to the suburb_key...


    # print("What is the selected filter right now? " + str(selected_filter) + " and it has datatype " + str(type(selected_filter)))
    listings = apply_filter_and_format(combined_filters_dict)

    print("The listings retrieved from apply_filter.. are : " + str(listings) + " with datatype: " + str(type(listings)))
    
    formatted_listings = []
    if not any(listing.id for listing in listings):
        listings = Listing.query.join(Region_key, Listing.region == Region_key.id)\
                .join(City_key, Listing.city == City_key.id)\
                .join(Suburb_key, Listing.suburb == Suburb_key.id)\
                .join(Proptype_key, Listing.prop_type == Proptype_key.id)
        print("All filters have been removed. Show everything!")
    formatted_listings, avg_listing_price_psqm  = process_listings(listings) # This returns a tuple
    # print("The formatted_listings after processing are : " + str(formatted_listings) + " with datatype : " + str(type(formatted_listings)))
  
    return jsonify(listings=formatted_listings, avg_listing_price_psqm=format_currency(avg_listing_price_psqm))




@scraper.route("/runscrape/<string:region_name>", methods=['GET','POST'])
def scraper_runner(region_name):
    url = "https://www.realestate.co.nz"
    print("Retriving list using get_list method")
    
    # Get the list that we want to scrape based off the region_name
    wgtn_suburb_list = get_list(region_name)
    scraper_still_running = True
    for suburb in wgtn_suburb_list:
        print(">>>>>>>> STARTING SCRAPING FOR SUBURB: " + suburb)
        next_action = "start_scrape"
        pagenum = 1

        # Update the Last_scraped table 
        update_region(region_name, "start")

        while next_action != "next_suburb":
            if next_action == "start_scrape": # This is a new scrape for this suburb. Scrape the main page.
                subdir = "/residential/sale/wellington/wellington-city/" + suburb
            elif next_action == "next_page":
                subdir = "/residential/sale/wellington/wellington-city/" + suburb + "?page=" + str(pagenum)
            next_action = scrape_main(url, subdir, pagenum)
            pagenum += 1
            update_region(region_name, "end")
        print("next_action must have returned next_suburb. Moving on to next item in suburb_list...")
    print("We have run through the full suburb list")
    

    print("You have finished scraping")

    # Note, beeps only work when triggering script from a local machine, it will not work on a browser-based app
    winsound.Beep(1000, 100)
    winsound.Beep(1000, 50)
    winsound.Beep(1000, 50)
    winsound.Beep(3000, 300)

    return scraper_still_running


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
    listing_price_psqm = 0
    total_listed_sqm_with_prices = 0

    # calc_psqm_average(listings)
    # First, retrieve the listings with a valid list price and area
    # and calculate the average listing's price per sqm
    for listing in listings:
        # print("the listing's list_price is :" + str(listing))
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
    # update_psqm_average(avg_listing_price_psqm)

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
                
        formatted_listings.append(formatted_listing)
    return formatted_listings, avg_listing_price_psqm 