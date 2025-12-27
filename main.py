from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   flash,
                   jsonify)

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

@app.route('/', methods=("GET", "POST"))
def index():
    # print(request.headers)
    return render_template("index.html", valid_user=current_user.is_authenticated)

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
            return redirect('/')
        
        except sqlite3.IntegrityError:
            flash(user_data)
            flash("User already exist.")
            return redirect("/register")
    
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
                return redirect("/profile")
            
            else:
                flash("Invalid credentials !!!")
                return redirect("/login")
    
    elif current_user.is_authenticated:
        return redirect("/profile")
    
    return render_template("login.html")

@app.route("/profile/", methods=("GET", "POST"))
@login_required
def profile():
    return render_template("profile.html", username=current_user.username)

@app.route("/profile/borrow-book/", methods=("GET", "POST"))
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
            bid_tup = cur.fetchall()

            cur.close()
        
        bids = [bid[0] for bid in bid_tup]

        return jsonify({"books": books, "borrow_bids": bids})
    
    return render_template("borrow.html")

@app.route("/profile/add-borrow", methods=("POST",))
@login_required
def add_borrow():
    if request.method == "POST":
        borrow_info: dict[str, str] = request.json
        book_name = borrow_info.get("bookName")
        book_author = borrow_info.get("bookAuthor")
        borrow_date = datetime.date.today()
        exp_date = borrow_date + datetime.timedelta(7)
        with sqlite3.connect("library.db") as conn:
            cur = conn.cursor()

            bid_query = "select bid from books where bname=? and bauthor=?"
            cur.execute(bid_query, (book_name, book_author))
            bid = cur.fetchone()[0]

            insert_query = "insert into orders (uid, bid, brw_date, exp_date) values (?, ?, ?, ?)"
            cur.execute(insert_query, (current_user.uid, bid, borrow_date, exp_date))

            update_query = "update books set qty = qty-1 where bid = ? and qty != 0"
            cur.execute(update_query, (bid,))

            conn.commit()
            cur.close()
        
        return jsonify({"success": True})

@app.route("/profile/check-borrow/")
@login_required
def check_borrow():
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()

        query = "select oid, bname, bauthor, brw_date, exp_date, fine from orders o, books b where o.bid = b.bid and uid = ?"
        cur.execute(query, (current_user.uid,))
        borrows = cur.fetchall()
        cur.close()
    
    return render_template("check.html", borrows=borrows)

@app.route("/profile/remove-borrow", methods=("POST",))
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
    return redirect('/')

if __name__ == "__main__":
    app.run("0.0.0.0", 80, True)
