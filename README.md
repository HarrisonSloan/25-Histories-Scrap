# Details


# Work flow 
## Scrapping
run scrap_history to produce all scrapped files 
run scrap chinese_era_names -> then produce emperors_year_1.json by hand (selective about including certain emperors from List of Chinese Era names) from emperors_data_raw.json
Note repeat_emperor name a valdility check and more manual work needs to be done after this has been completed. Note this is still yet to be reflected and done
## Creating data
run combine_xml to make a large text file that gets rid of the volumes and put the entire history into 1 file
run find_emperor_positions to create XML of all the emperor positions 
run create_year_patterns to create the year_patterns. The reasoning is for this is we dont necessarily want years that are within a sentence but instead come after punctation.
run find_year_positions to find all the year positions and produce XML for final and main program
## Main program 
simply run alter patterns as needed

## Other notes
havent dealed with the volume problem, need to add in a "start" match. If you match something at the start of the volume a better guess to to reference the next emeperor in the volume not the last emperor in the previous volume. Can remedy this by adding a match at the start position of every volume and value it by whatever is next emperor metioned.
Have not included the appendix yet or tables from Wikipedia (strictly just volumes from each respective list)
Have not cleaned the data properly, this means removing certain text ect, notes and other random HTML stuff
We previously included emperors as a way to match keywords against, but we only strictly do the years. This is what we had in the original paper shown
