from flask import Flask, render_template

#Create a flask instance
#__name__ helps flask find files in the directory
app = Flask(__name__)

#Create a route so that the website (specifically the home page) can be accessed (via URL) 
@app.route('/')
#Create function to define the home page
# def index():
#     return "<h1>Hello World!</h1>"

def index():
    #Porgram will go to the template folder and find the right file to display
    return render_template("index.html")

#<> allows us to pass a name
@app.route('/user/<name>')
def user(name):
    #Display given name at the top of the page
    return "<h1>Hello {}</h1>".format(name)

#Run app
if __name__ == "__main__":
    #Set debug to True so errors will be displayed on the screen
    app.run(debug=True)