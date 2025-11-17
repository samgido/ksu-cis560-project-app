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

@app.route("/return_book/", methods=['POST', 'GET'])
def return_book():
    if request.method == "POST":
        condition = request.form.get('condition_list')
        book_copy_id = request.form.get('book_copy_id')
        checkout_id = request.form.get('checkout_id')

        error = service.return_book(checkout_id, book_copy_id, condition)

        return utils.render_success_failure(error or "Successfully returned book and updated condition")

    error = None

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

    return utils.render_success_failure(error or "Book returned successfully")

@app.route("/books/<int:page_number>")
def books(page_number):
    book_count = service.get_book_count()

    page_count = math.ceil(book_count / utils.PAGE_SIZE)

    books = service.repo.get_book_list_display(page_number)

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

    return render_template('book_details.html', book=book)

app.run(debug=True)

service.dispose()
