from typing import Optional
from pyodbc import Row
from repository import Repository
from utils import check_dotenv
from dataclasses import dataclass

@dataclass
class ListDisplayBook:
	book_id: int
	cover_img_url: str
	title: str
	genre: str
	available: bool

@dataclass
class Book:
	book_id: int
	isbn: int
	cover_img_url: str
	author: str
	title: str
	genre: str
	available: bool

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

	def get_books_list_display(self, page_number):
		def make_display_book(r: Row):
			book_id = r.book_id
			available = self.repo.book_available_for_checkout(book_id)

			return ListDisplayBook(
				book_id,
				r.cover_img_url,
				r.title,
				r.genre,
				self.book_available_for_checkout(book_id)
			)

		rows = self.repo.get_books_list_display(page_number)
		books = map(make_display_book, rows)

		return books

	def get_book(self, book_id) -> Optional[Book]:
		rows = self.repo.get_book(book_id)

		if (len(rows) == 0):
			return None

		b = rows[0]
		available = self.book_available_for_checkout(book_id)
		return Book(
			b.book_id,
			b.isbn,
			b.cover_img_url,
			b.author, 
			b.title,
			b.genre,
			available
		)

	def dispose(self):
		self.repo.dispose()
