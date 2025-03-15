
from market import app, db, bcrypt
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime


#@app.route('/')
# def hello_world():
#    return '<h1>Home Page</h1>'

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')
    #  we went on to call the home.html file as can be seen above.
    # 'render_template()' basically works by rendering files.

@app.route('/about/')
def about_us():
    return ' <h1>About Us</h1> '


@app.route('/about/<username>')
def about_page(username):
    return f'<h1>More About Us {username} </h1>'


@app.route('/market', methods=['GET', 'POST'])
@login_required
#below list of dictionaries is sent to the market page through the market.html
#       but we are going to look for a way to store information inside an organized
#       DATABASE which can be achieved through configuring a few things in our flask
#       application
# WE ARE THUS GOING TO USE SQLITE3 is a File WHich allows us to store information and we are going to
#   connect it to the Flask APplication.We thus have to install some flask TOOL THAT ENABLES THIS through the terminal
def market_page():
    purchase_form = PurchaseItemForm()
    if request.method == "POST":
        #Purchase item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
                
        #Sell item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')

        return redirect(url_for('market_page'))
    
    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items)

    items = Item.query.all()
    #items = [
    #    {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
    #    {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
    #    {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
    #]
    return render_template('market.html', items=items, purchase_form=purchase_form)




@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                            email_address=form.email_address.data,
                            password_hash=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            #print(f'There was an error with creating a user: {err_msg}')
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
            
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

#added this code for the search bar at the navbar in 'base.html'
@app.route('/search')
def search_results():
    query = request.args.get('query')
    # Implement search logic here (e.g., search database for results)
    #return f"Results for: {query}"
    results = []

    if query:
        # Search MongoDB collection (case-insensitive regex search)
        results = collection.find({"name": {"$regex": query, "$options": "i"}})

        # Convert results to a list
        results = [doc for doc in results]



@app.route('/livestock_dashboard')
def livestock_dashboard():
    return render_template('livestock_dashboard.html')


@app.route('/livestock_dashboard/age', methods=['GET', 'POST'])
def age_calculator():
    age_result = None
    next_birthday = None

    if request.method == 'POST':
        dob_str = request.form.get("dob")
        calc_date_str = request.form.get("calc_date")
        format_choice = request.form.get("format_choice")
        
        if dob_str and calc_date_str:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            calc_date = datetime.strptime(calc_date_str, "%Y-%m-%d")
            delta = calc_date - dob
            

            #Format the output based on user selection
            if format_choice == "days":
                age_result = f"{delta.days} day(s)"
            elif format_choice == "weeks":
                age_result = f"{delta.days // 7 } week(s)"
            elif format_choice == "months":
                age_result = f"{delta.days // 30} month(s)"
            elif format_choice == "years":
                age_result = f"{delta.days // 365} year(s)"
            else:
                years = delta.days // 365
                months = (delta.days % 365) // 30
                days = (delta.days % 365) % 30
                result = f"{years} years, {months} months, {days} days"

    return render_template('livestock_dashboard.html', result=result)
#added this one again



@app.route('/animals')
def view_animals():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Animals')
    animals = cursor.fetchall()
    return render_template('animals.html', animals=animals)