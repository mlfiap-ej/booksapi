from Scrap.Scrap import Scrap
from bs4 import BeautifulSoup, Tag

class ScrapMainPage(Scrap):
	"""Scrap the main page of the website."""
	main_url = ""
	
	def __init__(self, main_url: str):
		"""Initialize the ScrapMainPage class."""
		self.main_url = main_url
		

	def get_all_books_url(self):
		"""Get all books URL from the main page."""
		page = 1
		all_books_url = []
		while True:
			books_url = self.get_all_books(page)
			if len(books_url) == 0:
				break
			all_books_url.extend(books_url)
			print("Scrape - Read URL Page " + str(page))
			page += 1
		
		return all_books_url
			

	def get_all_books(self, page: int) -> list[str]:
		"""
    Get all books URL from the main page.
    Args:
        page: The page number to scrape
    Returns:
        A list of all books URL from the main page
    """
		url = self.main_url + "catalogue/page-" + str(page) + ".html"
		content = self.get_page_content(url)		

		#Start the Scrape
		soup = BeautifulSoup(content, "html.parser")				
		all_books_rows = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
		all_books_url = []
		for book_info_page in all_books_rows:
			if book_info_page and isinstance(book_info_page, Tag):
				div_image_container = book_info_page.find("div", class_="image_container")
				if div_image_container and isinstance(div_image_container, Tag):
					book_a = div_image_container.find("a")
					if book_a and isinstance(book_a, Tag) and "href" in book_a.attrs:
						book_url = str(book_a["href"])
						all_books_url.append(self.main_url + "catalogue/" + book_url)
					else:
						all_books_url.append("")
		return all_books_url


