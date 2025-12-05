#!/usr/bin/env python3
"""
ERD-aligned data generator with strict fields and realistic dates.

- Source CSV is READ-ONLY (BooksFull.csv / AllBooks.csv / books.csv / Books.csv).
- Require non-empty isbn13 (13 digits), title, authors, thumbnail.
- CoverImg <- thumbnail. BookTitle <- title + optional ': subtitle'.
- DueDate always = CheckoutDate + 14 days (not nullable).
- DateReturned present only for returned items.
- LibraryCards.CustomerID may be NULL for deleted accounts.

Checkout distribution:
- 50% returned
- 40% still out but not overdue (checked out within last 14 days)
- 7% overdue (1-14 days past due)
- 3% very overdue (30-90 days past due)
"""
import csv
import os
import random
from datetime import datetime, timedelta

BOOKS_TARGET_COUNT = 200

NUM_CUSTOMERS = 180
NUM_LIBRARYCARDS = 160
NUM_CHECKOUTS = 300

DEFAULT_LOAN_DAYS = 14

FRACTION_LIBRARYCARDS_DELETED = 0.12

PCT_RETURNED = 0.50
PCT_STILLOUT_INWINDOW = 0.40
PCT_OVERDUE = 0.07
PCT_VERY_OVERDUE = 0.03

NUM_HEAVY_BORROWERS = 6
HEAVY_BORROWER_MIN = 20
HEAVY_BORROWER_MAX = 60

AUTHORS_CSV = "data/Author.csv"
GENRES_CSV = "data/Genre.csv"
BOOKS_CSV = "data/Book.csv"
BOOKCOPYCOND_CSV = "data/BookCopyCondition.csv"
BOOKCOPIES_CSV = "data/BookCopy.csv"
CUSTOMERS_CSV = "data/Customer.csv"
LIBCARDS_CSV = "data/LibraryCard.csv"
CHECKOUTS_CSV = "data/Checkout.csv"

CONDITIONS = ["New", "Like New", "Very Good", "Good", "Acceptable", "Poor"]

FIRST_NAMES = [
    "Alex","Jordan","Taylor","Casey","Riley","Morgan","Quinn","Avery","Parker","Rowan",
    "Cameron","Emerson","Harper","Reese","Skyler","Hayden","Logan","Jamie","Drew","Remy",
    "Noah","Liam","Mason","Ethan","Oliver","Elijah","Lucas","Levi","Henry","Mateo",
    "Sophia","Isabella","Mia","Charlotte","Amelia","Evelyn","Abigail","Emily","Avery",
    "Kai","Maya","Zoe","Leo","Theo","Aria","Ivy","Nova","Eden","Mila",
    "Nora","Sadie","Layla","Aiden","Wyatt","Miles","Jude","Rory","Sage","June"
]
LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Martinez","Lopez",
    "Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez",
    "Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker","Young",
    "Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores","Green","Adams",
    "Baker","Nelson","Carter","Mitchell","Perez","Roberts","Phillips","Turner","Campbell","Parker"
]

DOMAINS = [
    "gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","proton.me",
    "aol.com","live.com","pm.me","msn.com"
]

GENRE_NAMES = [
    "Fiction","Non-Fiction","Fantasy","Science","History","Biography",
    "Mystery","Horror","Romance","Philosophy","Self-Help","Poetry"
]

CATEGORY_MAP = {
    "fiction":"Fiction","novel":"Fiction","literary":"Fiction","literature":"Fiction",
    "non-fiction":"Non-Fiction","nonfiction":"Non-Fiction","essay":"Non-Fiction",
    "fantasy":"Fantasy","sci-fi":"Science","science fiction":"Science","science":"Science",
    "history":"History","biography":"Biography","memoir":"Biography",
    "mystery":"Mystery","thriller":"Mystery","crime":"Mystery","horror":"Horror",
    "romance":"Romance","philosophy":"Philosophy","self-help":"Self-Help","poetry":"Poetry"
}

def rand_choice(seq):
    return seq[random.randrange(len(seq))]

def slugify(s):
    return ''.join(ch for ch in str(s).lower() if ch.isalnum())

def random_username(first, last):
    f = slugify(first); l = slugify(last)
    variants = [(f,l),(l,f),(f,),(l,),(f[:1],l),(l,f[:1])]
    base = rand_choice(variants)
    sep = rand_choice([".", "_", "-", ""])
    name = sep.join([p for p in base if p])
    if random.random() < 0.7:
        name += str(random.randint(0,9999))
    return name or f"user{random.randint(10,99)}"

def unique_email(first,last,seen):
    for _ in range(3000):
        e = f"{random_username(first,last)}@{rand_choice(DOMAINS)}"
        if e not in seen:
            seen.add(e); return e
    while True:
        e = f"{slugify(first)}{slugify(last)}{random.randint(1000,9999)}@{rand_choice(DOMAINS)}"
        if e not in seen:
            seen.add(e); return e

def normalize_isbn(s):
    return "".join(ch for ch in str(s) if ch and ch.isdigit())

def detect_books_source():
    for name in ("BooksFull.csv", "AllBooks.csv", "books.csv", "Books.csv"):
        if os.path.exists(name):
            return name
    raise SystemExit("Place your big 7k source CSV here (BooksFull.csv / AllBooks.csv / books.csv / Books.csv). We only read it.")

def map_category_to_genre(categories_value):
    text = (categories_value or "").lower()
    for key, genre in CATEGORY_MAP.items():
        if key in text:
            return genre
    return rand_choice(GENRE_NAMES)

def read_source_books(limit):
    src = detect_books_source()
    rows = []
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            isbn13 = row.get("isbn13") or row.get("ISBN13") or row.get("ISBN") or row.get("isbn")
            title = row.get("title") or row.get("Title") or row.get("BookTitle")
            subtitle = row.get("subtitle") or row.get("Subtitle") or ""
            authors = row.get("authors") or row.get("Authors") or row.get("Author")
            thumbnail = row.get("thumbnail") or row.get("Thumbnail") or row.get("cover") or row.get("Cover")
            categories = row.get("categories") or row.get("Categories") or ""
            isbn_norm = normalize_isbn(isbn13)
            if len(isbn_norm) != 13:
                continue
            if not (title and authors and thumbnail):
                continue
            # Filter out books with problematic multi-author separators
            authors_str = str(authors).strip()
            if ';' in authors_str or '|' in authors_str or authors_str.count(',') > 2:
                continue
            full_title = f"{title}: {subtitle}" if subtitle else title
            rows.append({
                "isbn13": isbn_norm,
                "title": full_title.strip(),
                "authors": authors_str,
                "thumbnail": str(thumbnail).strip(),
                "genre_name": map_category_to_genre(categories)
            })
    if len(rows) < limit:
        raise SystemExit(f"Source lacks {limit} clean rows (need isbn13/title/authors/thumbnail). Found {len(rows)}.")
    random.shuffle(rows)
    return rows[:limit]

def generate_ids(start_min=100_000, spread=900_000, count=1):
    start = random.randint(start_min, start_min + spread)
    return list(range(start, start + count))

def parse_author_name(author_str):
    """Extract first and last name from author string. Returns (FirstName, LastName)."""
    # Handle formats like: "J.K. Rowling", "Rowling, J.K.", "John Smith"
    author_str = author_str.strip()
    if not author_str:
        return ("Unknown", "Author")

    # Remove common suffixes
    for suffix in [" Jr.", " Sr.", " III", " II", " IV"]:
        author_str = author_str.replace(suffix, "")

    # If contains comma, assume "Last, First" format
    if "," in author_str:
        parts = author_str.split(",", 1)
        last = parts[0].strip()
        first = parts[1].strip() if len(parts) > 1 else "Unknown"
        return (first, last)

    # Otherwise assume "First Last" format
    parts = author_str.split()
    if len(parts) == 0:
        return ("Unknown", "Author")
    elif len(parts) == 1:
        return (parts[0], parts[0])
    else:
        # First name is first part, last name is everything else
        first = parts[0]
        last = " ".join(parts[1:])
        return (first, last)

def generate_authors(clean_rows):
    """Generate unique authors from book data."""
    seen_authors = {}  # (first, last) -> AuthorID
    authors = []
    author_ids = generate_ids(count=1)[0]

    for rec in clean_rows:
        # Take first author if multiple (separated by /, &, or 'and')
        author_str = rec["authors"]
        for sep in ["/", " & ", " and "]:
            if sep in author_str:
                author_str = author_str.split(sep)[0]
                break

        first, last = parse_author_name(author_str)
        key = (first, last)

        if key not in seen_authors:
            aid = author_ids
            seen_authors[key] = aid
            authors.append({"AuthorID": str(aid), "FirstName": first, "LastName": last})
            author_ids += 1

        # Store author ID for book linking
        rec["author_id"] = str(seen_authors[key])

    return authors

def generate_genres():
    return [{"GenreID": str(i), "Name": name} for i, name in enumerate(GENRE_NAMES, start=1)]

def generate_conditions():
    return [{"ConditionID": str(i), "Condition": cond} for i, cond in enumerate(CONDITIONS, start=1)]

def genre_id_by_name(genres, name):
    for g in genres:
        if g["Name"] == name:
            return g["GenreID"]
    return rand_choice([g["GenreID"] for g in genres])

def generate_books_and_copies(clean_rows, genres, conditions):
    books = []
    copies = []
    book_ids = generate_ids(count=len(clean_rows))
    next_copy = generate_ids(count=1)[0]
    today = datetime.today().date()

    # Track unique (AuthorID, Title) to prevent duplicates
    seen_author_title = set()

    for rec, bid in zip(clean_rows, book_ids):
        author_title_key = (rec["author_id"], rec["title"])

        # Skip if we've already added this author/title combination
        if author_title_key in seen_author_title:
            continue
        seen_author_title.add(author_title_key)

        books.append({
            "BookID": str(bid),
            "ISBN": rec["isbn13"],
            "CoverImg": rec["thumbnail"],
            "AuthorID": rec["author_id"],
            "Title": rec["title"],
            "GenreID": genre_id_by_name(genres, rec["genre_name"])
        })
        # Generate 1-3 copies per book with random conditions and purchase dates
        for _ in range(random.randint(1,3)):
            cond = rand_choice(conditions)
            # Random purchase date in the past 1-5 years
            days_ago = random.randint(365, 365*5)
            purchased = today - timedelta(days=days_ago)
            copies.append({
                "BookCopyID": str(next_copy),
                "BookID": str(bid),
                "ConditionID": cond["ConditionID"],
                "PurchasedDate": iso_date(purchased)
            })
            next_copy += 1
    return books, copies

def iso_date(d): return d.strftime("%Y-%m-%d")

def generate_customers(n):
    seen=set(); customers=[]
    for cid in generate_ids(count=n):
        first = rand_choice(FIRST_NAMES); last = rand_choice(LAST_NAMES)
        customers.append({
            "CustomerID": str(cid),
            "EmailAddress": unique_email(first,last,seen),
            "FirstName": first,
            "LastName": last
        })
    return customers

def generate_librarycards(customers, n, deleted_fraction):
    selected = random.sample(customers, min(n, len(customers)))
    cards=[]
    for person, card_id in zip(selected, generate_ids(count=len(selected))):
        deleted = random.random() < deleted_fraction
        # Inactive = 1 if deleted, otherwise randomly 0 or 1 (20% inactive)
        inactive = "1" if deleted else ("1" if random.random() < 0.2 else "0")
        cards.append({
            "LibraryCardID": str(card_id),
            "CustomerID": person["CustomerID"],
            "Inactive": inactive,
            "Deleted": deleted
        })
    return cards

def make_checkout_for_type(copy_id, lender_card_id, card_deleted, outcome_type):
    today = datetime.today().date()
    if card_deleted:
        outcome_type = "returned"  # no active loans on deleted accounts
    if outcome_type == "inwindow":
        checkout = today - timedelta(days=random.randint(0,13))
        due = checkout + timedelta(days=DEFAULT_LOAN_DAYS)
        date_returned = ""
    elif outcome_type == "overdue":
        checkout = today - timedelta(days=random.randint(15,28))
        due = checkout + timedelta(days=DEFAULT_LOAN_DAYS)
        date_returned = ""
    elif outcome_type == "very_overdue":
        checkout = today - timedelta(days=random.randint(60,90))
        due = checkout + timedelta(days=DEFAULT_LOAN_DAYS)
        date_returned = ""
    else:  # returned
        checkout = today - timedelta(days=random.randint(1,120))
        due = checkout + timedelta(days=DEFAULT_LOAN_DAYS)
        # 80% on-time, 20% late by 1-21 days
        if random.random() < 0.8:
            ret = checkout + timedelta(days=random.randint(1, DEFAULT_LOAN_DAYS))
        else:
            ret = due + timedelta(days=random.randint(1,21))
        date_returned = iso_date(ret)
    return {
        "BookCopyID": copy_id,
        "LenderLibraryCardID": lender_card_id,
        "CheckoutDate": iso_date(checkout),
        "DueDate": iso_date(due),
        "DateReturned": date_returned
    }

def generate_checkouts(copies, cards, n_total):
    copy_ids = [c["BookCopyID"] for c in copies]
    # Track inactive status (Inactive == "1"), not just deleted
    card_pool = [(c["LibraryCardID"], c["Inactive"] == "1") for c in cards]
    inactive_lookup = {c["LibraryCardID"]: (c["Inactive"] == "1") for c in cards}

    n_returned = max(0, int(n_total * PCT_RETURNED))
    n_inwindow = max(0, int(n_total * PCT_STILLOUT_INWINDOW))
    n_overdue = max(0, int(n_total * PCT_OVERDUE))
    n_very_overdue = max(0, int(n_total * PCT_VERY_OVERDUE))
    assigned = n_returned + n_inwindow + n_overdue + n_very_overdue
    for _ in range(n_total - assigned):
        n_inwindow += 1

    outcomes = (["returned"]*n_returned + ["inwindow"]*n_inwindow +
                ["overdue"]*n_overdue + ["very_overdue"]*n_very_overdue)
    random.shuffle(outcomes)

    checkouts = []
    currently_checked_out = set()  # Track copies with NULL DateReturned
    heavy_candidates = [cid for cid,_ in card_pool]
    heavy_pick = random.sample(heavy_candidates, min(NUM_HEAVY_BORROWERS, len(heavy_candidates)))
    heavy_quota = {cid: random.randint(HEAVY_BORROWER_MIN, HEAVY_BORROWER_MAX) for cid in heavy_pick}

    for outcome in outcomes:
        if heavy_quota:
            cid = random.choice(list(heavy_quota.keys()))
            heavy_quota[cid] -= 1
            if heavy_quota[cid] <= 0:
                del heavy_quota[cid]
            is_inactive = inactive_lookup[cid]
        else:
            cid, is_inactive = rand_choice(card_pool)

        # Select book copy: if outcome is not returned, pick from available copies only
        if outcome != "returned":
            available = [c for c in copy_ids if c not in currently_checked_out]
            if not available:
                # If all copies are checked out, skip this checkout or force it to be returned
                outcome = "returned"
                copy_id = rand_choice(copy_ids)
            else:
                copy_id = rand_choice(available)
                currently_checked_out.add(copy_id)
        else:
            copy_id = rand_choice(copy_ids)

        checkouts.append(make_checkout_for_type(copy_id, cid, is_inactive, outcome))

    random.shuffle(checkouts)
    start_id = generate_ids(count=1)[0]
    for i, r in enumerate(checkouts):
        r["CheckoutID"] = str(start_id + i)
    return [{
        "CheckoutID": r["CheckoutID"],
        "BookCopyID": r["BookCopyID"],
        "LenderLibraryCardID": r["LenderLibraryCardID"],
        "CheckoutDate": r["CheckoutDate"],
        "DueDate": r["DueDate"],
        "DateReturned": r["DateReturned"],
    } for r in checkouts]

def write_csv(path, fieldnames, rows):
    with open(path, "w", newline='', encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

def main():
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    clean_rows = read_source_books(BOOKS_TARGET_COUNT)
    authors = generate_authors(clean_rows)  # Must be called before books (modifies clean_rows)
    genres = generate_genres()
    conditions = generate_conditions()
    books, copies = generate_books_and_copies(clean_rows, genres, conditions)
    customers = generate_customers(NUM_CUSTOMERS)
    cards = generate_librarycards(customers, NUM_LIBRARYCARDS, FRACTION_LIBRARYCARDS_DELETED)
    checkouts = generate_checkouts(copies, cards, NUM_CHECKOUTS)

    write_csv(AUTHORS_CSV, ["AuthorID","FirstName","LastName"], authors)
    write_csv(GENRES_CSV, ["GenreID","Name"], genres)
    write_csv(BOOKCOPYCOND_CSV, ["ConditionID","Condition"], conditions)
    write_csv(BOOKS_CSV, ["BookID","ISBN","CoverImg","AuthorID","Title","GenreID"], books)
    write_csv(BOOKCOPIES_CSV, ["BookCopyID","BookID","ConditionID","PurchasedDate"], copies)
    write_csv(CUSTOMERS_CSV, ["CustomerID","EmailAddress","FirstName","LastName"], customers)
    write_csv(LIBCARDS_CSV, ["LibraryCardID","CustomerID","Inactive"], [{"LibraryCardID":c["LibraryCardID"],"CustomerID":c["CustomerID"],"Inactive":c["Inactive"]} for c in cards])
    write_csv(CHECKOUTS_CSV, ["CheckoutID","BookCopyID","LenderLibraryCardID","CheckoutDate","DueDate","DateReturned"], checkouts)
    print("Done. Generated CSVs in data/:")
    for n in (AUTHORS_CSV, GENRES_CSV, BOOKCOPYCOND_CSV, BOOKS_CSV, BOOKCOPIES_CSV, CUSTOMERS_CSV, LIBCARDS_CSV, CHECKOUTS_CSV):
        print(" -", n)

if __name__ == "__main__":
    random.seed()
    main()
