from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   jsonify,
                   abort)

from flask_login import (LoginManager,
                         UserMixin,
                         login_user,
                         logout_user,
                         login_required,
                         current_user)

from werkzeug.security import (generate_password_hash,
                               check_password_hash)

import sqlite3
import datetime

app = Flask(__name__, static_url_path='/')
app.secret_key = "techsubho"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# login_manager.login_message = ''

class User(UserMixin):
    def __init__(self, uid, firstname, lastname, email, username, password, isadmin, iskeeper):
        self.uid = uid
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.username = username
        self.password = password
        self.isadmin = isadmin
        self.iskeeper = iskeeper
    
    def get_id(self):
        return self.uid

@login_manager.user_loader
def load_user(uid):
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select * from users where uid = ?"
        cur.execute(query, (uid,))

        row = cur.fetchone()
        cur.close()

    return User(*row)

@app.before_request
def admin_access():
    # print(request.path)
    if request.path.startswith("/admin/"):
        if not (current_user.is_authenticated and current_user.isadmin):
            abort(403)
    
    elif request.path.startswith("/keeper/"):
        if not (current_user.is_authenticated and current_user.iskeeper):
            abort(403)

    elif request.path.startswith("/user"):
        if (current_user.is_authenticated and current_user.isadmin) or (current_user.is_authenticated and current_user.iskeeper):
            abort(403)

@app.route('/', methods=("GET", "POST"))
def index():
    # print(request.headers)
    return render_template("index.html", current_user=current_user)

@app.route("/register/", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        user_data = request.form.values()
        user_data = list(user_data)
        user_data[4] = generate_password_hash(user_data[4])
        
        try:
            with sqlite3.connect("library.db") as conn:
                cur = conn.cursor()

                query = "insert into users (firstname, lastname, email, username, password) values (?, ?, ?, ?, ?)"
                cur.execute(query, user_data)
                conn.commit()
                cur.close()
            
            flash("Successfully registered.")
            return redirect(url_for("index"))
        
        except sqlite3.IntegrityError:
            flash(user_data)
            flash("User already exist.")
            return redirect(url_for("register"))
    
    return render_template("register.html")

@app.route("/login/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            query = "select * from users where username = ?"
            cur.execute(query, (username,))
            row = cur.fetchone()
            # print(row)

            if row and check_password_hash(row[5], password):
                new_user = User(*row)
                login_user(new_user)

                isadmin = row[6]
                iskeeper = row[7]
                # print(isadmin, iskeeper)
                if isadmin:
                    return redirect(url_for("admin"))
                
                elif iskeeper:
                    return redirect(url_for("keeper_profile"))
                
                return redirect(url_for("user_profile"))
            
            else:
                flash("Invalid credentials !!!")
                return redirect(url_for("login"))
    
    elif current_user.is_authenticated:
        if current_user.isadmin:
            return redirect(url_for("admin"))
        
        elif current_user.iskeeper:
            return redirect(url_for("keeper_profile"))
        
        return redirect(url_for("user_profile"))
    
    return render_template("login.html")

@app.route("/admin/", methods=("GET", "POST"))
@login_required
def admin():
    # print(request.referrer)
    return "admin page"

@app.route("/keeper/", methods=("GET", "POST"))
@app.route("/keeper/profile", methods=("GET", "POST"))
@login_required
def keeper_profile():
    return render_template("keeper-profile.html")

@app.route("/keeper/add-book", methods=("GET", "POST"))
def add_book():
    if request.method == "POST":
        # print(request.form.values())
        new_book = request.form.values()
        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            query = "insert into books (bname, bauthor, qty, rate) values (?, ?, ?, ?)"
            cur.execute(query, tuple(new_book))

            conn.commit()
            cur.close()
        
        flash("Book Added.")
        return redirect(url_for("add_book"))
    
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        search_query = "select distinct bauthor from books"
        cur.execute(search_query)
        author_list = cur.fetchall()

        cur.close()
    
    authors = tuple(map(lambda author: author[0], author_list))
    # print(authors)

    return render_template("add-book.html", authors=authors)

@app.route("/keeper/update-qty", methods=("GET", "POST"))
def update_qty():
    if request.method == "POST":
        print(request.form)
        bid = request.form.get("bid")
        qty = request.form.get("qty")
        operation = request.form.get("operation")
        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            if operation == "add":
                update_query = "update books set qty = qty+? where bid = ?"
                flash("Quantity added successfully.")
            
            elif operation == "remove":
                update_query = "update books set qty = qty-? where bid = ?"
                flash("Quantity removed successfully.")
            
            cur.execute(update_query, (qty, bid))

            conn.commit()
            cur.close()
        
        return redirect(url_for("update_qty"))
    
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        bname_search_query = "select distinct bname from books"
        cur.execute(bname_search_query)
        bname_list = cur.fetchall()

        bauthor_search_query = "select distinct bauthor from books"
        cur.execute(bauthor_search_query)
        bauthor_list = cur.fetchall()

        cur.close()
    
    bnames = tuple(map(lambda bname: bname[0], bname_list))
    bauthors = tuple(map(lambda bauthor: bauthor[0], bauthor_list))

    return render_template("update-qty.html", bnames=bnames, bauthors=bauthors)

@app.route("/keeper/fetch-id", methods=("POST",))
def fetch_id():
    json_data: dict[str, str] = request.json
    bname = json_data.get("bname")
    bauthor = json_data.get("bauthor")
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select bid from books where bname = ? and bauthor = ?"
        cur.execute(query, (bname, bauthor))
        bid = cur.fetchone()

        cur.close()
    
    return jsonify({"bid": bid[0] if bid is not None else 0})

@app.route("/user/", methods=("GET", "POST"))
@app.route("/user/profile/", methods=("GET", "POST"))
@login_required
def user_profile():
    return render_template("user-profile.html", username=current_user.username)

@app.route("/user/borrow-book/", methods=("GET", "POST"))
@login_required
def borrow_book():
    if request.method == "POST":
        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            query = "select bid, bname, bauthor, qty from books"
            cur.execute(query)
            books = cur.fetchall()

            bid_query = "select bid from orders where uid = ?"
            cur.execute(bid_query, (current_user.uid,))
            bid_list = cur.fetchall()

            cur.close()
        
        bids = tuple(map(lambda bid: bid[0], bid_list))

        return jsonify({"books": books, "borrow_bids": bids})
    
    return render_template("borrow.html")

@app.route("/user/add-borrow/", methods=("POST",))
@login_required
def add_borrow():
    if request.method == "POST":
        borrow_info: dict[str, str] = request.json
        book_name = borrow_info.get("bookName")
        book_author = borrow_info.get("bookAuthor")
        brw_date = datetime.date.today()
        exp_date = brw_date + datetime.timedelta(7)
        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            bid_query = "select bid from books where bname = ? and bauthor = ?"
            cur.execute(bid_query, (book_name, book_author))
            bid = cur.fetchone()[0]

            insert_query = "insert into orders (uid, bid, brw_date, exp_date) values (?, ?, ?, ?)"
            cur.execute(insert_query, (current_user.uid, bid, brw_date, exp_date))

            update_query = "update books set qty = qty-1 where bid = ? and qty != 0"
            cur.execute(update_query, (bid,))

            conn.commit()
            cur.close()
        
        return jsonify({"success": True})

@app.route("/user/check-borrow/")
@login_required
def check_borrow():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select oid, bname, bauthor, brw_date, exp_date, fine from orders o, books b where o.bid = b.bid and uid = ?"
        cur.execute(query, (current_user.uid,))
        borrows = cur.fetchall()
        cur.close()
    
    return render_template("check.html", borrows=borrows)

@app.route("/user/remove-borrow/", methods=("POST",))
@login_required
def remove_borrow():
    if request.method == "POST":
        remove_data: dict[str, str] = request.json
        oid = remove_data.get("oid")

        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            update_query = "update books set qty = qty+1 where bid = (select bid from orders where oid = ?)"
            cur.execute(update_query, (oid,))

            insert_query = "delete from orders where oid = ?"
            cur.execute(insert_query, (oid,))

            conn.commit()
            cur.close()

    return jsonify({"success": True})

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run("0.0.0.0", 80, True)
