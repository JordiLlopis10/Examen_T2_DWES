from bson import ObjectId
from flask import Flask, render_template,request,redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_required, logout_user,LoginManager, login_user
from smtplib import SMTP


############ MONGO ######################
client = MongoClient("mongodb://localhost:27017/")
db = client["examen"]

############## FLASK #######################
app = Flask(__name__)
app.secret_key = "nano"
    
############## FLASK-LOGIN #######################    
loginmanager = LoginManager(app)
loginmanager.login_view = "login"
    
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email
    
@loginmanager.user_loader
def load_user(id):
    user_data = db.users.find_one({"_id": ObjectId(id)})
    if user_data:
        return User(str(user_data["_id"]), user_data["email"])
    return None
    
########################### HOME ###################################
@app.route("/")
def home():
    return render_template("home.html")
########################### LOGIN ###################################
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email,password)
        comprobar_email = db.users.find_one({"email":email})
        
        if comprobar_email and check_password_hash(comprobar_email["password"],password):
            user = User(str(comprobar_email["_id"]), comprobar_email["email"])
            login_user(user)
            
            return redirect(url_for("perfil"))
        print("datos invalidos")
    return render_template("login.html")

########################### REGISTER ###################################
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]
        print(username,email,password)
        if email and username and password:
            if len(password) < 6 and len(password) > 12:
                print("contraseña invalida")
            elif password != password2:
                print("Contraseñas no coinciden")
            elif email[0] == " ":
                print("Email invalido")
            elif password.find("$" or "_" or "-" or "*" or "&"):
                hashed_password = generate_password_hash(password)
                db.users.insert_one({"username":username,"email":email,"password":hashed_password})
                print("Registrado correctamente")
                return redirect(url_for("login"))
            
    return render_template("register.html")

########################### PERFIL ###################################
@app.route("/perfil",methods=["GET","POST"])
@login_required
def perfil():

       
    return render_template("perfil.html")

########################### ANYADIR ###################################
@app.route("/anyadir",methods=["GET","POST"])
@login_required
def anyadir():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        autor = request.form["autor"]
        print(nombre,descripcion,autor)
        if nombre and descripcion and autor:
            db.datos.insert_one({"nombre":nombre,"descripcion":descripcion,"autor":autor})
            print("datos insertados correctamente")
            return redirect(url_for("anyadir"))
    datos = list(db.datos.find())
    print(datos)
    return render_template("anyadir.html",datos=datos)

########################### EDIT ###################################
@app.route("/edit/<string:id>", methods=["GET","POST"])
@login_required
def edit(id):
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        autor = request.form["autor"]
        print(nombre,descripcion,autor)
        if nombre and descripcion and autor:
            db.datos.update_one({"_id":ObjectId(id)},{ "$set":{"nombre":nombre,"descripcion":descripcion,"autor":autor}})####Cambiar el contenido del update
            print("datos actualizados correctamente")
            return redirect(url_for("anyadir"))
    
    
    datos = db.datos.find_one({"_id":ObjectId(id)})
    print(datos)
    return render_template("edit.html",datos=datos)

########################### DELETE ###################################
@app.route("/delete/<string:id>", methods=["GET","POST"])
@login_required
def delete(id):
    
    datos = db.datos.find_one({"_id":ObjectId(id)})
    if datos:
        db.datos.delete_one({"_id":ObjectId(id)})
    return redirect(url_for("anyadir"))
    
########################### LOGOUT ###################################
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

########################### ADMIN ###################################
@app.route("/admin",methods=["GET","POST"])
@login_required
def admin():
    datos = list(db.datos.find())
    users = list(db.users.find())
    
    
    return render_template("admin.html",datos=datos,users=users)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    
    
    
    
    
    
    
    
    
    