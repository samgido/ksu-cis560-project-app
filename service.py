from repository import Repository
from utils import check_dotenv

class Service:
	def __init__(self, repository: Repository) -> None:
		check_dotenv()

		self.repo = repository

		self.book_count = 0
		self.get_book_count()

	def get_book_count(self):
		return self.repo.get_book_count()

	def email_belongs_to_customer(self, email):
		return self.repo.email_belongs_to_customer(email)

	def book_available_for_checkout(self, book_id):
		return self.repo.book_available_for_checkout(book_id)

	def dispose(self):
		self.repo.dispose()
