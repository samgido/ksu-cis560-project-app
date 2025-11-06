from utils import check_dotenv, create_database_connection

class ConnectionManager:
	def __init__(self) -> None:
		check_dotenv()

		self.connection = create_database_connection()

		self.book_count = 0
		self.get_book_count()

	def get_book_count(self):
		print("Warning: Book count implemented")
		self.book_count = 200

	def get_rows(self, query: str):
		cursor = self.connection.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()

		cursor.close()
		return rows

	def dispose(self):
		self.connection.close()

	def email_belongs_to_customer(self, email):
		print("Warning: Email belongs to customer not implemented")
		return email == "johndoe@gmail.com" 

	def book_available_for_checkout(self, book_id):
		print("Warning: Book available for checkout not implemented")
		return book_id == 1 
