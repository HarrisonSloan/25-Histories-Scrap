# Details


# Work flow 
## Scrapping
run test_alterntive to produce all scrapped files 
run scrap chinese_era_names -> then produced emperors_year_1.json by hand from emperors_data_raw.json
Note repeat_emperor name a valdility check and more manual work needs to be done after this has been completed
## Creating data
run combine_xml to make a large text file that gets rid of the volumes 
run find_emperor_positions to create XML of all the emperor positions 
run create_year_patterns to create the year patterns -> patterns
run find_year_positions to find all the year positions and produce XML for final and main program
## Main program 
simply run alter patterns as needed
