'''
Created on 09.04.2019
Extrahiert Daten von von Hotel URL aus TripAdvisor
@author: Matthias
'''

import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
from datetime import datetime


connection = mysql.connector.connect(host='localhost',
                         #database='test190415',!!!
                         #database='demo',
                         database="demoii",
                         #database='Masterarbeit',
                         user='root')
                         #password='123')

db_Info = connection.get_server_info()
print("Connected to MySQL database... MySQL Server version on ",db_Info)
cursor = connection.cursor()

# Methode um Daten in ta_hotel einzufuegen
def store_hotel_data (hotelData):
    cursor.execute("INSERT INTO ta_hotel (HotelName, HotelUrl, HotelClass) VALUES (%s,%s,%s)",(hotelData))
    connection.commit()
    
# Methode um Daten in ta_bewertungen einzufuegen
def store_bewertungs_data (bewertungsData):
    cursor.execute("INSERT INTO ta_bewertungen (ReviewText,ReviewSterne,ReviewStayDate,HotelID) VALUES (%s,%s,%s,%s)",(bewertungsData))
    connection.commit()
    
# Methode um Daten in ta_user einzufuegen
def store_user_information(userInformation):
    #print (userInformation)
    cursor.execute("INSERT INTO ta_user (UserName, UserCountry, UserSubmittedReviews, BewertungenID ) VALUES (%s,%s,%s,%s)",(userInformation))
    connection.commit()
    
#Methode um zu Pruefen, ob Datensatz bereits vorhanden
def data_set_available(title):
        cursor.execute("SELECT HotelName, COUNT(*) FROM ta_hotel WHERE HotelName = %s GROUP BY HotelName", (title,))
        cursor.fetchone()
        # gets the number of rows affected by the command executed
        row_count = cursor.rowcount
        print ("number of affected rows: {}".format(row_count))
        if row_count < 1:
            print ("It Does Not Exist")
            return row_count
        else:
            print ("It Exist")
            return row_count

#Crawler
def max_seitenzahl_hotels():
        url = "https://www.tripadvisor.co.uk/Hotels-g187782-Sorrento_Province_of_Naples_Campania-Hotels.html"
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text,"html.parser")
        helpPageNumbers = ""
        for item_name in soup.findAll('a', {'class': 'pageNum'}):
           helpPageNumbers = item_name.text
        pageNumbers = int(helpPageNumbers)
        return ((pageNumbers)*30)

def max_seitenzahl_bewertungen(item_url):
        source_code = requests.get(item_url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text,"html.parser")
        pageNumbers = 0
        for item_name in soup.findAll('a', {'class': 'pageNum'}):
            pageNumbers = int(item_name.text)
        #pageNumbers = int(helpPageNumbers)
        return (pageNumbers)
'''
Funktionsbeschreibung
-
-
'''

def get_hotel_class(item_url):
    source_code = requests.get(item_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text,"html.parser")
    result = 0
    for item_name in soup.findAll('span', {'class': 'ui_star_rating star_50 hotels-hotel-review-about-with-photos-goodtoknow-StarRating__stars--3tYZG'}):
        result = 5
    for item_name in soup.findAll('span', {'class': 'ui_star_rating star_40 hotels-hotel-review-about-with-photos-goodtoknow-StarRating__stars--3tYZG'}):
        result = 4
    for item_name in soup.findAll('span', {'class': 'ui_star_rating star_30 hotels-hotel-review-about-with-photos-goodtoknow-StarRating__stars--3tYZG'}):
        result = 3
    for item_name in soup.findAll('span', {'class': 'ui_star_rating star_20 hotels-hotel-review-about-with-photos-goodtoknow-StarRating__stars--3tYZG'}):
        result = 2
    return result

'''
Funktionsbeschreibung:
- Extrahiert Namen, Wohnort und Anzahl der bereits getaetigten Bewertungen des Users
Uebergabeparameter:
- BeatifulSoup Objet
- BewertungsID
''' 
def get_user_information(soupI, BewertungenID):
    containerI = soupI.find("div", {'class': 'info_text'})
    children = containerI.findChildren ("div")
    userName=""
    userLocation=""
    userSubmittedReviews = 0
    for child in children:
        userName = child.text
        break
    childrenI = containerI.findChildren ("div", {"class": "userLoc"})
    for child in childrenI:
        userLocation =  child.text
        break
    containerII = soupI.find("div", {'class': 'member_info'})
    childrenII = containerII.findChildren ("span", {"class": "badgetext"})
    for child in childrenII:
        userSubmittedReviews = child.text
        break
    #SQL Anbindung
    userInformaiton = [userName,userLocation,userSubmittedReviews, BewertungenID]
    store_user_information(userInformaiton)#
'''
Funktionsbeschreibung:
- Laedt die URL des ersten Reviews (Vergleibar mit Klick auf die erste Bewertung)
- Extrahiert den Text der Bewertung, die Anzahl der Sterne sowie ein Zeitstempel
Uebergabeparameter:
- Maximale Anzahl an zu crawlenden Bewertungen
- Url zu der Bewertung (item_url)
- HotelID
''' 
def get_single_textrating(anzahlBewertungen, item_url, HotelID):
    page = 5
    while (page < anzahlBewertungen):
        item_urlI, item_urlII = item_url.split("Reviews",1)
        item_urlHelp = item_urlI + "Reviews-or" + str(page) + item_urlII
        source_code = requests.get(item_urlHelp)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text,"html.parser")
        print("__"+ item_urlHelp) 
        #Jeder Bewertung wird einzeln geoeffnet
        i=0
        for a in soup.findAll('a', attrs={'href': re.compile("^/ShowUserReviews-")}):
            href = "http://www.tripadvisor.co.uk/"+ a['href']
            print (href)
            source_codeI = requests.get(href)
            plain_textI = source_codeI.text
            soupI = BeautifulSoup(plain_textI.encode("utf-8"),"html.parser")
            #Der ganze Text jeder Bewertung wird geoeffnet
            for item_name in soupI.findAll('span', {'class': 'fullText'}):
                reviewText = (item_name.text)
                print("Hier waere eine Bewertung")
                #print(reviewText)
            #Die vergebenen Sterne extrahieren
            for container in soupI.findAll("div", {"ui_column is-10-desktop is-12-tablet is-12-mobile"}):
                rating = container.span["class"]
                reviewSterne = (int((str(rating)[-4:])[:2])/10)
                print (reviewSterne)
                break
            #Datum wird extrahiert
            for containerI in soupI.findAll("span", {"class":"ratingDate"}):
                date = containerI.get("title")
                reviewStayDate = datetime.strptime(date, '%d %B %Y').date()
                #print (date_object)
                #MySQL Anbindung
                bewertungsData = [reviewText,reviewSterne,reviewStayDate,HotelID]
                store_bewertungs_data(bewertungsData)#
                break
            #Aufruf der Methode Userinformationen
            BewertungenID = cursor.lastrowid
            get_user_information(soupI, BewertungenID)
            #Fuenf Bewertungen pro Seite werden ausgelesen
            i+=1
            if i==5:
                break
        page +=5
'''
Funktionsbeschreibung:
- Steuert den allgemeinen Ablauf des Programms
- Start Url wird initialisiert
- Speichert HTML-Code der Start Url in BeautifulSoup Objekt:
- max_seitenzahl: Anzahl an Hotels welche gecrawlt werden sollen
'''
        
def trip_spider():
    page = 30
    max_seitenzahl = max_seitenzahl_hotels()
    while (page < max_seitenzahl): 
        url = "https://www.tripadvisor.co.uk/Hotels-g187782-oa" + str(page) + "-Sorrento_Province_of_Naples_Campania-Hotels.html"
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text,"html.parser")
        for link in soup.findAll('a', {'class': 'property_title prominent'}):
            item_url = 'https://www.tripadvisor.co.uk' + link.get('href')
            #item_url = "https://www.tripadvisor.co.uk/Attraction_Review-g187782-d1439265-Reviews-Spa_Ulysse-Sorrento_Province_of_Naples_Campania.html"
            title = link.string
            #title = "Spa Ulysse"
            anzahlBewertungen = (max_seitenzahl_bewertungen(item_url)*5)
            hotel_class = get_hotel_class(item_url)
            #Pruefe ob maximale Seitenzahl vorhanden und sterne zwischen 3 und 4
            if ((anzahlBewertungen >= 1) and (3 <= hotel_class <= 4)):
                print (anzahlBewertungen)
                print (hotel_class)
                print (title )
                #MySQL Anbindung, abspeicherung der Hoteldaten  
                #Pruefe ob Hotel bereits abgespeichert. Wenn nicht, Hotel wird abgespeichert
                if (data_set_available(title.strip()) < 1):#<
                    hotelData = [title.strip(),item_url.strip(), hotel_class]
                    #hotelData = [title, item_url, hotel_class]
                    store_hotel_data (hotelData)#
                    HotelID = cursor.lastrowid
                    get_single_textrating(anzahlBewertungen, item_url, HotelID)
                else: 
                    print ("Hotel: " + title + "ist bereits vorhanden")
            else:
                print("Seitenzahl Bewertungen 0 oder Sterne Anzahl nicht zwischen 3 und 4")     
        page+=30

'''Startet den Crawlvorgang'''
trip_spider()
