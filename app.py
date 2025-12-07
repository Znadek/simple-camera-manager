from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///objects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(200), nullable=True)
    username = db.Column(db.String(100), nullable=True)
    psw = db.Column(db.String(100), nullable=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

@app.route('/', methods=['GET'])
def index():
    objects = Object.query.all()
    return render_template('index.html', objects=objects)

@app.route('/add', methods=['POST'])
def add_object():
    name = request.form['name']
    description = request.form['description']
    url = request.form.get('url')
    username = request.form.get('username')
    psw = request.form.get('psw')
    new_obj = Object(name=name, description=description, url=url, username=username, psw=psw)
    db.session.add(new_obj)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_object(id):
    obj = Object.query.get_or_404(id)
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for('index'))

