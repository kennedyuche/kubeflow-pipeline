import pandas as pd
import numpy as np
import requests
from requests.exceptions import SSLError
import click
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import re
from azure.storage.filedatalake import DataLakeServiceClient
import configparser
from html_table_parser.parser import HTMLTableParser


config = configparser.ConfigParser()
config.read('config.cfg.template', encoding='utf-8-sig')
container_name         =  config['AZURE']['CONTAINER_NAME']
storage_account_name   =  config['AZURE']['STORAGE_ACCOUNT_NAME']
account_access_key     =  config['AZURE']['ACCOUNT_ACCESS_KEY']
storage_dir_name       =  config['STORAGE']['STORAGE_DIRECTORY_NAME']
file_name              =  config['STORAGE']['FILINGS_10K_DATA']
start_date             =  config['CLICK']['START_DATE']
end_date               =  config['CLICK']['END_DATE'] 
user_agent             =  config['CLICK']['USER_AGENT']


Edgar_Prefix = "https://www.sec.gov/Archives/"

logging.basicConfig(level=logging.INFO)

def make_master_index_urls(start_date=None, end_date=None):
    """This function creates URLs for master index 
    files for every given quarter and year. Either a start date or an end date
    could be given or both."""
    
    quarters= ['QTR1', 'QTR2', 'QTR3', 'QTR4']
    if start_date and end_date:
        start_date_converted = datetime.strptime(start_date, '%m-%d-%Y')
        end_date_converted = datetime.strptime(end_date, '%m-%d-%Y')

        start_year = start_date_converted.year 
        end_year = end_date_converted.year        
        year = range(start_year, end_year + 1)
        history = list((y, q) for y in year for q in quarters)
        logging.info('Creating master index file URLs from %s to %s' % (start_date_converted.date(), end_date_converted.date()))
        return [(Edgar_Prefix + "edgar/full-index/%s/%s/master.idx" % (h[0], h[1]))
            for h in history]
    else:
        year = [i for i in [start_date, end_date] if i][0]
        print(year)
        _year = year.year 
        quarter = 'QTR' + str(year.quarter)
        history = list((_year, quarter) for q in quarters)
        logging.info('Creating master index files URLs for %s' % (_year))
        return [(Edgar_Prefix + "edgar/full-index/%s/%s/master.idx" % (h[0], h[1])) for h in history]

def select_actual_dates(start, end, df):
    start_converted = datetime.strptime(start, '%m-%d-%Y')
    end_converted = datetime.strptime(end, '%m-%d-%Y')

    start = str(start_converted.date())
    end = str(end_converted.date())
    df = df[start : end]
    return df
    
    
def get_form_type(data, form_type):
    """This function creates a dataframe to contain each 
    filing information and gives a name to each filing"""
    
    master_data = pd.DataFrame(data)
    master_data.columns = ['CIK', 'company_name', 'form_id', 'date', 'file_url']
    master_data['date'] = pd.to_datetime(master_data['date'])
    master_data['file_name'] = master_data['file_url'].str[-24:]
    master_data_ = master_data.loc[master_data['form_id'] == form_type]
    return master_data_ 


def get_Bermuda_companies(user_agent):
    try:
        pages = np.arange(0, 1600, 100)
        headers = {'User-Agent': user_agent}
        Companies = []

        for page in pages:
            xhtml = requests.get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&State=D0&owner=exclude&match=&start=" 
                             + str(page) + "&count=100&hidefilings=0", headers=headers).text
        
            p = HTMLTableParser()
            p.feed(xhtml)
            data = p.tables
            e = pd.DataFrame(np.column_stack(data))
            e.columns = e.iloc[0]
            e = e[1:]
            Companies.append(e)
        final = pd.concat(Companies)
        return final
    except Exception:
        logging.exception("An error occured")

def read_master_index(urls, user_agent):
    """This function reads each master index file and records each filing information into a dataframe"""
    try:
        master_dataset = []
        for url in urls:
            headers = {'User-Agent': user_agent}
            content = requests.get(url, headers=headers).content
            with open('master.text', 'wb') as f:
                f.write(content)
            with open('master.text', 'rb') as f:   #read the content of the text file
                byte_data = f.read()
        
            data = byte_data.decode('latin-1').split('  ')  #decode the byte data
            master_data = []

            for index, item in enumerate(data):
                if 'ftp://ftp.sec.gov/edgar/' in item:
                    start_ind = index
            data_format = data[start_ind + 1:]  #create a new list that removes junk
            for index, item in enumerate(data_format):
                if index== 0:
                    clean_item_data = item.replace('\n', '|').split('|')
                    clean_item_data = clean_item_data[8:]
                else:
                    clean_item_data = item.replace('\n', '|').split('|')

                for index, row in enumerate(clean_item_data):
                    if '.txt' in row:   #when you find the text file
                        mini_list = clean_item_data[(index - 4): index + 1]
                        if len(mini_list) !=0:
                            mini_list[4] = Edgar_Prefix + mini_list[4]
                            master_data.append(mini_list)
            master_dataset.append(get_form_type(master_data, '10-K'))
        logging.info('Pulling 10-K filings')
    
        final_master = pd.concat(master_dataset)
        compare = get_Bermuda_companies(user_agent)
        final_master_ = pd.merge(final_master, compare, on='CIK', how='left').drop(['Company', 'State/Country'], axis=1)
        final = final_master_.sort_values(by='date')
        final_ = final.set_index('date')
        return final_
    except Exception:
        logging.exception("An error occured")

def extract_10_K_items(url, user_agent):
    headers = {"User-Agent": user_agent}
    try:
        r = requests.get(url, headers=headers)
        raw_10k = r.text
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')
        doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]
    
        document = {}
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == '10-K':
                document[doc_type] = raw_10k[doc_start:doc_end]
            
    
        regex = re.compile(r'>?(ITEM|Item)(\s|&#160;|&nbsp;|&#xa0;)([1-9]+|1A|1B|7A)(\.+|:){0,2}')
    
        try:
            matches = regex.finditer(document['10-K'])
            matches_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
            matches_df.columns = ['item', 'start', 'end']
    
            matches_df.replace('&#160;|&nbsp;|\.|>|\s|&#xa0;', '',regex=True,inplace=True)
            new_df = matches_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')

            table = []
            for i in range(len(new_df)-1):
                table.append(document['10-K'][new_df['start'].iloc[i]:new_df['start'].iloc[i+1]])
    
            new_table =[]
            for i in table:
                new_table.append(BeautifulSoup(i, 'lxml'))
        
            newer_table = []
            for i in new_table:
                newer_table.append(i.get_text("\n\n"))
        
            final_df = pd.DataFrame(newer_table)
            final_df.columns = ['Item Contents']
            final_df['file_url'] = url
            return final_df
    
        except (ValueError, KeyError) as e:
            logging.exception('An error occurred: 10-K file could not be parsed')
    
    except Exception:
        logging.exception(f'An error occured while parsing this file, {url}')

def upload_file_to_storage():
    try:
        global service_client

        service_client = DataLakeServiceClient(account_url=f"https://{storage_account_name}.dfs.core.windows.net", 
        credential=account_access_key)

        file_system_client = service_client.get_file_system_client(file_system=container_name)


        directory_client = file_system_client.get_directory_client(f"{storage_dir_name}")
        
        file_client = directory_client.create_file(f"{file_name}")
        f = open('10k_files_raw.csv','r')

        file_contents = f.read()

        file_client.upload_data(file_contents, overwrite=True)

        f.close()

        logging.info(f"{file_name} uploaded successfully")
    except Exception:
        logging.exception(f"An error occurred while uploading {file_name} to the azure data lake storage")

                
def validate_date(ctx, param, value):
    if value == "":
        return value
    try:
        value = pd.to_datetime(value, format='%m-%d-%Y')
        return value
    except ValueError:
        raise click.BadParameter("format must be in format '%m-%d-%Y'")      
        
    
# @click.command()
# @click.option("--start_date", type=click.UNPROCESSED, callback=validate_date, default="", prompt=True)
# @click.option("--end_date", type=click.UNPROCESSED, callback=validate_date, default="", prompt=True)
# @click.option("--user_agent", prompt="Enter your email address")
def main():
    logging.info("Starting")
    try:
        df = read_master_index(make_master_index_urls(start_date, end_date), user_agent)
        if start_date and end_date:
            df = select_actual_dates(start_date, end_date, df)
        mini_df = df.reset_index()
        no_of_files = len(mini_df['file_url'])
        print(f'Number of files to be extracted: {no_of_files}')
        if no_of_files > 0:
            urls = df['file_url']
            dataf = []
            for url in urls:
                parsed = extract_10_K_items(url, user_agent)
                dataf.append(parsed)
            new = pd.concat(dataf)
            new_df = pd.merge(new, df, on='file_url', how='left').drop(['form_id', 'file_name'], axis=1)
            new_df['Items'] = new_df['Item Contents'].str[:8]
            new_df['Item Contents'] = new_df['Item Contents'].str[8:]
            new_df = new_df.apply(lambda x : x.str.replace('\n', '\\n'))
            new_df = new_df[['CIK', 'company_name', 'Items', 'Item Contents', 'file_url']]
            new_df.to_csv('10k_files_raw.csv')
            upload_file_to_storage()
        else:
            print('No files found for specified period')

    except Exception as e:
        print('An error occured;', e)

if __name__ == '__main__':
    main()