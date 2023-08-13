# Contains utility functions that are used by the routes in main package
import locale
from flask import render_template, Flask  # Not needed here but commonly used, clean up if not used on submission!
from proptrends import db
from proptrends.models import Last_scraped
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'en_NZ')

# This is a custom filter for formatting integers to a currency string
def format_currency(value):
    # return locale.currency(value, grouping=True)
    return "${:,.0f}".format(round(value))

# This is a custom filter for formatting integers to a currency string
def format_area2(value):
    return str(value) + "m²"

#======================================================================================================
# This method looks up a name in a key-table, retrieves or creates a new record, 
# then returns the name's id
#-----------------------------------------------------------------------------------------------------
def convert_to_id(Table_key, name_in_table, name_to_convert):
    # The table associates the name that we want to convert with int ids so that it's cheaper, and more efficient to store/call
    name_exists = db.session.query(Table_key.query.filter(getattr(Table_key, name_in_table) == name_to_convert).exists()).scalar()
    if name_exists:
        # Get Name id
        name_id = Table_key.query.filter_by(**{name_in_table: name_to_convert}).first().id
        print("existing name's id is " + str(name_id))
    else:
        # Create a new record using the name_to_convert and grab the new record's id
        new_name = Table_key(
            **{name_in_table: name_to_convert}
        )
        db.session.add(new_name)
        db.session.commit()
        db.session.refresh(new_name)
        name_id = new_name.id  # getting new name_id id
        print("new name's id is " + str(name_id))
    return name_id



#======================================================================================================
# This function UPDATE last_scraped TABLE with the current datetime
# No return required
#-----------------------------------------------------------------------------------------------------
# Check if region already exists:
def update_region(region_name, action):
    # Method used below. Defined to reduce repetition
    # Defined within the update_region function as we don't really want to 
    # call this function without first checking that the region exists
    def update_lastscraped(action,region_name):
        region_record = Last_scraped.query.filter_by(region=region_name).first()
        # Update the last_scrape_start or last_scraped_end depending on action
        if action == "start":
            try:
                region_record.last_scrape_start = datetime.now()
                region_record.still_running = True
                db.session.commit()
                print("last_scrape_start updated successfully")
            except Exception as err:
                raise err

        elif action == "end":
            try:
                region_record.last_scrape_end = datetime.now()
                region_record.still_running = False
                db.session.commit()
                print("last_scrape_end updated successfully")
            except Exception as err:
                raise err
            
    # name_exists = db.session.query(Suburb_key.query.filter(Suburb_key.suburb_name == selected_sub).exists()).scalar()
    region_exists = db.session.query(Last_scraped.query.filter_by(region=region_name).exists()).scalar()
    if region_exists:
        update_lastscraped(action, region_name)
    else:
        # Create region
        new_region = Last_scraped(region=region_name)
        db.session.add(new_region)
        db.session.commit()
        db.session.refresh(new_region)
        region_id = new_region.id  # getting new region's id (although in this case we might not need it? Check and delete if not needed)
        print("new region's id is " + str(region_id))
        update_lastscraped(action, region_name)