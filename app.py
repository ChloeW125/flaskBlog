from flask import Flask, render_template
from flask_wtf import FlaskForm
#Import fields to be able to build form
from wtforms import StringField, SubmitField
#Import validators to validate the string input (this validator in particular will validate the string)
from wtforms.validators import DataRequired

#Create a flask instance
#__name__ helps flask find files in the directory
app = Flask(__name__)
#Create a secret key (to create a CRSF token) for the form to make sure that hackers cannot hijack the form
app.config['SECRET_KEY'] = "56y32888"

#Create form class
class NamerForm(FlaskForm):
    #Define the fields that we want using vars
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

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
    #Pass name and from vars onto the page
    return render_template("name.html", name=name, form=form)

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

#Run app
if __name__ == "__main__":
    #Set debug to True so errors will be displayed on the screen
    app.run(debug=True)