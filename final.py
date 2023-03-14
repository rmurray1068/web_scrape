import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import matplotlib.pyplot as plt
import re
import random as rnd

#this program will scrape data from wikipedia on massacres, clean it, and turn
# it into dataclass objects. we will then use the mathplot library to display the results

@dataclass
class Event:
    name: str
    date: str
    deaths: str
    description: str


def get_data()-> BeautifulSoup:
    resp = requests.get("https://en.wikipedia.org/wiki/List_of_massacres_in_Ireland")
    return BeautifulSoup(resp.content, "html.parser")

test = get_data()

table = test.find_all('tr')

table_cleaned = table[3:57]

def convert_to_num(s: str)-> bool:
    try:
        int(s)
        return True
    except:
        return False

def scrape_table(soup: list)-> list:
    #takes in the list of soup objects and creates a list of event objects
    event_list = []
    for row in soup:
        td = row.find_all('td')
        date = td[0].text
        name = td[1].text
        deaths = td[3].text.split('\u2013')[-1].split('-')[-1]
        description = td[5].text
        #using regular expersions to filer just 4 digit or 3 digit years
        year = re.search(r"\d{4}", date)
        if year == None:
            year = re.search(r"\d{3}", date)
        if year == None:
            continue
        year = year.group(0)

        event_list.append(Event(name.strip(), year.strip(),
        deaths.strip().replace(',', '').replace('~', '').replace('+', ''),
        description.strip()))
    #checking that the deaths can be converted to a int
    for event in event_list:
        if convert_to_num(event.deaths) == False:
            event_list.remove(event)
    
    #turning the deaths into ints here because the strings have now been cleaned
    for event in event_list:
        event.deaths = int(event.deaths)
    return event_list

the_data = scrape_table(table_cleaned)

##########################################
# data analysis
##########################################
pre_modern_list = []
modern_list = []
worst_event = []

for item in the_data:
    if int(item.date) < 1970:
        pre_modern_list.append(item)
    modern_list.append(item)

name = None
num = 0

for item in the_data:
    if item.deaths > num:
        num = item.deaths
        name = item
worst_event.append(name)

num_modern_events = len(modern_list)
num_pre_modern_events = len(pre_modern_list)



##########################################
# start of pyplot work
##########################################

x_vals = []
y_vals = []
values_dict = {}

#collating the data into a dictionary
for row in the_data:
    if row.date not in values_dict:
        values_dict[row.date] = row.deaths
    values_dict[row.date] += row.deaths

#using the dictionary to fill the x/y arrays
for date, value in values_dict.items():
    x_vals.append(date)
    y_vals.append(value)

#Main Plot
plt.rcParams['xtick.major.pad']='8'
plt.plot(x_vals, y_vals)
plt.title('Massacres in Ireland by Year')
plt.xlabel('Years')
plt.ylabel('Deaths')
plt.text(9, 23000, '1641 Rebellion')
plt.text(12, 16000, 'Cromwellian Reconquest')
plt.text(15, 150, 'IRA actions during the "troubles"')
plt.xticks(fontsize=14, rotation=90)
plt.show()
# plt.close()
#The large plot doesnt show the nuance
#during the modern era because of scale

modern_era_x_vals = []
modern_era_y_vals = []

#grabbing the data post 1970
for date, value in values_dict.items():
    if int(date) > 1970:
        modern_era_x_vals.append(date)
        modern_era_y_vals.append(value)

 
plt.plot(modern_era_x_vals, modern_era_y_vals)
plt.title('IRA Actions A.K.A "the troubles"')
plt.xlabel('Years')
plt.ylabel('Deaths')
# plt.show()
# plt.close()

worst_year = max(values_dict, key=values_dict.get)

print('The worst year in terms of casualties was', worst_year)
print('The Pre-modern era had only', num_pre_modern_events, 'events compared with the modern era which had', num_modern_events, 'events')
print('The worst event was', worst_event[0].name,'.', worst_event[0].description)