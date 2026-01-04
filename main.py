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

            if row and check_password_hash(row[5], password):
                new_user = User(*row)
                login_user(new_user)

                isadmin = row[6]
                iskeeper = row[7]
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
    return "admin page"

@app.route("/keeper/", methods=("GET", "POST"))
@app.route("/keeper/profile/", methods=("GET", "POST"))
@login_required
def keeper_profile():
    return render_template("keeper-profile.html")

@app.route("/keeper/show-books/")
@login_required
def show_books():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select * from books"
        cur.execute(query)
        books = cur.fetchall()

        cur.close()
    
    return render_template("show-books.html", books=books)

@app.route("/keeper/add-book/", methods=("GET", "POST"))
@login_required
def add_book():
    if request.method == "POST":
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

    return render_template("add-book.html", authors=authors)

@app.route("/keeper/update-qty/", methods=("GET", "POST"))
@login_required
def update_qty():
    if request.method == "POST":
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

@app.route("/keeper/fetch-id/", methods=("POST",))
@login_required
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

@app.route("/keeper/pending-orders/")
@login_required
def pending_orders():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select oid, username, bname, bauthor from orders o, users u, books b where status = 1 and o.uid = u.uid and o.bid = b.bid"
        cur.execute(query)
        pendings = cur.fetchall()

        cur.close()
    
    return render_template("pending-orders.html", pendings=pendings)

@app.route("/keeper/accept-order/", methods=("POST",))
@login_required
def accept_order():
    json_data: dict[str, str] = request.json
    oid = json_data.get("oid")
    brw_date = datetime.date.today()
    exp_date = brw_date + datetime.timedelta(7)
    
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        update_orders = "update orders set brw_date = ?, exp_date = ?, fine = 0, returned = 0, status = 2 where oid = ?"
        cur.execute(update_orders, (brw_date, exp_date, oid))

        conn.commit()
        cur.close()
    
    return jsonify({"success": True})

@app.route("/keeper/reject-order/", methods=("POST",))
@login_required
def reject_order():
    json_data: dict[str, str] = request.json
    oid = json_data.get("oid")

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        update_orders = "update orders set status = 3 where oid = ?"
        cur.execute(update_orders, (oid,))

        update_books = "update books set qty = qty+1 where bid = (select bid from orders where oid = ?)"
        cur.execute(update_books, (oid,))

        conn.commit()
        cur.close()
    
    return jsonify({"success": True})

@app.route("/keeper/borrowed-books/")
@login_required
def borrowed_books():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select oid, username, bname, bauthor, brw_date, exp_date, fine from orders o, users u, books b where status = 2 and o.uid = u.uid and o.bid = b.bid"
        cur.execute(query)
        borrows = cur.fetchall()

        cur.close()
    
    return render_template("borrowed-books.html", borrows=borrows)

@app.route("/keeper/return-book/", methods=("POST",))
@login_required
def return_book():
    json_data: dict[str, str] = request.json
    oid = json_data.get("oid")

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        update_orders = "update orders set status = 4 where oid = ?"
        cur.execute(update_orders, (oid,))

        update_books = "update books set qty = qty+1 where bid = (select bid from orders where oid = ?)"
        cur.execute(update_books, (oid,))

        conn.commit()
        cur.close()
    
    return jsonify({"success": True})

@app.route("/keeper/history/")
@login_required
def keeper_history():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select oid, username, bname, bauthor, brw_date, exp_date, fine, status from orders o, users u, books b where status >= 3 and o.uid = u.uid and o.bid = b.bid"
        cur.execute(query)
        histories = cur.fetchall()

        cur.close()
    
    return render_template("keeper-history.html", histories=histories)

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

            bid_query = "select bid, status from orders where uid = ? and status < 3"
            cur.execute(bid_query, (current_user.uid,))
            order_info_list = cur.fetchall()

            cur.close()
        
        order_info_json = {bid: status for bid, status in order_info_list}
        
        return jsonify({"books": books, "order_info_json": order_info_json})
    
    return render_template("borrow-book.html")

@app.route("/user/add-borrow/", methods=("POST",))
@login_required
def add_borrow():
    if request.method == "POST":
        borrow_info: dict[str, str] = request.json
        book_name = borrow_info.get("bookName")
        book_author = borrow_info.get("bookAuthor")
        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            bid_query = "select bid from books where bname = ? and bauthor = ?"
            cur.execute(bid_query, (book_name, book_author))
            bid = cur.fetchone()[0]

            insert_query = "insert into orders (uid, bid, status) values (?, ?, 1)"
            cur.execute(insert_query, (current_user.uid, bid))

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

        query = "select oid, bname, bauthor, brw_date, exp_date, fine, returned, status from orders o, books b where uid = ? and status < 3 and o.bid = b.bid"
        cur.execute(query, (current_user.uid,))
        borrows = cur.fetchall()
        cur.close()
    
    return render_template("check-borrow.html", borrows=borrows)

@app.route("/user/remove-borrow/", methods=("POST",))
@login_required
def remove_borrow():
    remove_data: dict[str, str] = request.json
    if "oid" in remove_data.keys():
        oid = remove_data.get("oid")

        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            update_query = "update books set qty = qty+1 where bid = (select bid from orders where oid = ?)"
            cur.execute(update_query, (oid,))

            delete_query = "delete from orders where oid = ?"
            cur.execute(delete_query, (oid,))

            conn.commit()
            cur.close()
    
    else:
        book_name = remove_data.get("bookName")
        book_author = remove_data.get("bookAuthor")

        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            bid_query = "select bid from books where bname = ? and bauthor = ?"
            cur.execute(bid_query, (book_name, book_author))
            bid = cur.fetchone()[0]

            update_query = "update books set qty = qty+1 where bid = ?"
            cur.execute(update_query, (bid,))

            delete_query = "delete from orders where uid = ? and bid = ? and status = 1"
            cur.execute(delete_query, (current_user.uid, bid))

            conn.commit()
            cur.close()

    return jsonify({"success": True})

@app.route("/user/history/")
@login_required
def user_history():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select oid, bname, bauthor, brw_date, exp_date, fine, status from orders o, books b where uid = ? and status >= 3 and o.bid = b.bid"
        cur.execute(query, (current_user.uid,))
        histories = cur.fetchall()

        cur.close()
    
    return render_template("user-history.html", histories=histories)

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run("0.0.0.0", 80, True)
