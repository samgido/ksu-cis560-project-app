import math
import utils
import flask
from flask import redirect, render_template, request

class View:
    def __init__(self, service):
        self.service = service

        self.blueprint = flask.Blueprint("view", __name__)

        self.analytics_queries = utils.get_analytics_query_names()

        if self.analytics_queries is None:
            print("Could not read analytics query names")
            exit(1)

        self.analytics_queries_proper = list(
            map(utils.snake_case_to_proper, self.analytics_queries)
        )

        self.setup_routes()

    def setup_routes(self):
        # books
        self.blueprint.add_url_rule("/", view_func=self.index, methods=["GET"])
        self.blueprint.add_url_rule("/books/<int:page_number>", view_func=self.books, methods=["GET"])
        self.blueprint.add_url_rule("/book_details/<int:book_id>", view_func=self.book_details, methods=["GET"])
        self.blueprint.add_url_rule("/checkout_book/<int:book_id>", view_func=self.checkout_book, methods=["GET", "POST"])
        self.blueprint.add_url_rule("/return_book", view_func=self.return_book, methods=["GET", "POST"])

        # customers
        self.blueprint.add_url_rule("/create_customer", view_func=self.create_customer, methods=["GET", "POST"])
        self.blueprint.add_url_rule("/disable_library_card", view_func=self.disable_library_card, methods=["GET", "POST"])

        # analytics
        self.blueprint.add_url_rule("/analytics", view_func=self.analytics, methods=["GET", "POST"])

    def index(self):
        return redirect("/books/1")

    def books(self, page_number):
        book_count = self.service.get_book_count()

        page_count = math.ceil(book_count / utils.PAGE_SIZE)

        books = self.service.get_books_list_display(page_number)

        return render_template(
            "books.html", page_number=page_number, page_count=page_count, books=books
        )

    def book_details(self, book_id):
        book = self.service.get_book(book_id)

        if book is None:
            return utils.render_success_failure("Book not found")

        return render_template("book_details.html", book=book)

    def checkout_book(self, book_id):
        if request.method == "POST":
            email = request.form.get("email")
            print(f"Checkout request for book {book_id} to customer {email}")

            error = self.service.checkout_book(book_id, email)

            return utils.render_success_failure(
                error or "Book checked out successfully"
            )

        book = self.service.get_book(book_id)

        if book is None:
            message = "Book not found"
            return utils.render_success_failure(message)

        return render_template("checkout_book.html", book=book)

    def return_book(self):
        if request.method == "POST":
            condition = request.form.get("condition_list")
            book_copy_id = request.form.get("book_copy_id")
            checkout_id = request.form.get("checkout_id")

            error = self.service.return_book(checkout_id, book_copy_id, condition)

            return utils.render_success_failure(
                error or "Successfully returned book and updated condition"
            )

        email = request.args.get("email", None)
        book_id = request.args.get("book_id", None)

        if email is not None and book_id is not None:
            conditions = self.service.conditions
            checkout = self.service.get_checkout(email, book_id)

            if checkout is None:
                return utils.render_success_failure("Could not find checkout")

            book = self.service.get_book(checkout.book_id)

            if book is None:
                return utils.render_success_failure("Could not find book")

            return render_template(
                "checkout_details.html",
                conditions=conditions,
                checkout=checkout,
                book=book,
            )

        if email is not None and book_id is None:
            books = self.service.get_user_checked_books(email)

            if books is None:
                return utils.render_success_failure("User has no checked books")

            return render_template("user_checked_books.html", email=email, books=books)

        if book_id is not None and email is None:
            users = self.service.get_book_loaners(book_id)

            if users is None:
                return utils.render_success_failure(
                    "Book isn't checked out by any users"
                )

            return render_template("book_loaners.html", book_id=book_id, users=users)

        if email is None and book_id is None:
            return render_template("get_user.html")

        return utils.render_success_failure("Book returned successfully")

    def create_customer(self):
        if request.method == "POST":
            email = request.form.get("email")
            first_name = request.form.get("fname")
            last_name = request.form.get("lname")
            print(f"Create customer request for customer {email}, ({last_name}, {first_name})")

            error = self.service.create_customer(email, first_name, last_name)

            return utils.render_success_failure(
                error or "Customer created successfully"
            )

        return render_template("create_customer.html")

    def disable_library_card(self):
        if request.method == "POST":
            email = request.form.get("email")

            error = self.service.disable_library_card(email)

            return utils.render_success_failure(
                error or "Library card successfully disabled"
            )

        return render_template("disable_library_card.html")

    def analytics(self):
        if request.method == "POST":
            query_str = request.form.get("query")
            begin_date_str = request.form.get("begin_date")
            end_date_str = request.form.get("end_date")

            if (
                query_str not in self.analytics_queries_proper
                or begin_date_str is None
                or end_date_str is None
            ):
                return utils.render_success_failure("Some form field(s) were not valid")

            query_name = query_str.replace(" ", "") + "Proc"
            query_data = self.service.get_analytics_data(
                query_name, begin_date_str, end_date_str
            )

            template_name = "analytics/" + query_str.lower().replace(" ", "_") + ".html"

            return render_template(template_name, data_rows=query_data)

        return render_template(
            "analytics/analytics_input.html", queries=self.analytics_queries_proper
        )
