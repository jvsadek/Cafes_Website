from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired, URL
import csv
import  os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FLASK_KEY'
# app.config['SECRET_KEY']=  os.environ.get('FLASK_KEY')
Bootstrap5(app)


# CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///cafes.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'

db = SQLAlchemy()
db.init_app(app)


class Cafe(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    cafe = db.Column(db.String(250), unique=True, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    open = db.Column(db.String(250), nullable=False)
    close = db.Column(db.String(250), nullable=False)
    coffee_rating = db.Column(db.Text, nullable=False)
    wifi_rating = db.Column(db.Text, nullable=False)
    power_rating = db.Column(db.Text, nullable=False)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
    open = StringField("Opening Time e.g. 8AM", validators=[DataRequired()])
    close = StringField("Closing Time e.g. 5:30PM", validators=[DataRequired()])
    coffee_rating = SelectField("Coffee Rating", choices=["☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"], validators=[DataRequired()])
    wifi_rating = SelectField("Wifi Strength Rating", choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"], validators=[DataRequired()])
    power_rating = SelectField("Power Socket Availability", choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"], validators=[DataRequired()])
    submit = SubmitField('Submit')

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():

        result = db.session.execute(db.select(Cafe).where(Cafe.location == form.location.data))
        cafe_result = result.scalar()

        if cafe_result  :
            # User already exists
            flash("You've already added this cafe before, add a new one instead!")
            return redirect(url_for('add_cafe'))

        new_cafe = Cafe(
            cafe=form.cafe.data,
            location=form.location.data,
            open=form.open.data,
            close=form.close.data,
            coffee_rating=form.coffee_rating.data,
            wifi_rating=form.wifi_rating.data,
            power_rating=form.power_rating.data,
        )
        db.session.add(new_cafe)
        db.session.commit()

        # with open("cafe-data.csv", mode="a") as csv_file:
        #     csv_file.write(f"\n{form.cafe.data},"
        #                    f"{form.location.data},"
        #                    f"{form.open.data},"
        #                    f"{form.close.data},"
        #                    f"{form.coffee_rating.data},"
        #                    f"{form.wifi_rating.data},"
        #                    f"{form.power_rating.data}")
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    # with open('cafe-data.csv', newline='') as csv_file:
    #     csv_data = csv.reader(csv_file, delimiter=',')
    #     list_of_rows = []
    #     for row in csv_data:
    #         list_of_rows.append(row)

    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    # print(cafe_result)
    return render_template('cafes.html', all_cafes=cafes)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
