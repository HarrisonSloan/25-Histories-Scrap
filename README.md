# Details


# Work flow 
## Scrapping
run scrap_history to produce all scrapped files 
run scrap chinese_era_names -> then produce emperors_year_1.json by hand (selective about including certain emperors from List of Chinese Era names) from emperors_data_raw.json
Note repeat_emperor name a valdility check and more manual work needs to be done after this has been completed. Note this is still yet to be reflected and done
## Creating data
run combine_xml to make a large text file that gets rid of the volumes and put the entire history into 1 file, it also creates a file which stores the vol positions
run find_emperor_positions to create XML of all the emperor positions 
run create_year_patterns to create the year_patterns. The reasoning is for this is we dont necessarily want years that are within a sentence but instead come after punctation.
run find_year_positions to find all the year positions and produce XML
run matching_data which combines the vol_xml, emperor_xml and year_xml into a large matching_XML
run filter_matching_data which then filters the matching_xml based on the rules described below
run count_year_freq to get total frequency of years mentioned
## Main program 
simply run alter patterns as needed

## Other notes
havent dealed with the volume problem, need to add in a "start" match. If you match something at the start of the volume a better guess to to reference the next emeperor in the volume not the last emperor in the previous volume. Can remedy this by adding a match at the start position of every volume and value it by whatever is next emperor metioned.
Have not included the appendix yet or tables from Wikipedia (strictly just volumes from each respective list)
Have not cleaned the data properly, this means removing certain text ect, notes and other random HTML stuff
We previously included emperors as a way to match keywords against, but we only strictly do the years. This is what we had in the original paper shown

Know the position of the start of a volume, then add a proxy which would be the next emperor mentions year 

## Matches and how we handle it
Types of matches
Emperor A -> number+year -> keyword
    the keyword is then matched to the emperor A start year + number, (start.EmperorA + number)
Emperor A -> keyword
    keyword is matched to middle of emperor A reign, (start.EmperorA+end.EmperorA) / 2
Emperor A -> keyword -> Emperor B
    keyword is matched to middle of emperor A reign, (start.EmperorA+end.EmperorA) / 2
Start of Vol X -> keyword -> Emperor A
    keyword is matched to midle of emperor A reign, (start.EmperorA+end.EmperorA) / 2
Start of Vol X -> keyword -> number+year -> emperor A
    logically this shouldnt happen and should be matched to (start.emperorA+end.emperorA) / 2
Start of Vol X -> number+year -> keyword -> emperor A 
    logically this shouldnt happen and should be matched to (start.emperorA+end.emperorA) / 2
Start of Vol X -> keyword -> Start of Vol X+1 
    cant associate a year with the data so we ignore this

For the start of a Vol X, add a match that is emperor type and the middle of their reign
Any year we find proceeding the emperor we ignore this, but record it for later investigation
So the end case we explicitly ignore
The second last case is simply handled as we will have a keyword that is matched between 2 things and we take the preceeding match
The last case I will ignore the number+year and take note of this occurence
