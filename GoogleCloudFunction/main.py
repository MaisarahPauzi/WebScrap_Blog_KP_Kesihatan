'''
Rename your Google Cloud Function to: update_death_case
'''
from google.cloud import storage
import io 
import csv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests

# define month name in bahasa Malaysia
months_name = {
    1: 'januari',
    2: 'februari',
    3: 'mac',
    4: 'april',
    5: 'mei',
    6: 'jun',
    7: 'julai',
    8: 'ogos',
    9: 'september',
    10: 'oktober',
    11: 'november',
    12: 'disember'
}

def generate_csv(rows, filepath):
  with open(filepath, mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for row in rows:
      arr = []
      columns = row.findAll('td')
      for column in columns:
        arr.append(column.text)
      writer.writerow(arr)


def update_death_case(request):
  # today's day & month & year
  year = datetime.now().year
  month = datetime.now().month
  day = datetime.now().day

  URL = f"https://kpkesihatan.com/{year}/{month}/{day}/kenyataan-akhbar-kpk-{day}-{months_name[month]}-{year}-situasi-semasa-jangkitan-penyakit-coronavirus-2019-covid-19-di-malaysia"
  # get request
  response = requests.get(URL)
  if response.status_code == 200:
    html_text = response.text

    # scrap all tables
    soup = BeautifulSoup(html_text)
    tables = soup.findAll('table')

    # get table of covid death
    selected_table = ''

    for table in tables:
      rows = table.findAll('tr')
      for row in rows:
        columns = row.findAll('td')
        for column in columns:
          if 'Kes kematian' in column.text or 'No. Kematian' in column.text:
            selected_table = table
          

    # generate file
    if selected_table != '':
        storage_client = storage.Client()
        bucket = storage_client.get_bucket("datacovidscrap")
        my_file = bucket.blob(f'Data kematian covid {day}-{month}-{year}.csv')
        rows = selected_table.findAll('tr')
        filepath = f'/tmp/data kematian covid {day}-{month}-{year}.csv'
        generate_csv(rows, filepath)
        my_file.upload_from_filename(filepath)
        my_file.make_public()
        
    else:
        return f'No death report on this date: {day}/{month}/{year}'
  else:
    return 'Unable to connect to URL'
