from typing import Optional
from pyodbc import Row
from repository import Repository
from utils import check_dotenv
from dataclasses import dataclass
import utils

@dataclass
class ListDisplayBook:
	book_id: int
	cover_img_url: str
	title: str
	genre: str
	available: bool
	available_count: int

@dataclass
class Book:
	book_id: int
	isbn: int
	cover_img_url: str
	author: str
	title: str
	genre: str
	available: bool
	available_count: int
	total_count: int

class Service:
	def __init__(self, repository: Repository) -> None:
		check_dotenv()

		self.repo = repository

		self.book_count = 0
		self.get_book_count()

	def return_book(self, book_id, email):
		print("Warning: book return not implemented")
		book_exists = self.get_book(book_id) is not None
		if not book_exists:
			return f"Book {book_id} doesn't exist"

		if self.book_available_for_checkout(book_id):
			return f"Book {book_id} not checked out, cannot be returned"


		return None

	def checkout_book(self, book_id, loaner_email):
		print("Warning: book checkout not implemented")
		if not self.book_available_for_checkout(book_id):
			return f"Book {book_id} unavailable for checkout"

		if not self.repo.get_customer(loaner_email):
			return f"Email {loaner_email} doesn't belong to a customer"

		return None

	def create_customer(self, email, first_name, last_name):
		print("Warning: create customer not implemented")
		if self.repo.get_customer(email):
			return f"Email {email} already belongs to a customer"

		return None

	def remove_customer(self, email):
		print("Warning: remove customer not implemented")
		if not self.repo.get_customer(email):
			return f"Email {email} does not belong to a customer"

		return None

	def get_book_count(self):
		return self.repo.get_book_count()

	def get_books_list_display(self, page_number):
		def make_display_book(r: Row):
			book_id = r.book_id
			available_count = self.repo.get_checked_copy_count(book_id)
			available = self.book_available_for_checkout(book_id)

			return ListDisplayBook(
				book_id,
				r.cover_img_url,
				r.title,
				r.genre,
				available,
				available_count
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
		available_count = self.repo.get_checked_copy_count(book_id)
		total_count = self.repo.get_total_copy_count(book_id)
		return Book(
			b.book_id,
			b.isbn,
			b.cover_img_url,
			b.author, 
			b.title,
			b.genre,
			available,
			available_count,
			total_count
		)

	def get_available_count(self, book_id):
		total_count = self.repo.get_total_copy_count(book_id)
		checked_count = self.repo.get_checked_copy_count(book_id)

		return total_count - checked_count

	def book_available_for_checkout(self, book_id):
		return self.get_available_count(book_id) > 0

	def email_belongs_to_customer(self, email):
		rows = self.repo.get_customer(email)
		return len(rows) > 0

	def dispose(self):
		self.repo.dispose()
