import flask 
from flask import redirect, request, render_template
from repository import Repository
import utils 
from service import Service
import math

repository = Repository()
global service
service = Service(repository)

app = flask.Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/remove_customer", methods=['POST', 'GET'])
def remove_customer():
    if request.method == "POST":
        email = request.form.get('email')
        print(f"Remove customer request for customer {email}")

        message = f"Success: customer {email} removed"

        if not service.email_belongs_to_customer(email):
            message = f"Failure: email {email} does not belong to a customer"

        return utils.render_success_failure(message)

    return render_template('remove_customer.html')

@app.route("/create_customer", methods=['POST', 'GET'])
def create_customer():
    if request.method == "POST":
        email = request.form.get('email')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        print(f"Create customer request for customer {email}, ({lname}, {fname})")

        error = service.create_customer(email, fname, lname)

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

@app.route("/return_book/")
def return_book():
    error = None

    email = request.args.get('email', None)
    book_id = request.args.get('book_id', None)

    if email is not None and book_id is not None:
        if not service.email_belongs_to_customer(email):
            return utils.render_success_failure(f"Email {email} does not belong to customer")

        return utils.render_success_failure("Invalid args given")

    if email is not None and book_id is None:
        return utils.render_success_failure(f"Received email arg, showing all books checked out by {email}")

    if book_id is not None and email is None:
        return utils.render_success_failure(f"Received book_id arg, showing all users who've checked out book {book_id}")

    if email is None and book_id is None:
        return utils.render_success_failure("Neither arg given, showing form for user email input")

    return utils.render_success_failure(error or "Book returned successfully")

@app.route("/books/<int:page_number>")
def books(page_number):
    book_count = service.get_book_count()

    page_count = math.ceil(book_count / utils.PAGE_SIZE)

    books = service.repo.get_books_list_display(page_number)

    return render_template('books.html', 
        page_number=page_number, 
        page_count=page_count, 
        books=books
    )

@app.route("/book_details/<int:book_id>")
def book_details(book_id):
    book = service.get_book(book_id)

    if book == None:
        message = "Book not found"
        return utils.render_success_failure(message)

    return render_template('view_book.html', book=book)

app.run(debug=True)

service.dispose()
