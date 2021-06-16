from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests,os
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
TMDB_API_KEY='5750fd54e24e12a7c2585df82a8dfdf9'
URL='https://api.themoviedb.org/3/search/movie'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-lists.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)
db.create_all()

class RateMovieForm(FlaskForm):
    rating = StringField('Your rating out of 10', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Done')

@app.route("/")
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=["GET","POST"])
def edit():
    rating_form = RateMovieForm()
    movie_id = request.args.get('id')
    update_movie = Movie.query.filter_by(id=movie_id).first()
    if rating_form.validate_on_submit():
        update_movie.rating = rating_form.rating.data
        update_movie.review = rating_form.review.data
        db.session.commit()
        return redirect('/')
    return render_template('edit.html',movie=update_movie,form=rating_form)

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect('/')

@app.route('/add',methods=["GET","POST"])
def add():
    add_movie_form = AddMovie()

    if add_movie_form.validate_on_submit():
        search_movie = add_movie_form.title.data
        parameters = {
            'api_key': TMDB_API_KEY,
            'query': search_movie

        }
        response = requests.get(URL,params=parameters)
        response.raise_for_status()
        movie_data = response.json()['results']
        return render_template('select.html',movies=movie_data)
    return render_template('add.html',form=add_movie_form)

@app.route('/get')
def get():
    movie_id = request.args.get('id')
    find_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    parameters = {
        'api_key' : TMDB_API_KEY,
    }
    response = requests.get(find_url,params=parameters)
    response.raise_for_status()
    movie_data = response.json()
    movie_title = movie_data['original_title']
    movie_poster = f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}"
    movie_year = movie_data['release_date'].split("-")[0]
    movie_overview = movie_data['overview']
    new_movie = Movie(title=movie_title,year=movie_year,description=movie_overview,img_url=movie_poster)
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit',id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
