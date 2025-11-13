from utils import check_dotenv, create_database_connection, PAGE_SIZE

class Repository:
	def __init__(self):
		check_dotenv()

		self.conn = create_database_connection()

	def get_book_count(self):
		sql="""\
		select count(*) from Book;
		"""
		rows = self.get_rows(sql)

		if (len(rows) == 0):
			print("Warning: get book count returned no rows")
			return 0

		book_count = int(rows[0][0])
		return book_count

	def get_customer(self, email):
		sql=f"""\
		select count(*) 
		from Customer 
		where Customer.EmailAddress = N'{email}'
		"""
		rows = self.get_rows(sql)
		return rows

	def get_users_checked_books(self, email):
		print("Warning: Get users checked books not implemented")
		return []

	def get_book_loaners(self, book_id):
		print("Warning: Get loaners not implemented")
		return []

	def get_checked_copy_count(self, book_id):
		print("Warning: Get available count not implemented")
		return 3 if book_id != 1 else 0

	def get_total_copy_count(self, book_id):
		sql=f"""\
		select count(*) 
		from SharedData.dbo.BookCopy
		where BookCopy.BookID = {book_id}
		"""
		rows = self.get_rows(sql)

		if (len(rows) == 0):
			return 0

		return int(rows[0][0])

	def get_books_list_display(self, page_number):
		sql=f"""\
		select 
			Book.BookID as book_id, 
			Book.CoverImg as cover_img_url, 
			Book.Title as title, 
			Genre.Name as genre
		from SharedData.dbo.Book
			inner join SharedData.dbo.Genre on Genre.GenreID = Book.GenreID
		order by Book.BookID asc
		offset ({PAGE_SIZE} * ({page_number} - 1)) rows fetch next {PAGE_SIZE} rows only;
		"""
		rows = self.get_rows(sql)
		return rows

	def get_book(self, book_id):
		sql=f"""\
		select 
			Book.BookID as book_id,
			Book.ISBN as isbn,
			Book.CoverImg as cover_img_url,
			concat(Author.LastName, ',', Author.FirstName) as author,
			Book.Title as title,
			Genre.Name as genre
		from SharedData.dbo.Book
			inner join SharedData.dbo.Genre on Genre.GenreID = Book.GenreID
			inner join SharedData.dbo.Author on Author.AuthorID = Book.AuthorID
		where Book.BookID = {book_id}
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
