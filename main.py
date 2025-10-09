from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for)
import oracledb

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.args:
        var = request.args["hello"]
        print(var)
    return render_template("register.html")

# @app.route("/validate", methods=["GET", "POST"])
# def validate():
#     fname = request.form["fname"]
#     phone = request.form["phone"]
#     email = request.form["mail"]
#     print(fname, phone, email)

#     # connecting to database
#     oracledb.init_oracle_client()

#     conn = oracledb.connect(user="shinobi", password="ninja")
#     cur = conn.cursor()

#     query = "insert into registration values (:1, :2, :3, 'techsubho', 'helloworld')"
#     cur.execute(query, [fname, phone, email])
#     conn.commit()

#     return render_template("validate.html")

@app.route("/user-pass", methods=["GET", "POST"])
def user_pass():
    fname = request.form["fname"]
    phone = request.form["phone"]
    email = request.form["mail"]
    # print(fname, phone, email)

    return render_template("userpass.html", fname=fname, phone=phone, email=email)

@app.route("/show-msg", methods=["GET", "POST"])
def show_msg():
    fname = request.form["fname"]
    phone = request.form["phone"]
    email = request.form["mail"]
    uname = request.form["uname"]
    passwd = request.form["passwd"]
    repasswd = request.form["repasswd"]

    if passwd != repasswd:
        return redirect("/register", hello="world")

    print(fname, phone, email, uname, passwd, repasswd)

    # connecting to database
    oracledb.init_oracle_client()

    conn = oracledb.connect(user="shinobi", password="ninja")
    cur = conn.cursor()

    query = "insert into registration values (:1, :2, :3, :4, :5)"
    cur.execute(query, [uname, passwd, fname, phone, email])
    conn.commit()

    return "<h1><center>registration successful</center></h1>"

@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run("localhost", 80, True)
