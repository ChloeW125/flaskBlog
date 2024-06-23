from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
#Import fields to be able to build form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
#Import validators to validate the string input (this validator in particular will validate the string)
from wtforms.validators import DataRequired, EqualTo, Length
#Import db and datetime so we can track the time of every entry
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
#Import werkzeug to hash passwords
from werkzeug.security import generate_password_hash, check_password_hash

#Create a flask instance
#Create extension to the db
db = SQLAlchemy()
#__name__ helps flask find files in the directory
app = Flask(__name__)
#Create a secret key (to create a CRSF token) for the form to make sure that hackers cannot hijack the form
app.config['SECRET_KEY'] = "56y32888"
#Add the databaase to the app (where URI points to where our database is) 
#Old sqllite db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' #Sqlite used here, can change to other dbs by adjusting the value
#New mysql
#Formatting: app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost(or server)/db_name' 
#pymysql is the new "connector"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:56y32888@localhost/our_users' 
#Initialize the database
db.init_app(app)
#Migrate app with database
migrate = Migrate(app, db)

# Create a blog post model
class Posts(db.Model):
    # Define what to save in this model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now())
    # Slug will adjust text in url for each blog post
    slug = db.Column(db.String(255))

#Create a model (defines what is saved in the database)
class Users(db.Model):
    #Keep track of id (since everyone has a unique id, will make it easy to delete specific entries later), name, email, and date added
    #Define data type in each column in the brackets, specify validation + features for each column
    id = db.Column(db.Integer, primary_key = True) #By using primary keys, each entry will automatically be assigned a unique id, which is exactly what we want
    name = db.Column(db.String(200), nullable=False) #Nullable=false means that the value for the name var cannot be empty
    email = db.Column(db.String(120), nullable=False, unique=True) #Set unique as true because we want everyone to have a unique email
    favourite_colour = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now)
    #Implement password input section for input
    password_hash = db.Column(db.String(128))

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

#Create a user form class
class UserForm(FlaskForm):
    #Define the fields that we want using vars
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_colour = StringField("Favourite Colour")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create name form class
class NamerForm(FlaskForm):
    #Define the fields that we want using vars
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create password form class
class PasswordForm(FlaskForm):
    #Define the fields that we want using vars
    email = StringField("What's Your Email?", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

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
            user = Users(name=form.name.data, email=form.email.data, favourite_colour=form.favourite_colour.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        #Pass the inputted name as a var into the function so it's value can be used later
        name = form.name.data
        #Clear the form
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