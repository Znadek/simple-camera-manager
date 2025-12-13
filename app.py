from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
from flask import Response
import uuid

from sqlalchemy import null

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
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

@app.route('/modify/<int:id>', methods=['GET', 'POST'])
def modify_object(id):
    obj = Object.query.get_or_404(id)
    if request.method == 'POST':
        obj.name = request.form['name']
        obj.description = request.form['description']
        obj.url = request.form['url']
        obj.username = request.form['username']
        obj.psw = request.form['psw']
        db.session.commit()
        flash('Object updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('modify.html', obj=obj)

def gen_camera_stream(rtsp_url, username, psw, small=False):
    address = f'rtsp://{username}:{psw}@{rtsp_url}'
    cap = cv2.VideoCapture(address)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot connect to {rtsp_url}")
    while True:
        success, frame = cap.read()
        if not success:
            break
        if small:
            frame = cv2.resize(frame, (320, 180))
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

@app.route('/preview/<int:id>')
def preview(id):
    obj = Object.query.get_or_404(id)
    if not obj.url:
        return "No URL configured", 404
    return Response(gen_camera_stream(obj.url, obj.username, obj.psw),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/preview-small/<int:id>')
def preview_small(id):
    obj = Object.query.get_or_404(id)
    if not obj.url:
        return "No URL configured", 404
    return Response(gen_camera_stream(obj.url, obj.username, obj.psw, small=True),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
