# import all libraries
from datetime import datetime

from data_scrape.Scrap.ScrapMainPage import ScrapMainPage
from data_scrape.Scrap.ScrapBook import ScrapBook

main_url = "https://books.toscrape.com/"
print("Start the Scrape - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

#Scrap Main Page Info and get all books url
all_books = []
scrapMainPage = ScrapMainPage(main_url)
all_books_url = scrapMainPage.get_all_books_url()

print("--------------------------------")
print("Scrape - Read all Books URL - " + str(len(all_books_url)) + " - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("--------------------------------")

#Scrap Book Info , get all books info and save to CSV
scrapBook = ScrapBook(main_url)
scrapBook.get_all_books_info(all_books_url)

print("--------------------------------")
print("Finish the Scrape - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("--------------------------------")