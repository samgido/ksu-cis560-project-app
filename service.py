from datetime import date
from typing import Optional, List
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

@dataclass
class User:
	customer_id: int
	email: str
	name: str
	card_inactive: bool

@dataclass
class Checkout:
	checkout_date: date
	due_date: date
	book_id: int
	condition: str
	overdue: bool
	checkout_id: int
	book_copy_id: int

class Service:
	def __init__(self, repository: Repository, logger) -> None:
		self.logger = logger 

		check_dotenv()
		self.repo = repository
		
		self.get_book_count()

		self.conditions = []
		self.initialize_conditions()

	def get_special_query_data(self, query_name, begin_date, end_date):
		rows = self.repo.run_aggregating_query(query_name, begin_date, end_date)
		return rows

	def initialize_conditions(self):
		rows = self.repo.get_condition_names()

		try:
			self.conditions = list(map(lambda r: r.condition, rows))
		except:
			print("Could not initialize condition names")
			exit(1)

	def get_checkout(self, email, book_id) -> Optional[Checkout]:
		rows = self.repo.get_checkouts(email, book_id)

		if len(rows) == 0:
			return None

		return self.make_checkout(rows[0])

	def return_book(self, checkout_id, book_copy_id, condition) -> Optional[str]:
		if self.repo.return_book(checkout_id) == 0:
			return "Failed to return book"

		if self.repo.update_condition(book_copy_id, condition) == 0:
			return "Failed to update book condition"

		return None

	def checkout_book(self, book_id, loaner_email) -> Optional[str]:
		if not self.book_available_for_checkout(book_id):
			return f"Book {book_id} unavailable for checkout"

		if not self.repo.get_num_accounts(loaner_email):
			return f"Email {loaner_email} doesn't belong to a customer"

		if self.repo.create_checkout(loaner_email, book_id) == 0:
			return f"Failed to create checkout"

		return None

	def create_customer(self, email, first_name, last_name) -> Optional[str]:
		error = ""

		rows = self.repo.get_user(email)
		if len(rows) > 0:
			error += f"Email {email} already belongs to a customer, their card has been activated.\n"

		self.repo.create_customer(email, first_name, last_name)

		return error

	def disable_library_card(self, email) -> Optional[str]:
		rows = self.repo.get_user(email)

		if len(rows) == 0:
			return f"Error: Email doesn't belong to a customer"

		user = self.make_user(rows[0])

		if user is None:
			return f"Error occurred reading user"

		if user.card_inactive:
			return f"Card is already inactive"

		if len(self.repo.get_users_checked_books(email)) > 0:
			return f"Error: User has checked out books"

		rows_affected = self.repo.disable_library_card(email)

		if rows_affected == 0:
			return "Error occurred disabling card"

		return None

	def get_book_count(self) -> int:
		return self.repo.get_book_count()

	def get_books_list_display(self, page_number) -> Optional[List[ListDisplayBook]]:
		rows = self.repo.get_book_list_display(page_number)
		books = list(map(self.make_display_book, rows))

		return utils.all_or_none(books)

	def get_book(self, book_id) -> Optional[Book]:
		rows = self.repo.get_book(book_id)

		if len(rows) == 0:
			return None

		return self.make_book(rows[0])

	def get_user_checked_books(self, email) -> Optional[List[ListDisplayBook]]:
		rows = self.repo.get_users_checked_books(email)

		if len(rows) == 0:
			return None

		books = list(map(self.make_display_book, rows))

		return utils.all_or_none(books)

	def get_book_loaners(self, book_id) -> Optional[List[User]]:
		rows = self.repo.get_book_loaners(book_id)

		if len(rows) == 0:
			return None

		users = list(map(self.make_user, rows))

		return utils.all_or_none(users)

	def get_available_count(self, book_id) -> int:
		total_count = self.repo.get_total_copy_count(book_id)
		checked_count = self.repo.get_checked_copy_count(book_id)

		return total_count - checked_count

	def book_available_for_checkout(self, book_id) -> bool:
		return self.get_available_count(book_id) > 0

	def email_belongs_to_customer(self, email) -> bool:
		rows = self.repo.get_num_accounts(email)
		return rows > 0

	def make_user(self, r: Row) -> Optional[User]:
		try:
			return User(
				r.customer_id,
				r.email,
				r.name,
				r.card_inactive
			)
		except:
			print("make_display_user was not given a row it needed")
			return None

	def make_book(self, r: Row) -> Optional[Book]:
		try: 
			book_id = r.book_id
			available = self.book_available_for_checkout(book_id)
			available_count = self.get_available_count(book_id)
			total_count = self.repo.get_total_copy_count(book_id)

			return Book(
				r.book_id,
				r.isbn,
				r.cover_img_url,
				r.author, 
				r.title,
				r.genre,
				available,
				available_count,
				total_count
			)
		except:
			print("make_book was not given a row it needed")
			return None

	def make_display_book(self, r: Row) -> Optional[ListDisplayBook]:
		try:
			book_id = r.book_id
			available = self.book_available_for_checkout(book_id)
			available_count = self.get_available_count(book_id)

			return ListDisplayBook(
				book_id,
				r.cover_img_url,
				r.title,
				r.genre,
				available,
				available_count
			)
		except:
			print("make_display_book was not given a row it needed")
			return None

	def make_checkout(self, r: Row) -> Optional[Checkout]:
		try:
			return Checkout(
				r.checkout_date,
				r.due_date,
				r.book_id,
				r.condition,
				r.overdue,
				r.checkout_id,
				r.book_copy_id
			)
		except:
			print("make_checkout was not given a row it needed")
			return None

	def dispose(self):
		self.repo.dispose()
