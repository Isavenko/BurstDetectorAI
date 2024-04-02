import bs4
import requests

# This parses a .txt file contaning all burst events. The .txt files are manually downloaded from the online database.
# This file is then used later when downloading the data

# === DOWNLOAD ===
# url = 'http://soleil.i4ds.ch/solarradio/data/BurstLists/2010-yyyy_Monstein/2023/'

# response = requests.get(url)
# data = bs4.BeautifulSoup(response.text, 'html.parser')
# for i in range(5, len(data.find_all('a'))):
#     l = data.find_all('a')[i]
#     response = requests.get(url+l['href'])
#     filename = l.get_text('href')
#     print(filename) 

#     with open(f'burstList2023/{filename}', mode='wb') as f1:
#         f1.write(response.content)
        
bursts = [] # format [[(start), (end), type, [station1, station2, ...]], [...], [...]]

# for i in range(12):
#     if i < 9:
#         with open(f'burstList2023/e-CALLISTO_2023_0{i+1}.txt', mode = 'r') as f:  
#             for line in [line for line in f.readlines()[8:] if '2023' in line]:
#                 lines.append(line) 
#     else:
#         with open(f'burstList2023/e-CALLISTO_2023_{i+1}.txt', mode = 'r') as f:  
#             for line in [line for line in f.readlines()[8:] if '2023' in line]:
#                 lines.append(line) 
# with open('burstList2023/bursts.txt', mode='w') as f:
#     f.truncate()
#     for line in lines:
#         f.write(line)



# === CLEANUP ===
# file = open('burstList2023/bursts.txt', 'r')
# text = file.read()
# file.close()

# text = text.replace('+', '')

# file = open('burstList2023/bursts.txt', 'w')
# file.write(text)
# file.close()

def getEvents():
    with open('burstData/bursts.txt', mode='r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            try:
                line = lines[i].split('\t')
                year = int(line[0][0:4])
                month = int(line[0][4:6])
                day = int(line[0][6:8])
                hourS = int(line[1].split('-')[0].split(':')[0])
                minuteS = int(line[1].split('-')[0].split(':')[1])
                hourE = int(line[1].split('-')[1].split(':')[0])
                minuteE = int(line[1].split('-')[1].split(':')[1])
                
                start = (year, month, day, hourS, minuteS)
                end = (year, month, day, hourE, minuteE)
                
                bType = line[2]
                stations = line[3].split(',')
                stations[-1] = stations[-1].replace('\n', '')
                stations = [station.strip() for station in stations]
                burst = [start, end, bType, stations]
                

                bursts.append(burst)
            except:
                continue
    return bursts

getEvents()
# for burst in bursts:
#     print(burst)
        