from bs4 import BeautifulSoup
import requests
import csv
import datetime
import os
import configparser
import time

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

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})

######################################## DISPLAY CAPSULE PRICES ######################################################

if(ant[0] != 0 or ant[1] != 0 or ant[2] != 0 or ant[3] != 0):
    page = session.get('https://steamcommunity.com/market/search?q=antwerp+capsule')
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']
    count = 0
    hrefs = ['https://steamcommunity.com/market/listings/730/Antwerp%202022%20Legends%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Challengers%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Contenders%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Antwerp%202022%20Champions%20Autograph%20Capsule']
    print('\033[35m------------Antwerp Capsule--------------\033[0m')
    for href in hrefs:
        if(ant[count] != 0):
            listing = soup.find('a', attrs={'href':f'{href}'})
            if listing is None:
                print('[!] Failed to load.(Too many requests)')
                break
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')
            print(*[data, '--> $' + str(round(float(ant[count] * float(data_raw)), 2)) + f' ({ant[count]})' ])
            total = total + (ant[count] * float(data_raw) )
        count = count + 1

if(st[0] != 0 or st[1] != 0 or st[2] != 0 or st[3] != 0):
    page = session.get('https://steamcommunity.com/market/search?q=stockholm+capsule')
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']
    count = 0
    hrefs = ['https://steamcommunity.com/market/listings/730/Stockholm%202021%20Legends%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Challengers%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Contenders%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Stockholm%202021%20Champions%20Autograph%20Capsule']
    print('\033[35m------------Stockholm Capsule------------\033[0m')
    for href in hrefs:
        if(st[count] != 0):
            listing = soup.find('a', attrs={'href':f'{href}'})
            if listing is None:
                print('[!] Failed to load.(Too many requests)')
                break
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')
            print(*[data, '--> $' + str(round(float(st[count] * float(data_raw)), 2)) + f' ({st[count]})'])
            total = total + (st[count] * float(data_raw) )
        count = count + 1

if(rio[0] != 0 or rio[1] != 0 or rio[2] != 0 or rio[3] != 0):
    page = session.get('https://steamcommunity.com/market/search?q=rio+capsule')
    soup = BeautifulSoup(page.content, 'html.parser')
    capsule_name = ['\033[34mLegends\033[0m', '\033[34mChallengers\033[0m', '\033[34mContenders\033[0m', '\033[34mChampions Autographs\033[0m']
    count = 0
    hrefs = ['https://steamcommunity.com/market/listings/730/Rio%202022%20Legends%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Challengers%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Contenders%20Sticker%20Capsule'
            ,'https://steamcommunity.com/market/listings/730/Rio%202022%20Champions%20Autograph%20Capsule']
    print('\033[35m------------Rio Capsule------------------\033[0m')
    for href in hrefs:
        if(rio[count] != 0):
            listing = soup.find('a', attrs={'href':f'{href}'})
            if listing is None:
                print('[!] Failed to load.(Too many requests)')
                break
            price = listing.find('span', attrs={'class':'normal_price'})
            print(capsule_name[count]) 
            data = price.text.split()[2]
            data_raw = data.replace('$', '')
            print(*[data, '--> $' + str(round(float(rio[count] * float(data_raw)), 2)) + f' ({rio[count]})' ])
            total = total + (rio[count] * float(data_raw) )
        count = count + 1

##################################### DISPLAY CASES ###############################################################


case_amounts = [rev1_case,rec_case,dnn_case,rip_case,snk_case,brk_case,frac_case,chr_case,chr2_case,chr3_case,clt_case,csg_case,csg2_case,csg3_case,cs20_case,dgz_case,
                esp_case,espw_case,esps_case,flch_case,gam_case,gam2_case,glv_case,hrz_case,hnts_case,brav_case,brkt_case,hydr_case,phnx_case,vngd_case,wldf_case,prsm_case,
                prsm2_case,rev_case,shdw_case,shwb_case,spec_case,spec2_case,woff_case]
case_names = ['Revolution Case','Recoil Case','Dreams And Nightmares Case','Operation Riptide Case','Snakebite Case','Operation Broken Fang Case','Fracture Case','Chroma Case',
                'Chroma 2 Case','Chroma 3 Case','Clutch Case','CSGO Weapon Case','CSGO Weapon Case 2','CSGO Weapon Case 3','CS20 Case','Danger Zone Case','eSports 2013 Case','eSports 2013 Winter Case',
                'eSports 2014 Summer Case','Falchion Case','Gamma Case','Gamma 2 Case','Glove Case','Horizon Case','Huntsman Weapon Case','Operation Bravo Case','Operation Breakout Weapon Case',
                'Operation Hydra Case','Operation Phoenix Weapon Case','Operation Vanguard Weapon Case','Operation Wildfire Case','Prisma Case','Prisma 2 Case','Revolver Case','Shadow Case',
                'Shattered Web Case','Spectrum Case','Spectrum 2 Case','Winter Offensive Weapon Case']
case_links = ['https://steamcommunity.com/market/search?q=revolution+case',
                'https://steamcommunity.com/market/search?q=recoil+case',
                'https://steamcommunity.com/market/search?q=dreams+and+nightmares+case',
                'https://steamcommunity.com/market/search?q=operation+riptide+case',
                'https://steamcommunity.com/market/search?q=snakebite+case',
                'https://steamcommunity.com/market/search?q=broken+fang+case',
                'https://steamcommunity.com/market/search?q=fracture+case',
                'https://steamcommunity.com/market/search?q=chroma+case',
                'https://steamcommunity.com/market/search?q=chroma+case',
                'https://steamcommunity.com/market/search?q=chroma+case',
                'https://steamcommunity.com/market/search?q=clutch+case',
                'https://steamcommunity.com/market/search?q=csgo+weapon+case',
                'https://steamcommunity.com/market/search?q=csgo+weapon+case',
                'https://steamcommunity.com/market/search?q=csgo+weapon+case',
                'https://steamcommunity.com/market/search?q=cs20+case',
                'https://steamcommunity.com/market/search?q=danger+zone+case',
                'https://steamcommunity.com/market/search?q=esports+case',
                'https://steamcommunity.com/market/search?q=esports+case',
                'https://steamcommunity.com/market/search?q=esports+case',
                'https://steamcommunity.com/market/search?q=falchion+case',
                'https://steamcommunity.com/market/search?q=gamma+case',
                'https://steamcommunity.com/market/search?q=gamma+case',
                'https://steamcommunity.com/market/search?q=glove+case',
                'https://steamcommunity.com/market/search?q=horizon+case',
                'https://steamcommunity.com/market/search?q=huntsman+weapon+case',
                'https://steamcommunity.com/market/search?q=operation+bravo+case',
                'https://steamcommunity.com/market/search?q=operation+breakout+case',
                'https://steamcommunity.com/market/search?q=operation+hydra+case',
                'https://steamcommunity.com/market/search?q=operation+phoenix+case',
                'https://steamcommunity.com/market/search?q=operation+vanguard+case',
                'https://steamcommunity.com/market/search?q=operation+wildfire+case',
                'https://steamcommunity.com/market/search?q=prisma+case',
                'https://steamcommunity.com/market/search?q=prisma+case',
                'https://steamcommunity.com/market/search?q=revolver+case',
                'https://steamcommunity.com/market/search?q=shadow+case',
                'https://steamcommunity.com/market/search?q=shattered+web+case',
                'https://steamcommunity.com/market/search?q=spectrum+case',
                'https://steamcommunity.com/market/search?q=spectrum+case',
                'https://steamcommunity.com/market/search?q=winter+offensive+case']
case_hrefs = ['https://steamcommunity.com/market/listings/730/Revolution%20Case',
                'https://steamcommunity.com/market/listings/730/Recoil%20Case',
                'https://steamcommunity.com/market/listings/730/Dreams%20%26%20Nightmares%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Riptide%20Case',
                'https://steamcommunity.com/market/listings/730/Snakebite%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Broken%20Fang%20Case',
                'https://steamcommunity.com/market/listings/730/Fracture%20Case',
                'https://steamcommunity.com/market/listings/730/Chroma%20Case',
                'https://steamcommunity.com/market/listings/730/Chroma%202%20Case',
                'https://steamcommunity.com/market/listings/730/Chroma%203%20Case',
                'https://steamcommunity.com/market/listings/730/Clutch%20Case',
                'https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case',
                'https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case%202',
                'https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case%203',
                'https://steamcommunity.com/market/listings/730/CS20%20Case',
                'https://steamcommunity.com/market/listings/730/Danger%20Zone%20Case',
                'https://steamcommunity.com/market/listings/730/eSports%202013%20Case',
                'https://steamcommunity.com/market/listings/730/eSports%202013%20Winter%20Case',
                'https://steamcommunity.com/market/listings/730/eSports%202014%20Summer%20Case',
                'https://steamcommunity.com/market/listings/730/Falchion%20Case',
                'https://steamcommunity.com/market/listings/730/Gamma%20Case',
                'https://steamcommunity.com/market/listings/730/Gamma%202%20Case',
                'https://steamcommunity.com/market/listings/730/Glove%20Case',
                'https://steamcommunity.com/market/listings/730/Horizon%20Case',
                'https://steamcommunity.com/market/listings/730/Huntsman%20Weapon%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Bravo%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Breakout%20Weapon%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Hydra%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Phoenix%20Weapon%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Vanguard%20Weapon%20Case',
                'https://steamcommunity.com/market/listings/730/Operation%20Wildfire%20Case',
                'https://steamcommunity.com/market/listings/730/Prisma%20Case',
                'https://steamcommunity.com/market/listings/730/Prisma%202%20Case',
                'https://steamcommunity.com/market/listings/730/Revolver%20Case',
                'https://steamcommunity.com/market/listings/730/Shadow%20Case',
                'https://steamcommunity.com/market/listings/730/Shattered%20Web%20Case',
                'https://steamcommunity.com/market/listings/730/Spectrum%20Case',
                'https://steamcommunity.com/market/listings/730/Spectrum%202%20Case',
                'https://steamcommunity.com/market/listings/730/Winter%20Offensive%20Weapon%20Case']

for i in range(len(case_amounts)):
    if(case_amounts[i] != 0):
        page = session.get(case_links[i])
        soup = BeautifulSoup(page.content, 'html.parser')
        listing = soup.find('a', attrs={'href':case_hrefs[i]})
        if listing is None:
            print('\033[35m' + f'------------{case_names[i]}-----------------------------------'[:41] + '\033[0m')
            print('[!] Failed to load.(Too many requests)')
            break
        price = listing.find('span', attrs={'class':'normal_price'})
        data = price.text.split()[2]
        data_raw = float(data.replace('$', ''))
        print('\033[35m' + f'------------{case_names[i]}-----------------------------------'[:41] + '\033[0m')
        print(data + ' --> $' + str(round(float(case_amounts[i] * data_raw), 2)) + ' (' + str(case_amounts[i]) + ')' )
        total += (case_amounts[i] * data_raw)
        time.sleep(1)


##################################### PRINT TOTAL #######################################################################

print('\033[32m------------USD Total--------------------\033[0m')
print('$' + str(float(f'{total:.2f}')))

url2 = 'https://www.xe.com/de/currencyconverter/convert/?Amount=1&From=EUR&To=USD'
page2 = session.get(url2)
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