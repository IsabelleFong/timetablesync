import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from ics import Calendar, Event
import pytz

# data for class schedule
week = week = datetime.today().date() + timedelta(days=7)
intake_code = "APU2F2409CS(AI)" # change this to your intake code
intake_group = "G1" # change this to your intake group

url = f"https://api.apiit.edu.my/timetable-print/index.php?Week={week}&Intake={intake_code}&Intake_Group={intake_group}&print_request=print_tt"


print("Scraping Data...")

# scrap data from the url
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")


# storing the data in a list of dictionaries
uni_classes = []
single_class = []
header_row = 0

uni_class_data = soup.find_all("td")
count = len(uni_class_data) - 6

for i in range(0, count+1, 6):
    uni_classes.append({
        "date": uni_class_data[i].get_text(strip=True),
        "time": uni_class_data[i+1].get_text(strip=True),
        "classroom": uni_class_data[i+2].get_text(strip=True),
        "location": uni_class_data[i+3].get_text(strip=True),
        "module": uni_class_data[i+4].get_text(strip=True),
        "lecturer": uni_class_data[i+5].get_text(strip=True)
    })

print("Data Scraped Successfully")   

print("Creating ICS File...")

#create ics file
c = Calendar()

time_zone = pytz.timezone("America/Los_Angeles")

file_name = "university.ics"

# Define the fixed offset time zone for PST (-08:00)
pst = timezone(timedelta(hours=+8))

for uni_class in uni_classes:
    e = Event()
    e.name = uni_class["module"]
    
    # reformat the date and time to be in the correct format    
    begin_datetime = uni_class["date"][5:] + " " + uni_class["time"].split(" - ")[0]
    end_datetime = uni_class["date"][5:] + " " + uni_class["time"].split(" - ")[1]

    # parse the date and time zone
    start_dt = datetime.strptime(begin_datetime, "%d-%b-%Y %H:%M")
    end_dt = datetime.strptime(end_datetime, "%d-%b-%Y %H:%M")
    
    # Manually set the time zone to PST (-08:00)
    start_dt = start_dt.replace(tzinfo=pst)
    end_dt = end_dt.replace(tzinfo=pst)
    
    formatted_begin = start_dt.strftime("%Y-%m-%d %H:%M:%S%z")
    formatted_end = end_dt.strftime("%Y-%m-%d %H:%M:%S%z")
    
    e.begin = formatted_begin
    e.end = formatted_end
    
    e.location = uni_class["classroom"] + " | " + uni_class["location"]
    c.events.add(e)


with open(file_name, 'w') as my_file:
    my_file.writelines(c.serialize_iter())
    
print("ICS File Created Successfully")