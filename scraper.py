from bs4 import BeautifulSoup
import requests

capsules = ['antwerp', 'stockholm', 'rio']

total = 0

ant_l = 1200
ant_c = 3600
ant_co = 1200
ant_au = 1000
ant = [ant_l, ant_c, ant_co, ant_au]

st_l = 650
st_c = 50
st_co = 50
st_au = 250
st = [st_l, st_c, st_co, st_au]

rio_l = 500
rio_c = 500
rio_co = 750
rio_au = 250
rio = [rio_l, rio_c, rio_co, rio_au]

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