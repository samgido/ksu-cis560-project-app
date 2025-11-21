from utils import check_dotenv, create_database_connection, PAGE_SIZE

class Repository:
	def __init__(self):
		check_dotenv()
		self.conn = create_database_connection()

	def get_user(self, email):
		sql=f"""\
		select 
			Customer.CustomerID as customer_id,
			Customer.EmailAddress as email,
			concat(Customer.LastName, ',', Customer.FirstName) as name,
			LibraryCard.Inactive as card_inactive
		from Customer
			inner join LibraryCard on LibraryCard.CustomerID = Customer.CustomerID
		where Customer.EmailAddress = N'{email}'
		"""
		rows = self.get_rows(sql)
		return rows

	def create_customer(self, email, first_name, last_name):
		sql=f"""\
		begin try
		insert into Customer(EmailAddress, FirstName, LastName) 
		values (N'{email}', N'{first_name}', N'{last_name}');
		end try 
		begin catch end catch

		declare @Customer int = (
			select Customer.CustomerID
			from Customer 
			where Customer.EmailAddress = N'{email}'
		);

		merge LibraryCard
		using (select @Customer) as C(CustomerID)
			on LibraryCard.CustomerID = C.CustomerID
		when matched
			then update 
			set Inactive = 0
		when not matched 
			then insert (CustomerID, Inactive) 
			values (C.CustomerID, 0);
		"""
		rows_affected = self.get_rows_affected(sql)
		return rows_affected

	def disable_library_card(self, email):
		sql=f"""\
		declare @CardID int = (
			select LibraryCard.LibraryCardID
			from LibraryCard
				inner join Customer on Customer.CustomerID = LibraryCard.CustomerID
			where Customer.EmailAddress = N'{email}'
		);

		update LibraryCard
		set Inactive = ~Inactive
		where LibraryCard.LibraryCardID = @CardID
		"""
		rows_affected = self.get_rows_affected(sql)
		return rows_affected

	def create_checkout(self, email, book_id):
		sql=f"""\
		declare @BestCopy int = (
			select top 1 BookCopy.BookCopyID
			from BookCopy 
				inner join BookCopyCondition on BookCopyCondition.ConditionID = BookCopy.ConditionID
			where BookCopy.BookID = {book_id}
			order by BookCopyCondition.ConditionID asc
		);

		declare @CardID int = (
			select LibraryCard.LibraryCardID
			from LibraryCard
				inner join Customer on Customer.CustomerID = LibraryCard.CustomerID
			where Customer.EmailAddress = N'{email}'
		);

		declare @Today date = getdate();
		declare @DueDate date = dateadd(day, 14, @Today);

		insert into Checkout(BookCopyID, LenderLibraryCardID, CheckoutDate, DueDate, DateReturned)
		values (@BestCopy, @CardID, @Today, @DueDate, null);
		"""
		rows_affected = self.get_rows_affected(sql)
		return rows_affected

	def update_condition(self, book_copy_id, condition):
		sql=f"""\
		declare @ConditionID int;
		set @ConditionID = (
			select top 1 BookCopyCondition.ConditionID
			from BookCopyCondition
			where BookCopyCondition.Condition = N'{condition}'
		);

		update BookCopy
		set 
			ConditionID = @ConditionID
		where BookCopy.BookCopyID = {book_copy_id};
		"""
		rows_affected = self.get_rows_affected(sql)
		return rows_affected

	def get_checkouts(self, email, book_id):
		sql=f"""\
		with CheckoutCte(CheckoutID, LenderEmailAddress, BookID, CheckoutDate, DueDate, ConditionID, BookCopyID) as (
			select 
				Checkout.CheckoutID, 
				Customer.EmailAddress as LenderEmailAddress, 
				BookCopy.BookID,
				Checkout.CheckoutDate,
				Checkout.DueDate,
				BookCopy.ConditionID,
				Checkout.BookCopyID
			from Checkout
				inner join BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
				inner join LibraryCard on LibraryCard.LibraryCardID = Checkout.LenderLibraryCardId
				inner join Customer on Customer.CustomerID = LibraryCard.CustomerID
			where Checkout.DateReturned is null
		)
		select
			CheckoutCte.CheckoutDate as checkout_date,
			CheckoutCte.DueDate as due_date,
			CheckoutCte.BookID as book_id,
			BookCopyCondition.Condition as condition,
			cast(iif(getdate() > CheckoutCte.DueDate, 1, 0) as bit) as overdue,
			CheckoutCte.CheckoutID as checkout_id,
			CheckoutCte.BookCopyID as book_copy_id
		from CheckoutCte
			inner join BookCopyCondition on BookCopyCondition.ConditionID = CheckoutCte.ConditionID
		where CheckoutCte.LenderEmailAddress = N'{email}' and CheckoutCte.BookID = {book_id}
		order by CheckoutCte.CheckoutDate asc, CheckoutCte.BookID;
		"""
		rows = self.get_rows(sql)
		return rows

	def get_condition_names(self):
		sql=f"""\
		select BookCopyCondition.Condition as condition
		from BookCopyCondition;
		"""
		rows = self.get_rows(sql)
		return rows

	def get_book_count(self):
		sql=f"""\
		select count(*) as count
		from Book;
		"""
		rows = self.get_rows(sql)

		if len(rows) == 0:
			print("Warning: get book count returned no rows")
			return 0

		return int(rows[0].count)

	def get_num_accounts(self, email):
		sql=f"""\
		select count(distinct Customer.CustomerID) as count 
		from Customer 
		where Customer.EmailAddress = N'{email}';
		"""
		rows = self.get_rows(sql)

		if len(rows) == 0:
			print("Warning: get_num_accounts returned no rows")
			return 0

		return int(rows[0].count)

	def get_users_checked_books(self, email):
		sql=f"""\
		with CurrentCheckedBook(BookID, LenderEmailAddress) as (
			select BookCopy.BookID, Customer.EmailAddress
			from Checkout
				inner join BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
				inner join LibraryCard on LibraryCard.LibraryCardID = Checkout.LenderLibraryCardId
				inner join Customer on Customer.CustomerID = LibraryCard.CustomerID
			where Checkout.DateReturned is null
		),
		BookInfo(BookID, ISBN, CoverImg, Title, Author, Genre) as (
			select
				Book.BookID, Book.ISBN, Book.CoverImg, Book.Title,
				concat(Author.LastName, ',', Author.FirstName) as Author,
				Genre.Name
			from Book
				inner join Author on Author.AuthorID = Book.AuthorID
				inner join Genre on Genre.GenreID = Book.GenreID
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
		order by BookInfo.ISBN;
		"""
		rows = self.get_rows(sql)
		return rows

	def return_book(self, checkout_id):
		sql=f"""\
		update Checkout
		set 
			DateReturned = getdate()
		where Checkout.CheckoutID = {checkout_id};
		"""
		rows_affected = self.get_rows_affected(sql)
		return rows_affected

	def get_book_loaners(self, book_id):
		sql=f"""\
		with UserWithCheckedBook(CustomerID, BookID, Inactive) as (
			select LibraryCard.CustomerID, BookCopy.BookID, LibraryCard.Inactive
			from Checkout
				inner join LibraryCard on LibraryCard.LibraryCardID = Checkout.LenderLibraryCardId
				inner join BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
			where Checkout.DateReturned is null
		)
		select 
			Customer.CustomerID as customer_id,
			Customer.EmailAddress as email,
			concat(Customer.LastName, ',', Customer.FirstName) as name,
			UserWithCheckedBook.Inactive as card_inactive
		from UserWithCheckedBook
			inner join Customer on Customer.CustomerID = UserWithCheckedBook.CustomerID
		where UserWithCheckedBook.BookID = {book_id}
		order by Customer.LastName, Customer.FirstName, Customer.CustomerID;
		"""
		rows = self.get_rows(sql)
		return rows

	def get_checked_copy_count(self, book_id):
		sql=f"""\
		select count(distinct BookCopy.BookCopyID) as count
		from Checkout
			inner join BookCopy on BookCopy.BookCopyID = Checkout.BookCopyID
		where Checkout.DateReturned is null and BookCopy.BookID = {book_id};
		"""
		rows = self.get_rows(sql)

		if(len(rows) == 0):
			print("Issue with get checked copy count")
			return 0

		return int(rows[0].count)

	def get_total_copy_count(self, book_id):
		sql=f"""\
		select count(distinct BookCopy.BookCopyID) as count
		from BookCopy
		where BookCopy.BookID = {book_id};
		"""
		rows = self.get_rows(sql)

		if (len(rows) == 0):
			print("Issue with get total copy count")
			return 0

		return int(rows[0].count)

	def get_book_list_display(self, page_number):
		sql=f"""\
		select 
			Book.BookID as book_id, 
			Book.CoverImg as cover_img_url, 
			Book.Title as title, 
			Genre.Name as genre
		from Book
			inner join Genre on Genre.GenreID = Book.GenreID
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
		from Book
			inner join Genre on Genre.GenreID = Book.GenreID
			inner join Author on Author.AuthorID = Book.AuthorID
		where Book.BookID = {book_id};
		"""
		rows = self.get_rows(sql)
		return rows

	def get_rows(self, query: str):
		cursor = self.conn.cursor()
		cursor.execute(query)

		rows = cursor.fetchall()
		cursor.close()

		return rows

	def get_rows_affected(self, query: str):
		cursor = self.conn.cursor()
		cursor.execute(query)
		self.conn.commit()

		rows_affected = cursor.rowcount;
		cursor.close()

		return rows_affected

	def dispose(self):
		self.conn.close()
