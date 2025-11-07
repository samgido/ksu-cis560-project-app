from utils import check_dotenv, create_database_connection, PAGE_SIZE

class Repository:
	def __init__(self):
		check_dotenv()

		self.conn = create_database_connection()

	def get_book_count(self):
		sql="""\
		select count(*) from Books;
		"""
		rows = self.get_rows(sql)

		if (len(rows) == 0):
			print("Warning: get book count returned no rows")
			return 0

		book_count = int(rows[0][0])
		return book_count

	def email_belongs_to_customer(self, email):
		print("Warning: Email belongs to customer not implemented")
		return email == "johndoe@gmail.com" 

	def book_available_for_checkout(self, book_id):
		print("Warning: Book available for checkout not implemented")
		return book_id == 1 

	def get_books_list_display(self, page_number):
		sql=f"""\
		select 
			Books.BookID as book_id, 
			Books.CoverImg as cover_img_url, 
			Books.BookTitle as title, 
			Genres.GenreName as genre
		from SharedData.dbo.Books
			inner join SharedData.dbo.Genres on Genres.GenreID = Books.GenreID
		order by Books.BookID asc
		offset ({PAGE_SIZE} * ({page_number} - 1)) rows fetch next {PAGE_SIZE} rows only;
		"""
		rows = self.get_rows(sql)
		return rows

	def get_book(self, book_id):
		sql=f"""\
		select 
			Books.BookID as book_id,
			Books.ISBN as isbn,
			Books.CoverImg as cover_img_url,
			Books.Author as author,
			Books.BookTitle as title,
			Genres.GenreName as genre
		from SharedData.dbo.Books
			inner join SharedData.dbo.Genres on Genres.GenreID = Books.GenreID
		where Books.BookID = {book_id}
		"""
		rows = self.get_rows(sql)
		return rows

	def get_rows(self, query: str):
		cursor = self.conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()

		cursor.close()
		return rows

	def dispose(self):
		self.conn.close()
