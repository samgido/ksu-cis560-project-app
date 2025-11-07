import flask 
from flask import request, render_template
import utils 
from connection_manager import ConnectionManager
import math

PAGE_SIZE = 50

global manager
manager = ConnectionManager()

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

        if not manager.email_belongs_to_customer(email):
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

        if manager.email_belongs_to_customer(email):
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

        if not manager.book_available_for_checkout(book_id):
            message = f"Failure: book {book_id} unavailable for checkout"
        elif not manager.email_belongs_to_customer(email):
            message = f"Failure: email {email} doesn't belong to a customer"

        return utils.render_success_failure(message)

    return render_template('checkout_book.html')

@app.route("/return_book", methods=['POST', 'GET'])
def return_book():
    if request.method == "POST":
        book_id = int(request.form.get('book_id') or "0")
        print(f"Return book request for book {book_id}")

        message = f"Success: book {book_id} returned"

        if manager.book_available_for_checkout(book_id):
            message = f"Failure: book {book_id} not checked out"

        return utils.render_success_failure(message)

    return render_template('return_book.html')

@app.route("/books/<int:page_number>")
def books(page_number):
    book_count = manager.book_count

    page_count = math.ceil(book_count / PAGE_SIZE)

    return render_template('books.html', page_number=page_number, page_count=page_count)

app.run(debug=True)

manager.dispose()
