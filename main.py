import flask 
from flask import request, render_template
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
    return flask.render_template('index.html')

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

        message = f"Success: customer {email} created"

        if service.email_belongs_to_customer(email):
            message = f"Failure: email {email} belongs to another customer"

        return utils.render_success_failure(message)

    return render_template('create_customer.html')

@app.route("/checkout_book", methods=['POST', 'GET'])
def checkout_book():
    if request.method == "POST":
        email = request.form.get('email')
        book_id = int(request.form.get('book_id') or "0")
        print(f"Checkout request for book {book_id} to customer {email}")

        message = f"Success: book {book_id} checked out"

        if not service.book_available_for_checkout(book_id):
            message = f"Failure: book {book_id} unavailable for checkout"
        elif not service.email_belongs_to_customer(email):
            message = f"Failure: email {email} doesn't belong to a customer"

        return utils.render_success_failure(message)

    return render_template('checkout_book.html')

@app.route("/return_book", methods=['POST', 'GET'])
def return_book():
    if request.method == "POST":
        book_id = int(request.form.get('book_id') or "0")
        print(f"Return book request for book {book_id}")

        message = f"Success: book {book_id} returned"

        if service.book_available_for_checkout(book_id):
            message = f"Failure: book {book_id} not checked out"

        return utils.render_success_failure(message)

    return render_template('return_book.html')

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

@app.route("/book/<int:book_id>")
def book(book_id):
    book = service.get_book(book_id)

    if book == None:
        message = "Book not found"
        return utils.render_success_failure(message)

    return render_template('view_book.html', book=book)

app.run(debug=True)

service.dispose()
