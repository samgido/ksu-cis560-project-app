import flask 
from flask import request, render_template
from repository import Repository
import utils 
from service import Service
import math

app = flask.Flask(__name__)

repository = Repository()
global service
service = Service(repository, app.logger)

analytics_queries = utils.get_analytics_query_names()

if analytics_queries is None:
    print("Couldn't read analytics query names")
    exit(1) 

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/disable_library_card", methods=['POST', 'GET'])
def disable_library_card():
    if request.method == "POST":
        email = request.form.get('email')

        error = service.disable_library_card(email)
        
        return utils.render_success_failure(error or "Library card successfully disabled")

    return render_template('disable_library_card.html')

@app.route("/create_customer", methods=['POST', 'GET'])
def create_customer():
    if request.method == "POST":
        email = request.form.get('email')
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        print(f"Create customer request for customer {email}, ({last_name}, {first_name})")

        error = service.create_customer(email, first_name, last_name)

        return utils.render_success_failure(error or "Customer created successfully")

    return render_template('create_customer.html')

@app.route("/checkout_book/<int:book_id>", methods=['POST', 'GET'])
def checkout_book(book_id):
    if request.method == "POST":
        email = request.form.get('email')
        print(f"Checkout request for book {book_id} to customer {email}")

        error = service.checkout_book(book_id, email)

        return utils.render_success_failure(error or "Book checked out successfully")

    book = service.get_book(book_id)

    if book == None:
        message = "Book not found"
        return utils.render_success_failure(message)

    return render_template('checkout_book.html', book=book)

@app.route("/return_book/", methods=['POST', 'GET'])
def return_book():
    if request.method == "POST":
        condition = request.form.get('condition_list')
        book_copy_id = request.form.get('book_copy_id')
        checkout_id = request.form.get('checkout_id')

        error = service.return_book(checkout_id, book_copy_id, condition)

        return utils.render_success_failure(error or "Successfully returned book and updated condition")

    email = request.args.get('email', None)
    book_id = request.args.get('book_id', None)

    if email is not None and book_id is not None:
        conditions = service.conditions
        checkout = service.get_checkout(email, book_id)

        if checkout is None:
            return utils.render_success_failure("Could not find checkout")

        book = service.get_book(checkout.book_id)

        if book is None:
            return utils.render_success_failure("Could not find book")

        return render_template('checkout_details.html', 
            conditions=conditions,
            checkout=checkout,
            book=book
        )

    if email is not None and book_id is None:
        books = service.get_user_checked_books(email)

        if books is None:
            return utils.render_success_failure("User has no checked books")

        return render_template('user_checked_books.html', email=email, books=books)

    if book_id is not None and email is None:
        users = service.get_book_loaners(book_id)

        if users is None:
            return utils.render_success_failure("Book isn't checked out by any users")

        return render_template('book_loaners.html', book_id=book_id, users=users)

    if email is None and book_id is None:
        return render_template('get_user.html')

    return utils.render_success_failure("Book returned successfully")

@app.route("/books/<int:page_number>")
def books(page_number):
    book_count = service.get_book_count()

    page_count = math.ceil(book_count / utils.PAGE_SIZE)

    books = service.get_books_list_display(page_number)

    return render_template('books.html', 
        page_number=page_number, 
        page_count=page_count, 
        books=books
    )

@app.route("/book_details/<int:book_id>")
def book_details(book_id):
    book = service.get_book(book_id)

    if book is None:
        return utils.render_success_failure("Book not found")

    return render_template('book_details.html', book=book)

@app.route("/analytics", methods=['POST', 'GET'])
def analytics():
    if analytics_queries is None:
        return utils.render_success_failure("Server failure; could not read analytics query names")

    analytics_queries_proper = list(map(utils.snake_case_to_proper, analytics_queries))

    if request.method == 'POST':
        query_str = request.form.get('query')
        begin_date_str = request.form.get('begin_date')
        end_date_str = request.form.get('end_date')

        if analytics_queries is None:
            return utils.render_success_failure("Server failure; could not read analytics query names")

        analytics_queries_proper = list(map(utils.snake_case_to_proper, analytics_queries))

        if not query_str in analytics_queries_proper or begin_date_str is None or end_date_str is None:
            return utils.render_success_failure(f"Some form field(s) were not valid")

        query_name = query_str.replace(' ', '') + 'Proc'
        query_data = service.get_analytics_data(query_name, begin_date_str, end_date_str)

        template_name = "analytics/" + query_str.lower().replace(' ', '_') + '.html'

        return render_template(template_name, data_rows=query_data)

    return render_template('analytics/analytics_input.html', queries=analytics_queries_proper)

app.run(debug=True)

service.dispose()
