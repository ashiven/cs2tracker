from bs4 import BeautifulSoup
import requests
import csv
import datetime
import os
import configparser

####################################### READ CONFIG AND SET VARIABLES #################################################

config = configparser.ConfigParser()
config.read('config.ini')

total = 0

## sticker capsules
capsules = ['antwerp', 'stockholm', 'rio']

ant_l = int(config.get('Antwerp', 'Antwerp_Legends'))
ant_c = int(config.get('Antwerp', 'Antwerp_Challengers'))
ant_co = int(config.get('Antwerp', 'Antwerp_Contenders'))
ant_au = int(config.get('Antwerp', 'Antwerp_Champions_Autographs'))
ant = [ant_l, ant_c, ant_co, ant_au]

st_l = int(config.get('Stockholm', 'Stockholm_Legends'))
st_c = int(config.get('Stockholm', 'Stockholm_Challengers'))
st_co = int(config.get('Stockholm', 'Stockholm_Contenders'))
st_au = int(config.get('Stockholm', 'Stockholm_Champions_Autographs'))
st = [st_l, st_c, st_co, st_au]

rio_l = int(config.get('Rio', 'Rio_Legends'))
rio_c = int(config.get('Rio', 'Rio_Challengers'))
rio_co = int(config.get('Rio', 'Rio_Contenders'))
rio_au = int(config.get('Rio', 'Rio_Champions_Autographs'))
rio = [rio_l, rio_c, rio_co, rio_au]

## cases

rev_case = int(config.get('Cases', 'Revolution_Case'))
rec_case = int(config.get('Cases', 'Recoil_Case'))
dnn_case = int(config.get('Cases', 'Dreams_And_Nightmares_Case'))
rip_case = int(config.get('Cases', 'Operation_Riptide_Case'))
snk_case = int(config.get('Cases', 'Snakebite_Case'))
brk_case = int(config.get('Cases', 'Operation_Broken_Fang_Case'))
frac_case = int(config.get('Cases', 'Fracture_Case'))
chr_case = int(config.get('Cases', 'Chroma_Case'))
chr2_case = int(config.get('Cases', 'Chroma_2_Case'))
chr3_case = int(config.get('Cases', 'Chroma_3_Case'))
clt_case = int(config.get('Cases', 'Clutch_Case'))
csg_case = int(config.get('Cases', 'CSGO_Weapon_Case'))
csg2_case = int(config.get('Cases', 'CSGO_Weapon_Case_2'))
csg3_case = int(config.get('Cases', 'CSGO_Weapon_Case_3'))
cs20_case = int(config.get('Cases', 'CS20_Case'))
dgz_case = int(config.get('Cases', 'Danger_Zone_Case'))
esp_case = int(config.get('Cases', 'eSports_2013_Case'))
espw_case = int(config.get('Cases', 'eSports_2013_Winter_Case'))
esps_case = int(config.get('Cases', 'eSports_2014_Summer_Case'))
flch_case = int(config.get('Cases', 'Falchion_Case'))
gam_case = int(config.get('Cases', 'Gamma_Case'))
gam2_case = int(config.get('Cases', 'Gamma_2_Case'))
glv_case = int(config.get('Cases', 'Glove_Case'))
hrz_case = int(config.get('Cases', 'Horizon_Case'))
hnts_case = int(config.get('Cases', 'Huntsman_Weapon_Case'))
brav_case = int(config.get('Cases', 'Operation_Bravo_Case'))
brkt_case = int(config.get('Cases', 'Operation_Breakout_Weapon_Case'))
hydr_case = int(config.get('Cases', 'Operation_Hydra_Case'))
phnx_case = int(config.get('Cases', 'Operation_Phoenix_Weapon_Case'))
vngd_case = int(config.get('Cases', 'Operation_Vanguard_Weapon_Case'))
wldf_case = int(config.get('Cases', 'Operation_Wildfire_Case'))
prsm_case = int(config.get('Cases', 'Prisma_Case'))
prsm2_case = int(config.get('Cases', 'Prisma_2_Case'))
rev_case = int(config.get('Cases', 'Revolver_Case'))
shdw_case = int(config.get('Cases', 'Shadow_Case'))
shwb_case = int(config.get('Cases', 'Shattered_Web_Case'))
spec_case = int(config.get('Cases', 'Spectrum_Case'))
spec2_case = int(config.get('Cases', 'Spectrum_2_Case'))
woff_case = int(config.get('Cases', 'Winter_Offensive_Weapon_Case'))


######################################## DISPLAY CAPSULE PRICES ######################################################

for capsule in capsules:
    print(f'-------------{capsule} capsule-----------------')
    url = f'https://steamcommunity.com/market/search?q={capsule}+capsule'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['Legends', 'Challengers', 'Contenders', 'Champions Autographs']
    count = 0

    if(capsule == 'antwerp'):
        hrefs = ['https://steamcommunity.com/market/listings/730/Antwerp%202022%20Legends%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Challengers%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Contenders%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Champions%20Autograph%20Capsule']
        for href in hrefs:
            listing = soup.find('a', attrs={'href':f'{href}'})
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')

            print(*[data, '--> $' + str(int(ant[count] * float(data_raw))) + f' ({ant[count]})' ])
            total = total + (ant[count] * float(data_raw) )
            count = count + 1

    if(capsule == 'stockholm'):
        hrefs = ['https://steamcommunity.com/market/listings/730/Stockholm%202021%20Legends%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Challengers%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Contenders%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Champions%20Autograph%20Capsule']
        for href in hrefs:
            listing = soup.find('a', attrs={'href':f'{href}'})
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')

            print(*[data, '--> $' + str(int(st[count] * float(data_raw))) + f' ({st[count]})'])
            total = total + (st[count] * float(data_raw) )
            count = count + 1
        
    if(capsule == 'rio'):
        hrefs = ['https://steamcommunity.com/market/listings/730/Rio%202022%20Legends%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Challengers%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Contenders%20Sticker%20Capsule'
                ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Champions%20Autograph%20Capsule']
        for href in hrefs:
            listing = soup.find('a', attrs={'href':f'{href}'})
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')

            print(*[data, '--> $' + str(int(rio[count] * float(data_raw))) + f' ({rio[count]})' ])
            total = total + (rio[count] * float(data_raw) )
            count = count + 1

##################################### DISPLAY OTHER ITEMS ###############################################################

##################################### PRINT TOTAL #######################################################################

print('-----------------------------------')
print('Total in USD')
print(float(f'{total:.2f}'))

url2 = 'https://www.xe.com/de/currencyconverter/convert/?Amount=1&From=EUR&To=USD'
page2 = requests.get(url2)
soup2 = BeautifulSoup(page2.content, 'html.parser')
rate1 = soup2.find('div', attrs={'class':'unit-rates___StyledDiv-sc-1dk593y-0 dEqdnx'})
rate2 = rate1.text.split()
rate3 = rate2[3].replace(',', '.')
rate = float(rate3)
eur_total = rate * total
print('Total in EUR')
print(float(f'{eur_total:.2f}'))



##################################### WRITE TOTAL TO OUTPUT FILE ########################################################

filename = 'output.csv'
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d")

if not os.path.isfile(filename):
    open(filename, "w").close()

with open(filename, 'r', encoding = 'utf-8') as csvfile:
    reader = csv.reader(csvfile)
    last_row = None
    for row in reader:
        last_row = row
    if last_row is not None:
        last_date_str = last_row[0][:10]
    else:
        last_date_str = ''

if date != last_date_str:
    today = now.strftime("%Y-%m-%d %H:%M:%S")
    output1 = "{:.2f}$".format(total)
    output2 = "{:.2f}€".format(eur_total)
    with open(filename, 'a', newline = '', encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([today, output1])
        writer.writerow([today, output2])