from flask import Flask, render_template, flash, request, redirect, url_for
#Import db and datetime so we can track the time of every entry
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
#Import werkzeug to hash passwords
from werkzeug.security import generate_password_hash, check_password_hash
# Import tools for login
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# Import forms into app.py
from webforms import LoginForm, PostForm, UserForm, NamerForm, PasswordForm, SearchForm
# Import rich text editor to initialize the extension
from flask_ckeditor import CKEditor

# Source(s) for the robot avatar image: <a href="https://www.flaticon.com/free-icons/robot" title="robot icons">Robot icons created by Freepik - Flaticon</a>
# <a href="https://www.flaticon.com/free-icons/robot" title="robot icons">Robot icons created by Freepik - Flaticon</a>
# <a href="https://www.flaticon.com/free-icons/robot" title="robot icons">Robot icons created by Smashicons - Flaticon</a>
# <a href="https://www.flaticon.com/free-icons/robot" title="robot icons">Robot icons created by Freepik - Flaticon</a>
# <a href="https://www.flaticon.com/free-icons/bot" title="bot icons">Bot icons created by Smashicons - Flaticon</a>

#Create a flask instance
#Create extension to the db
db = SQLAlchemy()
#__name__ helps flask find files in the directory
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
#Create a secret key (to create a CRSF token) for the form to make sure that hackers cannot hijack the form
app.config['SECRET_KEY'] = "56y32888"
#Add the databaase to the app (where URI points to where our database is) 
#Old sqllite db
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' #Sqlite used here, can change to other dbs by adjusting the value
#New mysql
#Formatting: app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost(or server)/db_name' 
#pymysql is the new "connector"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:56y32888@localhost/our_users' 
#Initialize the database
db.init_app(app)
#Migrate app with database
migrate = Migrate(app, db)

# Flask login stuff
# Instantiates login tools
login_manager = LoginManager()
# Pass in this app into the login manager so it knows what to work with
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load info from database into the login manager so the login manager can use the data
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
# Create a blog post model
class Posts(db.Model):
    # Define what to save in this model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now())
    # Slug will adjust text in url for each blog post
    slug = db.Column(db.String(255))
    # Associate each post to a specific user (the one who made the post) by creating a foreign key to link users (the foreign key will refer to the primary key of the user (i.e. the user's id))
    # Link each post to a poster via user ids
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Create a model (defines what is saved in the database)
class Users(db.Model, UserMixin):
    #Keep track of id (since everyone has a unique id, will make it easy to delete specific entries later), name, email, and date added
    #Define data type in each column in the brackets, specify validation + features for each column
    id = db.Column(db.Integer, primary_key = True) #By using primary keys, each entry will automatically be assigned a unique id, which is exactly what we want
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False) #Nullable=false means that the value for the name var cannot be empty
    email = db.Column(db.String(120), nullable=False, unique=True) #Set unique as true because we want everyone to have a unique email
    favourite_colour = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    # ISSUE: # String used to save the NAME of the photo
    # profile_pic = db.Column(db.String(), nullable=True)
    #Implement password input section for input
    password_hash = db.Column(db.String(128))
    # Allow users to have many posts
    # Backref will keep track of the poster for posts
    posts = db.relationship('Posts', backref='poster')

    #Create password properties
    #Create functions to hash password and check hash to make sure that it matches up with the password
    @property
    def password(self):
        #Raise attribute error because we don't want the password to be given out, instead we can give out the password hash
        raise AttributeError('Password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        #Take whatever is in the password field and generate a password hash for that password
        self.password_hash = generate_password_hash(password)

    # Check to make sure that the hash goes with the password and vice versa
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    #Create a string to define what will show up on the screen
    def __repr__(self):
        return '<Name %r>' % self.name

#Create table for db
with app.app_context():
    db.create_all()

#Create a route so that the website (specifically the home page) can be accessed (via URL) 
@app.route('/')
#Create function to define the home page
def index():
    #Create new variable, then pass in this variable to the template to be used to be displayed
    first_name = "Chloe"
    stuff = "This is <strong>Bold</strong> Text"

    pizza = ["Pepperoni", "Cheese", 41]
    #Program will go to the template folder and find the right file to display
    return render_template("index.html", first_name=first_name, stuff=stuff, pizza=pizza)

#Create admin page 
@app.route('/admin')
@login_required
def admin():
    # Set var id equal to the current id
    id = current_user.id
    
    # Only users with the admin ID (which is set to 20 for this example) are able to access the admin page
    if id == 20:
        return render_template("admin.html")
    else:
        flash("Sorry you must be the Admin to access the Admin page")
        return redirect(url_for('dashboard'))

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    #Create a form to pass into the display using the UserForm class created earlier
    form = UserForm()
    #If someone submits the form, assign the inputted name value to the name variable
    if form.validate_on_submit():
        #Make sure that each user has a different valid email
        #This will go over all existing emails and find the first email entry with the same email as the one inputted
        user = Users.query.filter_by(email=form.email.data).first()
        #Is there is no existing email in the database, add the inputted name, email, etc.. Otherwise, don't
        if user is None:
            #Hash the password submitted to the form
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256:600000")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favourite_colour=form.favourite_colour.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        #Pass the inputted name as a var into the function so it's value can be used later
        name = form.name.data
        #Clear the form
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.favourite_colour.data = ''
        form.password_hash.data = ''
        #Implement flash function to make flash message pop-up on the screen
        flash("User added successfully!")
    #Variable to hold all the values inside the database (to be used to display the info in the database)
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

#<> allows us to pass a name
@app.route('/user/<name>')
def user(name):
    #Render the formatting in the user.html file. Also pass in the name variable so it can be accessed in the html file
    return render_template("user.html", username=name)

#Create name page
#Give the route some methods to allow the form to get and post information into/out of the form
@app.route('/name', methods=['GET', 'POST'])
def name():
    #Set name as none right now because when the page first opens the user has not entered their name yet. But the value of this var will change after the user enters in their name in the form
    name = None
    #Pass in the form that we want to use to the webpage
    form = NamerForm()
    #Validate form
    #If someone submits the form, assign the inputted name value to the name variable
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        #Implement flash function to make flash message pop-up on the screen
        flash("Form submitted successfully!")

    #Pass name and from vars onto the page
    return render_template("name.html", name=name, form=form)

#Create password test page
#Give the route some methods to allow the form to get and post information into/out of the form
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    #Set email and password as none right now because when the page first opens the user has not entered their name yet. But the value of this var will change after the user enters in their name in the form
    email = None
    password = None
    pw_to_check = None
    passed = None
    #Pass in the form that we want to use to the webpage
    form = PasswordForm()
    #Validate form
    #If someone submits the form, assign the inputted name value to the name variable
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        #Clear the form
        form.email.data = ''
        form.password_hash.data = ''

        # In the database, look up the user with the email that we are looking for (and return the first result if it already exists)
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check if the hashed password in the database is the same as the user's inputted password (i.e. if the right password was entered or not), return boolean value
        passed = check_password_hash(pw_to_check.password_hash, password)

    #Pass name and from vars onto the page
    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)

# Create new page to update database records
# Pass in the id of the entry we want to update
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
# Pass in the id that we want to update in the function
def update(id):
    # Create a form to update user info
    form = UserForm()
    # Determine what name in the database to update by calling query looking for the id
    name_to_update = Users.query.get_or_404(id)
    # If the request from the user is to post, update database with inputted new info
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_colour = request.form['favourite_colour']
        name_to_update.username = request.form['username']
        # Try to update info in database. If it doesn't work, then return an error message
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error! looks like there was an problem updating, please try again.")
            return render_template("update.html", form=form, name_to_update=name_to_update) 
    # Else if the user is just going to the page (before they make their changes, etc.), simply display the page
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id) 

#Create route to delete user entries
@app.route('/delete/<int:id>')  
def delete(id):
    name = None
    #Create a form to pass into the display using the UserForm class created earlier
    form = UserForm()
    #Look for user with selected id in database
    user_to_delete = Users.query.get_or_404(id)

    #Delete the record from the database
    try:
        db.session.delete(user_to_delete)
        #Commit change to database
        db.session.commit()
        #Pop-up flash message
        flash("User deleted successfully!")
        #Return back to page
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    #Throw error message if it does not work
    except:
        flash("Whoops! There was a problem deleting the user, try again.")
        #Pass in id so that id can be accessed in the html page
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    
# Add a posts page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        # Collect id of the poster and store under poster var
        poster = current_user.id
        # If the data in the form has been validated and submitted, collect the data in the form to be added to the database
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        # Redirect back to the form page after submission, and clear all fields
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''
        # Add the data in the form to the database
        db.session.add(post)
        db.session.commit()

        # Add a flash message telling the user the data was submitted successfully
        flash("Blog Post Submitted Successfully")
    # Redirect to the webpage
    return render_template("add_post.html", form=form)

# Make page to display blog posts
@app.route('/posts')
def posts():
    # Grab all posts from the database, ordered by posting date
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

# Make page to display individual blog posts
# Use the id number of each post to reference the specific blog post of interest
@app.route('/posts/<int:id>')
def post(id):
    # Pass in a query that looks up specific blog post in the database using the given id. If the post isn't found, return 404 error
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# Make a page to edit blog posts
# Use the id number of each post to reference the specific blog post of interest
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
# Add decorator so that only logged-in users can access this page
@login_required
def edit_post(id):
    # Pass in a query that looks up specific blog post in the database using the given id. If the post isn't found, return 404 error
    post = Posts.query.get_or_404(id)
    form = PostForm()
    # If form is submitted and validated, then commit the (updated) post title, author, etc. to the database 
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        
        # Update the database
        db.session.add(post)
        db.session.commit()

        # Return message to tell user about successful update
        flash("Post has been successfully updated!")

        # Return back to the individual blog post page
        return redirect(url_for('post', id=post.id))
    # Only allow users to go to the edit page if they are logged in as the poster
    if current_user.id == post.poster_id:
        # Show update post page
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    # Else return error message
    else:
        flash("You aren't authorized to edit this post")
        # Redirect to the posts page
        # Grab all posts from the database, ordered by posting date
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

# Create page to delete posts
# Use the id number of each post to reference the specific blog post of interest
@app.route('/posts/delete/<int:id>')
# Only able to delete if you are logged in
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    # Set var equal to user that is currently logged in
    id = current_user.id

    # If the id of the user who made this post matches the id of the user that is currently logged in, allow the user to delete the post
    if id == post_to_delete.poster.id:
        try:
            # Try to delete post
            db.session.delete(post_to_delete)
            db.session.commit()

            # Send user message about deleting
            flash("Blog post was deleted!")

            # Redirect user to main blog posts page
            # Grab all posts from the database, ordered by posting date
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

        except:
            # If the deleting doesn't work and something goes wrong, return error message
            flash("Whoops! There was a problem deleting the post, try again.")

            # Redirect user to main blog posts page
            # Grab all posts from the database, ordered by posting date
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    # Else user is not able to delete the post
    else:
        # Send user error message about deleting
            flash("You aren't authorized to delete this post!")

            # Redirect user to main blog posts page
            # Grab all posts from the database, ordered by posting date
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

# Create login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Database will grab first (and only because usernames should be unique) user that exists in the form with the given username. There should be a username that is grabbed if the data is indeed valid
        user = Users.query.filter_by(username=form.username.data).first()
        # If the user exists, check the hash to make sure the password inputted is the correct password
        if user:
            # User.password_hash is the thing in the database, form.password.data is the thing we typed in - here we are checking if the passwords match
            if check_password_hash(user.password_hash, form.password.data):
                # Then, this mean that the user has been logged in. They can now be sent to the dashboard
                login_user(user)
                flash("Login successful!")
                return redirect(url_for('dashboard'))
            # Else the password was wrong, throw an error message
            else:
                flash("Wrong password, try again")
        # If there isn't a user, throw an error message
        else:
            flash("That user doesn't exist, try again")

    return render_template('login.html', form=form)

# Create logout page/function
@app.route('/logout', methods=['GET', 'POST'])
# Need to login in order to be able to logout
@login_required
def logout():
    logout_user()
    flash("You have been logged out! Thanks for stopping by!")
    # Return user back to login page
    return redirect(url_for('login'))

# Create dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
# Creates a "barrier" where the user needs to login in order to go to the dashboard
@login_required
def dashboard():
    # Create a form to update user info
    form = UserForm()
    # Get the current user id so it can be used to update the profile info
    id = current_user.id
    # Determine what name in the database to update by calling query looking for the id
    name_to_update = Users.query.get_or_404(id)
    # If the request from the user is to post, update database with inputted new info
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_colour = request.form['favourite_colour']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']
        # name_to_update.profile_pic = request.files['profile_pic']
        # Try to update info in database. If it doesn't work, then return an error message
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error! looks like there was an problem updating, please try again.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update) 
    # Else if the user is just going to the page (before they make their changes, etc.), simply display the page
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id) 
    
    return render_template('dashboard.html')

# Pass info to navBar
#context_processor will pass things into base file
@app.context_processor
def base():
    form = SearchForm()
    # Return dictionary to pass form to the base.html file and then to the navBar (because the base.html file includes the navBar)
    return dict(form=form)

# Create search functionality
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    # Look for posts
    posts = Posts.query
    
    # If form was submitted, 
    if form.validate_on_submit:
        # Get data from the submitted form
        post.searched = form.searched.data
        # Query the database (look for similar content entries)
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        # Return all posts that meet this criteria. Store these posts in the (updated) var 'posts'
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)

#Create custom error pages
#Invalid URL page
#Call on mechanism to take care of the error
@app.errorhandler(404)
#Create function to define the page not found page
def page_not_found(e):
    #Display the code outlined in the 404.html file, 404 at the end of this line indicartes the type of error being handled
    return render_template("404.html"), 404

#Internal server error page
#Call on mechanism to take care of the error
@app.errorhandler(500)
#Create function to define the page
def page_not_found(e):
    #Display the code outlined in the 500.html file, 500 at the end of this line indicartes the type of error being handled
    return render_template("500.html"), 500

# Create a web page that will return JSON (can use to build API)
@app.route('/date')
def get_current_date():
    # Python dictionaries will automatically be converted into JSON in flask
    # Return JSON with date info
    return {"Date": date.today()}

#Run app
if __name__ == "__main__":
    #Set debug to True so errors will be displayed on the screen
    app.run(debug=True)