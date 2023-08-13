

def get_list(region_name):
    all_regions_dict = {
        'wellington':
            ["owhiro-bay", "wadestown", "tawa", "thorndon","crofton-downs", "glenside", "grenada-north", 
             "grenada-village", "haitaitai", "highbury", "horokiwi", "houghton-bay", "johnsonville", 
             "kaiwharawhara", "karaka-bays", "karori", "kelburn", "khandallah","kilbirnie", "lyall-bay", 
             "makara", "maupuia", "melrose", "miramar", "newlands", "ngaio", "ngauranga",
            "northland", "ohariu", "oriental-bay", "paparangi", "rongotai", "roseneath", "seatoun", "southgate",
            "strathmore-park", "tawa", "thorndon", "wadestown", "wellington-central", "wilton", "woodridge"],
        'wellington_test':
            ["owhiro-bay", "wadestown", "tawa", "thorndon"]
    }

    # suburb_list = [sub_list[region_name] for sub_list in all_regions_dict]
    suburb_list = all_regions_dict.get(region_name, [])
    print("suburb_list is:" + str(suburb_list))

    return suburb_list