from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from config import *



app = Flask(__name__)
app.config['SECRET_KEY'] = token
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-10-movies.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(300), unique=True, nullable=False)


# new_movie = Movies(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.create_all()
# db.session.add(new_movie)
# db.session.commit()
all_movies = []
api_key = movie_key

class EditForm(FlaskForm):
    rating = StringField("Your rating out of 10", render_kw={'autofocus': True})
    review = StringField("Your Review")
    submit = SubmitField("Done")

class AddMovies(FlaskForm):
    title = StringField("Movie Title", render_kw={'autofocus': True}, validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    all_movies = db.session.query(Movies).all()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    edit_form = EditForm()
    movie_id = request.args.get('id')
    movie_selected = Movies.query.get(movie_id)
    print(movie_id, flush=True)
    
    edit_form.validate_on_submit()

    if edit_form.validate_on_submit():
        
        movie_selected.rating = float(edit_form.rating.data)
        movie_selected.review = edit_form.review.data

        db.session.commit()
        return redirect(url_for('home'))

    
    movie_selected = Movies.query.get(movie_id)
    
    return render_template("edit.html", form=edit_form, movie=movie_selected)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    add_form = AddMovies()
    add_form.validate_on_submit()

    if add_form.validate_on_submit():
        movie_title = add_form.title.data
        print(movie_title, flush=True)
        
        movie_api_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}'


        res = requests.get(movie_api_url)
        res.raise_for_status()
        data = res.json()
        return render_template('select.html', movie_data=data)

    return render_template('add.html', form=add_form)
    
@app.route("/find")
def get_movie():
    
    user_choice_id = request.args.get("id")
    get_movie_details = f'https://api.themoviedb.org/3/movie/{user_choice_id}?api_key={api_key}&language=en-US'
    if user_choice_id:
        res = requests.get(get_movie_details)
        res.raise_for_status()
        movie_details_data = res.json()

        new_movie = Movies(
                title=movie_details_data["original_title"],
                year=movie_details_data["release_date"].split("-")[0],
                description=movie_details_data["overview"],
                rating=movie_details_data["vote_average"],
                ranking=int(movie_details_data["popularity"]),
                review="My favourite character was the caller.",
                img_url=f'https://image.tmdb.org/t/p/w500{movie_details_data["poster_path"]}'
                     )

        
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    
        

if __name__ == '__main__':
    app.run(debug=True)
