from flask import Flask,g,render_template,flash,redirect,url_for,request,abort
import models,forms
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from flask_bcrypt import check_password_hash
DEBUG = True
PORT = 3000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = "dkasjfadffdfadjafnadnfm"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #if user isnt logged in redirect them to login view
#also names the method used for this view/route to be login so make sure thats the methods name
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None # when its not existant in the db
@app.route('/')
def index():
    # form = forms.RegisterForm()
    # return render_template("register.html",form=form)
    stream = models.Post.select().limit(100)
    return render_template("stream.html",stream=stream)

@app.before_request
def before_request():
    """Connect to db before each req"""
    g.db = models.DATABASE
    g.db.connect()#use it to set up global variables to have avaiable everywhere
    g.user = current_user
@app.after_request
def after_request(response):
    """Close db connection after each completed req"""
    g.db.close()
    return response
@app.route("/login", methods=("GET","POST"))
def login():
    form2 = forms.LoginForm()
    if form2.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form2.email.data) #if the email is in the db
        except models.DoesNotExist:
            flash("email or password doesnt exist")
        else:#if we dont hit the exception
            #if the users password attribute matches that data inputed above then login
            if check_password_hash(user.password,form2.password.data):
                login_user(user) #creates a session on the browser w a cookie
                #cookie ref a user acct
                flash("logged in",'success')
                return redirect(url_for('index'))# redirect to the url for index
            else:
                flash("email or password doesnt exist","error")
    return render_template('login.html',form=form2)


@app.route("/register",methods=("GET","POST"))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit(): #detects that the form has been submitted, checks validity
        flash("wooh u reg'd",'success')
        models.User.create_user(username=form.username.data,email=form.email.data,password=form.password.data)
        return redirect(url_for('index')) #redirect
    return render_template("register.html",form=form)
@app.route("/logout",methods=("GET","POST"))
@login_required
def logout():
    logout_user()#deletes the cookie we created with login_user
    flash("LOGGEDDEADOUT")
    return redirect(url_for("index"))

@app.route("/new_post",methods=("GET","POST"))
@login_required
def post():
    form = forms.PostForm() #build form send it to template
    if form.validate_on_submit():
        # this is where we instantiate,process,and send our post form to the template
        # after the form is validly submitted,
        # we create a new post object with the users data that was inputted
        models.Post.create(user=g.user._get_current_object(),content=form.content.data)
        flash("thanks","success")
        return redirect(url_for('index'))
    return render_template('post.html',form=form)
@app.route("/stream")# all posts
@app.route("/stream/<username>")#that users posts
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:

            user = models.User.select().where(models.User.username**username)#** = is like matches similar disregards case
            stream = user.posts.limit(100)
        except models.DoesNotExist:
            abort(404)# url doesnt exist
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = "user_steam.html"
    return render_template(template,stream=stream,user=user)
@app.route("/post/<int:post_id>")
def view_post(post_id):

    posts = models.Post.select.where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)#wont get models doesnt exist cuz we can get back a no from our where
    return render_template("stream.html",stream=posts)

@app.route("/follow/<username>")
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(from_user=g.user._get_current_object(),to_user=to_user)
        except models.IntegrityError:
            abort(404)
        else:
            flash("youre now following{}.".format(to_user.username),"success")
    return redirect(url_for("stream",username=to_user.username))
@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.Relationship.get(from_user=g.user._get_current_object(),to_user=to_user).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("youre now following{}.".format(to_user.username),"success")
    return redirect(url_for("stream",username=to_user.username))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404



if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(username="fucku",email="nut@butt.com",password='password',admin=True)

    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)

