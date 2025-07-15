import csv

from sklearn.model_selection import train_test_split
from Scrap.Scrap import Scrap
from bs4 import BeautifulSoup, Tag
from model.book import Book
from typing import Optional
from decimal import Decimal
import re

class ScrapBook(Scrap):
    main_url = ""
    
    # Dictionary for converting text numbers to integers
    NUMBER_MAPPING = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
    }
    
    def __init__(self, main_url: str):
        self.main_url = main_url

    def get_all_books_info(self, all_books_url: list[str]):
        """Get information for all books from their URLs.
        
        Args:
            all_books_url: List of URLs for each book to scrape
            
        Returns:
            List of Book objects containing the scraped information
        """
        all_books_info = []
        book_url_index = 0
        for book_url in all_books_url:
            book_info = self.get_book_info(book_url)

            if book_info:
                all_books_info.append(book_info)

            book_url_index += 1
            print("Scrape - Read Book Info " + str(book_url_index) + " - " + book_url)
        
        train, test = train_test_split(all_books_info, test_size=0.2, random_state=42)
        self.save_books_info_to_csv(all_books_info, "books")
        self.save_books_info_to_csv(train, "books_train")
        self.save_books_info_to_csv(test, "books_test")

    def get_book_info(self, book_url: str) -> Optional[Book]:
        """Get information for a single book from its URL.
        
        Args:
            book_url: URL of the book to scrape
            
        Returns:
            Book object containing the scraped information
        """
        try:
            # Get the book info page content
            content = self.get_page_content(book_url)
            book_info_page = BeautifulSoup(content, "html.parser")
            
            # Mount the book info
            return self.mount_book_info(book_url, book_info_page)
        except Exception as e:
            print(f"Error getting book info from {book_url}: {e}")
            return None

    def mount_book_info(self, book_url: str, book_info_page: BeautifulSoup) -> Book:
        """Extract book information from the parsed HTML.
        
        Args:
            book_info_page: BeautifulSoup Tag containing the book information
            
        Returns:
            Book object containing the extracted information
        """
        book = Book(
            id="",
            author="",
            year=0,
            title="",
            category="",
            stock=1,
            price=Decimal('0'),
            rating=0,
        )
        
        # Get Book ID
        try:
            aux_book_id = book_url.split("/")[-2]
            book.id = aux_book_id.split("_")[-1]
        except (IndexError, AttributeError):
            book.id = "unknown"

        # Get Book Author and Year (not available in the page)
        book.author = ""
        book.year = 0

        # Get Book Category and Title
        try:
            breadcrumb = book_info_page.find("ul", class_="breadcrumb")
            if breadcrumb and isinstance(breadcrumb, Tag):
                all_lines = breadcrumb.find_all("li")
                if len(all_lines) > 2:
                    aux_li = all_lines[2]
                    if aux_li and isinstance(aux_li, Tag):
                        category_link = aux_li.find("a")
                        if category_link and isinstance(category_link, Tag) and hasattr(category_link, 'text'):
                            book.category = category_link.text.strip()
                        else:
                            book.category = ""
                    else:
                      book.category = ""
                if len(all_lines) > 3:
                    book.title = all_lines[3].text.strip()
        except (AttributeError, IndexError) as e:
            print(f"Error extracting category/title: {e}")
            book.category = ""
            book.title = ""

        # Get Book Price
        try:
            price_element = book_info_page.find("p", class_="price_color")
            if price_element and isinstance(price_element, Tag) and price_element.text:
                price_text = price_element.text.strip()
                price_text = price_text.replace("\\xc2\\xa3", "")
                # Extract numeric value from price string
                price_match = re.search(r'[\d.]+', price_text)
                if price_match:
                    book.price = Decimal(price_match.group())
                else:
                    book.price = Decimal('0')
            else:
                book.price = Decimal('0')
        except (AttributeError, ValueError) as e:
            print(f"Error extracting price: {e}")
            book.price = Decimal('0')

        # Get Book Stock
        try:
            stock_element = book_info_page.find("p", class_="instock availability")
            if stock_element and isinstance(stock_element, Tag) and stock_element.text:
                stock_text = stock_element.text.strip()
                if("In stock" in stock_text and "available" in stock_text):
                  #get only the number in string
                  stock_number = re.search(r'[\d.]+', stock_text)
                  if stock_number:
                    book.stock = int(stock_number.group())
                  else:
                    book.stock = 0
                else:
                  book.stock = 0
            else: 
                book.stock = 0
        except (AttributeError, ValueError) as e:
            print(f"Error extracting stock: {e}")
            book.stock = 0

        # Get Book Rating
        try:
            star_rating = book_info_page.find("p", class_="star-rating")
            if star_rating and isinstance(star_rating, Tag):
                rating_classes = star_rating.get("class")
                if rating_classes and len(rating_classes) > 1:
                    rating_class = rating_classes[1]
                    book.rating = self.get_number_from_string(rating_class)
                else:
                    book.rating = 0
            else:
                book.rating = 0
        except (AttributeError, IndexError) as e:
            print(f"Error extracting rating: {e}")
            book.rating = 0

        # Get Book Image
        try:
            img_aux = book_info_page.find("img")
            if img_aux and isinstance(img_aux, Tag):
                src_attr = img_aux.get("src")
                if src_attr and isinstance(src_attr, str):
                    aux_url = src_attr.replace("../", "")
                    book.image = self.main_url + aux_url
                else:
                    book.image = ""
            else:
                book.image = ""
        except (AttributeError, TypeError) as e:
            print(f"Error extracting image: {e}")
            book.image = ""

        return book

  
    def save_books_info_to_csv(self, books_info: list[Book], filename: str):
      """
      Save all books information to a CSV file.
      Args:
        all_books_info: List of Book objects to save to CSV
      """    
      print("--------------------------------")
      print("Scrape - Saving all Books Info to CSV - " + str(len(books_info)))
      print("--------------------------------")
      with open("mockdata/"+filename+".csv", "w") as file:
        writer = csv.writer(file,quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["id", "author", "year", "title", "category", "stock", "price", "rating", "image"])
        for book in books_info:
          writer.writerow([book.id, book.author, book.year, book.title, book.category, book.stock, book.price, book.rating, book.image])

    def get_number_from_string(self, string: str) -> int:
        """
        Convert text representation of numbers to integers.
        Args:
            string: The string to convert to an integer
        Returns:
            The integer representation of the string
        """
        if not string:
            return 0
        
        string_lower = string.lower()
        return self.NUMBER_MAPPING.get(string_lower, 0)			