import requests

class Scrap:

	def get_page_content(self, url: str) -> str:
		response = requests.get(url)

		# Check if the page is accessible
		if response.status_code != 200:
			print("Error to access the page - Error code:", response.status_code)
			return ""

		return str(response.content)
