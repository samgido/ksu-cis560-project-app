from utils import check_dotenv, create_database_connection

class Repository:
	def __init__(self):
		check_dotenv()

		self.conn = create_database_connection()

	def get_book_count(self):
		print("Warning: Book count implemented")
		self.book_count = 200

	def email_belongs_to_customer(self, email):
		print("Warning: Email belongs to customer not implemented")
		return email == "johndoe@gmail.com" 

	def book_available_for_checkout(self, book_id):
		print("Warning: Book available for checkout not implemented")
		return book_id == 1 

	def get_rows(self, query: str):
		cursor = self.conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()

		cursor.close()
		return rows

	def dispose(self):
		self.conn.close()
