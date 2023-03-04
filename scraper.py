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
capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']

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

rev1_case = int(config.get('Cases', 'Revolution_Case'))
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

if(ant[0] != 0 or ant[1] != 0 or ant[2] != 0 or ant[3] != 0):
    url = f'https://steamcommunity.com/market/search?q=antwerp+capsule'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']
    count = 0
    print('\033[35m------------Antwerp Capsule--------------\033[0m')
    hrefs = ['https://steamcommunity.com/market/listings/730/Antwerp%202022%20Legends%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Challengers%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Contenders%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Champions%20Autograph%20Capsule']
    for href in hrefs:
        if(ant[count] != 0):
            listing = soup.find('a', attrs={'href':f'{href}'})
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')
            print(*[data, '--> $' + str(int(ant[count] * float(data_raw))) + f' ({ant[count]})' ])
            total = total + (ant[count] * float(data_raw) )
        count = count + 1

if(st[0] != 0 or st[1] != 0 or st[2] != 0 or st[3] != 0):
    url = f'https://steamcommunity.com/market/search?q=stockholm+capsule'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']
    count = 0
    print('\033[35m------------Stockholm Capsule------------\033[0m')
    hrefs = ['https://steamcommunity.com/market/listings/730/Stockholm%202021%20Legends%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Challengers%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Contenders%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Champions%20Autograph%20Capsule']
    for href in hrefs:
        if(st[count] != 0):
            listing = soup.find('a', attrs={'href':f'{href}'})
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')
            print(*[data, '--> $' + str(int(st[count] * float(data_raw))) + f' ({st[count]})'])
            total = total + (st[count] * float(data_raw) )
        count = count + 1

if(rio[0] != 0 or rio[1] != 0 or rio[2] != 0 or rio[3] != 0):
    url = f'https://steamcommunity.com/market/search?q=rio+capsule'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']
    count = 0
    print('\033[35m------------Rio Capsule------------------\033[0m')
    hrefs = ['https://steamcommunity.com/market/listings/730/Rio%202022%20Legends%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Challengers%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Contenders%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Champions%20Autograph%20Capsule']
    for href in hrefs:
        if(rio[count] != 0):
            listing = soup.find('a', attrs={'href':f'{href}'})
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')
            print(*[data, '--> $' + str(int(rio[count] * float(data_raw))) + f' ({rio[count]})' ])
            total = total + (rio[count] * float(data_raw) )
        count = count + 1

##################################### DISPLAY CASES ###############################################################

/*
case_amounts = []
case_names = []
case_links = []
case_hrefs = []

for i in range(case_amounts.length):
	if(case_amounts[i] != 0):
    page = requests.get(case_links[i])
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':f'{case_hrefs[i]}')
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m' + f'------------{case_names[i]}------------------'[:41] + '\033[0m')
    print(data + ' --> $' + str(int(case_amounts[i] * data_raw)) + ' (' + str(case_amounts[i]) + ')' )
    total += (case_amounts[i] * data_raw)
*/

if(rev1_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=revolution+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Revolution Case--------------\033[0m')
    print(data + ' --> $' + str(int(rev1_case * data_raw)) + ' (' + str(rev1_case) + ')' )
    total += (rev1_case * data_raw)

if(rec_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=recoil+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Recoil%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Recoil Case------------------\033[0m')
    print(data + ' --> $' + str(int(rec_case * data_raw)) + ' (' + str(rec_case) + ')' )
    total += (rec_case * data_raw)

if(dnn_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=dreams+and+nightmares+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Dreams & Nightmares Case-----\033[0m')
    print(data + ' --> $' + str(int(dnn_case * data_raw)) + ' (' + str(dnn_case) + ')' )
    total += (dnn_case * data_raw)

if(rip_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+riptide+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Riptide Case-----------------\033[0m')
    print(data + ' --> $' + str(int(rip_case * data_raw)) + ' (' + str(rip_case) + ')' )
    total += (rip_case * data_raw)

if(snk_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=snakebite+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Snakebite Case---------------\033[0m')
    print(data + ' --> $' + str(int(snk_case * data_raw)) + ' (' + str(snk_case) + ')' )
    total += (snk_case * data_raw)

if(brk_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=broken+fang+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Broken Fang Case-------------\033[0m')
    print(data + ' --> $' + str(int(brk_case * data_raw)) + ' (' + str(brk_case) + ')' )
    total += (brk_case * data_raw)

if(frac_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=fracture+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Fracture Case----------------\033[0m')
    print(data + ' --> $' + str(int(frac_case * data_raw)) + ' (' + str(frac_case) + ')' )
    total += (frac_case * data_raw)

if(chr_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=chroma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Chroma%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Chroma Case------------------\033[0m')
    print(data + ' --> $' + str(int(chr_case * data_raw)) + ' (' + str(chr_case) + ')' )
    total += (chr_case * data_raw)

if(chr2_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=chroma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Chroma%202%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Chroma 2 Case----------------\033[0m')
    print(data + ' --> $' + str(int(chr2_case * data_raw)) + ' (' + str(chr2_case) + ')' )
    total += (chr2_case * data_raw)

if(chr3_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=chroma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Chroma%203%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Chroma 3 Case----------------\033[0m')
    print(data + ' --> $' + str(int(chr3_case * data_raw)) + ' (' + str(chr3_case) + ')' )
    total += (chr3_case * data_raw)

if(clt_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=clutch+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Clutch%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Clutch Case------------------\033[0m')
    print(data + ' --> $' + str(int(clt_case * data_raw)) + ' (' + str(clt_case) + ')' )
    total += (clt_case * data_raw)

if(csg_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=csgo+weapon+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------CSGO Weapon Case-------------\033[0m')
    print(data + ' --> $' + str(int(csg_case * data_raw)) + ' (' + str(csg_case) + ')' )
    total += (csg_case * data_raw)

if(csg2_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=csgo+weapon+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case%202'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------CSGO Weapon Case 2-----------\033[0m')
    print(data + ' --> $' + str(int(csg2_case * data_raw)) + ' (' + str(csg2_case) + ')' )
    total += (csg2_case * data_raw)

if(csg3_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=csgo+weapon+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case%203'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------CSGO Weapon Case 3-----------\033[0m')
    print(data + ' --> $' + str(int(csg3_case * data_raw)) + ' (' + str(csg3_case) + ')' )
    total += (csg3_case * data_raw)

if(cs20_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=cs20+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/CS20%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------CS20 Case--------------------\033[0m')
    print(data + ' --> $' + str(int(cs20_case * data_raw)) + ' (' + str(cs20_case) + ')' )
    total += (cs20_case * data_raw)

if(dgz_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=danger+zone+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Danger%20Zone%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Danger Zone Case-------------\033[0m')
    print(data + ' --> $' + str(int(dgz_case * data_raw)) + ' (' + str(dgz_case) + ')' )
    total += (dgz_case * data_raw)

if(esp_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=esports+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/eSports%202013%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------eSports 2013 Case------------\033[0m')
    print(data + ' --> $' + str(int(esp_case * data_raw)) + ' (' + str(esp_case) + ')' )
    total += (esp_case * data_raw)

if(espw_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=esports+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/eSports%202013%20Winter%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------eSports 2013 Winter Case-----\033[0m')
    print(data + ' --> $' + str(int(espw_case * data_raw)) + ' (' + str(espw_case) + ')' )
    total += (espw_case * data_raw)

if(esps_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=esports+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/eSports%202014%20Summer%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------eSports 2014 Summer Case-----\033[0m')
    print(data + ' --> $' + str(int(esps_case * data_raw)) + ' (' + str(esps_case) + ')' )
    total += (esps_case * data_raw)

if(flch_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=falchion+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Falchion%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Falchion Case----------------\033[0m')
    print(data + ' --> $' + str(int(flch_case * data_raw)) + ' (' + str(flch_case) + ')' )
    total += (flch_case * data_raw)

if(gam_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=gamma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Gamma%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Gamma Case-------------------\033[0m')
    print(data + ' --> $' + str(int(gam_case * data_raw)) + ' (' + str(gam_case) + ')' )
    total += (gam_case * data_raw)

if(gam2_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=gamma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Gamma%202%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Gamma 2 Case-----------------\033[0m')
    print(data + ' --> $' + str(int(gam2_case * data_raw)) + ' (' + str(gam2_case) + ')' )
    total += (gam2_case * data_raw)

if(glv_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=glove+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Glove%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Glove Case-------------------\033[0m')
    print(data + ' --> $' + str(int(glv_case * data_raw)) + ' (' + str(glv_case) + ')' )
    total += (glv_case * data_raw)

if(hrz_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=horizon+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Horizon%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Horizon Case-----------------\033[0m')
    print(data + ' --> $' + str(int(hrz_case * data_raw)) + ' (' + str(hrz_case) + ')' )
    total += (hrz_case * data_raw)

if(hnts_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=huntsman+weapon+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Huntsman Case----------------\033[0m')
    print(data + ' --> $' + str(int(hnts_case * data_raw)) + ' (' + str(hnts_case) + ')' )
    total += (hnts_case * data_raw)

if(brav_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+bravo+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Operation Bravo Case---------\033[0m')
    print(data + ' --> $' + str(int(brav_case * data_raw)) + ' (' + str(brav_case) + ')' )
    total += (brav_case * data_raw)

if(brkt_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+breakout+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Operation%20Breakout%20Weapon%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Operation Breakout Case------\033[0m')
    print(data + ' --> $' + str(int(brkt_case * data_raw)) + ' (' + str(brkt_case) + ')' )
    total += (brkt_case * data_raw)

if(hydr_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+hydra+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Operation%20Hydra%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Operation Hydra Case---------\033[0m')
    print(data + ' --> $' + str(int(hydr_case * data_raw)) + ' (' + str(hydr_case) + ')' )
    total += (hydr_case * data_raw)

if(phnx_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+phoenix+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Operation%20Phoenix%20Weapon%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Operation Phoenix Case-------\033[0m')
    print(data + ' --> $' + str(int(phnx_case * data_raw)) + ' (' + str(phnx_case) + ')' )
    total += (phnx_case * data_raw)

if(vngd_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+vanguard+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Operation%20Vanguard%20Weapon%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Operation Vanguard Case------\033[0m')
    print(data + ' --> $' + str(int(vngd_case * data_raw)) + ' (' + str(vngd_case) + ')' )
    total += (vngd_case * data_raw)

if(wldf_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=operation+wildfire+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Operation%20Wildfire%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Operation Wildfire Case------\033[0m')
    print(data + ' --> $' + str(int(wldf_case * data_raw)) + ' (' + str(wldf_case) + ')' )
    total += (wldf_case * data_raw)

if(prsm_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=prisma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Prisma%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Prisma Case------------------\033[0m')
    print(data + ' --> $' + str(int(prsm_case * data_raw)) + ' (' + str(prsm_case) + ')' )
    total += (prsm_case * data_raw)

if(prsm2_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=prisma+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Prisma%202%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Prisma 2 Case----------------\033[0m')
    print(data + ' --> $' + str(int(prsm2_case * data_raw)) + ' (' + str(prsm2_case) + ')' )
    total += (prsm2_case * data_raw)

if(rev_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=revolver+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Revolver%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Revolver Case----------------\033[0m')
    print(data + ' --> $' + str(int(rev_case * data_raw)) + ' (' + str(rev_case) + ')' )
    total += (rev_case * data_raw)

if(shdw_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=shadow+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Shadow%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Shadow Case------------------\033[0m')
    print(data + ' --> $' + str(int(shdw_case * data_raw)) + ' (' + str(shdw_case) + ')' )
    total += (shdw_case * data_raw)

if(shwb_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=shattered+web+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Shattered Web Case-----------\033[0m')
    print(data + ' --> $' + str(int(shwb_case * data_raw)) + ' (' + str(shwb_case) + ')' )
    total += (shwb_case * data_raw)

if(spec_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=spectrum+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Spectrum%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Spectrum Case----------------\033[0m')
    print(data + ' --> $' + str(int(spec_case * data_raw)) + ' (' + str(spec_case) + ')' )
    total += (spec_case * data_raw)

if(spec2_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=spectrum+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Spectrum%202%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Spectrum 2 Case--------------\033[0m')
    print(data + ' --> $' + str(int(spec2_case * data_raw)) + ' (' + str(spec2_case) + ')' )
    total += (spec2_case * data_raw)

if(woff_case != 0):
    page = requests.get('https://steamcommunity.com/market/search?q=winter+offensive+case')
    soup = BeautifulSoup(page.content, 'html.parser')
    listing = soup.find('a', attrs={'href':'https://steamcommunity.com/market/listings/730/Winter%20Offensive%20Weapon%20Case'})
    price = listing.find('span', attrs={'class':'normal_price'})
    data = price.text.split()[2]
    data_raw = float(data.replace('$', ''))
    print('\033[35m------------Winter Offensive Case--------\033[0m')
    print(data + ' --> $' + str(int(woff_case * data_raw)) + ' (' + str(woff_case) + ')' )
    total += (woff_case * data_raw)

##################################### PRINT TOTAL #######################################################################

print('\033[32m------------USD Total--------------------\033[0m')
print('$' + str(float(f'{total:.2f}')))

url2 = 'https://www.xe.com/de/currencyconverter/convert/?Amount=1&From=EUR&To=USD'
page2 = requests.get(url2)
soup2 = BeautifulSoup(page2.content, 'html.parser')
rate1 = soup2.find('div', attrs={'class':'unit-rates___StyledDiv-sc-1dk593y-0 dEqdnx'})
rate2 = rate1.text.split()
rate3 = rate2[3].replace(',', '.')
rate = float(rate3)
eur_total = rate * total
print('\033[32m------------EUR Total--------------------\033[0m')
print('€' + str(float(f'{eur_total:.2f}')))
print('\033[32m-----------------------------------------\033[0m')



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