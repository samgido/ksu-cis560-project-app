from utils import check_dotenv, create_database_connection, PAGE_SIZE

DB = "SharedData.dbo"

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
		sql=f"""\
		with CurrentCheckedBook(BookID, LenderEmailAddress) as (
			select BookCopy.BookID, Customer.EmailAddress
			from {DB}.Checkout
				inner join {DB}.BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
				inner join {DB}.LibraryCard on LibraryCard.LibraryCardID = Checkout.LenderLibraryCardId
				inner join {DB}.Customer on Customer.CustomerID = LibraryCard.CustomerID
			where Checkout.DateReturned is null
		),
		BookInfo(BookID, ISBN, CoverImg, Title, Author, Genre) as (
			select
				Book.BookID, Book.ISBN, Book.CoverImg, Book.Title,
				concat(Author.LastName, ',', Author.FirstName) as Author,
				Genre.Name
			from {DB}.Book
				inner join {DB}.Author on Author.AuthorID = Book.AuthorID
				inner join {DB}.Genre on Genre.GenreID = Book.GenreID
		)
		select 
			BookInfo.BookID as book_id,
			BookInfo.ISBN as isbn,
			BookInfo.CoverImg as cover_img_url,
			BookInfo.Title as title,
			BookInfo.Author as author,
			BookInfo.Genre as genre
		from CurrentCheckedBook
			inner join BookInfo on BookInfo.BookID = CurrentCheckedBook.BookID
		where CurrentCheckedBook.LenderEmailAddress = N'{email}'
		order by BookInfo.ISBN
		"""
		rows = self.get_rows(sql)
		return rows

	def return_book(self, checkout_id):
		sql=f"""\
		update {DB}.Checkout
		set DateReturned = GETDATE()
		where Checkout.CheckoutID = {checkout_id}
		"""
		_, rows_affected = self.get_rows_and_rows_affected(sql)
		return rows_affected

	def get_checkouts(self, email, book_id):
		sql=f"""\
		with CheckoutCte(CheckoutID, LenderEmailAddress, BookID, CheckoutDate) as (
			select 
				Checkout.CheckoutID, 
				Customer.EmailAddress as LenderEmailAddress, 
				BookCopy.BookID,
				Checkout.CheckoutDate
			from {DB}.Checkout
				inner join {DB}.BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
				inner join {DB}.LibraryCard on LibraryCard.LibraryCardID = Checkout.LenderLibraryCardId
				inner join {DB}.Customer on Customer.CustomerID = LibraryCard.CustomerID
		)
		select CheckoutCte.CheckoutID
		from CheckoutCte
		where CheckoutCte.LenderEmailAddress = {email} and CheckoutCte.BookID = {book_id}
		order by CheckoutCte.CheckoutDate asc
		"""
		rows = self.get_rows(sql)
		return rows

	def get_book_loaners(self, book_id):
		sql=f"""\
		with UserWithCheckedBook(CustomerID, BookID) as (
			select LibraryCard.CustomerID, BookCopy.BookID
			from {DB}.Checkout
				inner join {DB}.LibraryCard on LibraryCard.LibraryCardID = Checkout.LenderLibraryCardId
				inner join {DB}.BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
			where Checkout.DateReturned is null
		)
		select 
			Customer.CustomerID as customer_id,
			Customer.EmailAddress as email,
			concat(Customer.LastName, ',', Customer.FirstName) as name
		from UserWithCheckedBook
			inner join {DB}.Customer on Customer.CustomerID = UserWithCheckedBook.CustomerID
		where UserWithCheckedBook.BookID = {book_id};
		order by Customer.LastName, Customer.FirstName, Customer.CustomerID
		"""
		rows = self.get_rows(sql)
		return rows

	def get_checked_copy_count(self, book_id):
		sql=f"""\
		select count(distinct BookCopy.BookCopyID) as count
		from {DB}.Checkout
			inner join {DB}.BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
		where Checkout.DateReturned is null and BookCopy.BookID = {book_id}
		"""
		rows = self.get_rows(sql)

		if(len(rows) == 0):
			return 0

		return int(rows[0].count)

	def get_total_copy_count(self, book_id):
		sql=f"""\
		select count(distinct BookCopy.BookCopyID) as count
		from {DB}.BookCopy
		where BookCopy.BookID = {book_id}
		"""
		rows = self.get_rows(sql)

		if (len(rows) == 0):
			return 0

		return int(rows[0].count)

	def get_book_list_display(self, page_number):
		sql=f"""\
		select 
			Book.BookID as book_id, 
			Book.CoverImg as cover_img_url, 
			Book.Title as title, 
			Genre.Name as genre
		from {DB}.Book
			inner join {DB}.Genre on Genre.GenreID = Book.GenreID
		order by Book.Title asc
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
		from {DB}.Book
			inner join {DB}.Genre on Genre.GenreID = Book.GenreID
			inner join {DB}.Author on Author.AuthorID = Book.AuthorID
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

	def get_rows_and_rows_affected(self, query: str):
		cursor = self.conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()
		rows_affected = cursor.rowcount;
		cursor.close()

		return rows, rows_affected

	def dispose(self):
		self.conn.close()
