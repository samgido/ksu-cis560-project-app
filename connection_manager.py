from utils import check_dotenv, create_database_connection

class ConnectionManager:
	def __init__(self) -> None:
		check_dotenv()

		self.connection = create_database_connection()
		self.cursor = self.connection.cursor()

	def get_rows(self, query: str):
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def dispose(self):
		self.connection.close()

	def email_belongs_to_customer(self, email):
		return email == "johndoe@gmail.com" # placeholder

	def book_available_for_checkout(self, book_id):
		return book_id == 1 # placeholder
