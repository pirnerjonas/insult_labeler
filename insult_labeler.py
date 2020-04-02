from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = '58f2cae6bd981e8433d756d6ec34c1cd'
# here all 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insults.db' # three slash relative path
app.config['SQLALCHEMY_BINDS'] = {'label' : 'sqlite:///label.db'}
db = SQLAlchemy(app)

class Insult(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.Integer)
    Comment = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Insult %r>' % self.id

class Insult_labeled(db.Model):
    __bind_key__ = 'label'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    label = db.Column(db.Integer)

    def __repr__(self):
        return '<Insult_labeled %r>' % self.id

@app.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
        insult_content = request.form['content']
        new_insult = Insult(Comment=insult_content)

        try:
            db.session.add(new_insult)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue'

    else:
        # load all insults
        insults = Insult.query.order_by(Insult.Date).all()
        return render_template('index.html', insults=insults)

@app.route('/label', methods=['POST','GET'])
def label():
    # progress bar
    count_remaining = len(Insult.query.all())
    count_labeled = len(Insult_labeled.query.all())
    percentage = int(count_labeled / (count_labeled+count_remaining))

    # statistics
    count_toxic = len(Insult_labeled.query.filter_by(label=1).all())
    count_normal = len(Insult_labeled.query.filter_by(label=0).all())
    try:
        perTox = np.round(count_toxic/(count_toxic+count_normal)*100,2)
        perNor = np.round(count_normal/(count_toxic+count_normal)*100,2)
    except:
        perTox = 0
        perNor = 0
    total = perTox + perNor

    # if e.g. button is pressed
    if request.method == 'POST':
        try:
            insult = Insult.query.first_or_404()
            if request.form['action'] == 'Toxic':
                label = Insult_labeled(content=insult.Comment, label=1)
            elif request.form['action'] == 'Normal':
                label = Insult_labeled(content=insult.Comment, label=0)
            # create entry in label db
            db.session.add(label)
            # delete entry in insult db
            db.session.delete(insult)
            db.session.commit()
            return redirect('/label')
        except:
            flash(f'All data is labeled', 'message')
            return redirect('/results')
    # first initialization
    else:
        insult = Insult.query.first_or_404()
        return render_template('label.html', insult=insult, percentage=percentage, perTox=perTox, perNor=perNor, total=total)

@app.route('/results')
def results():
    label_data = Insult_labeled.query.order_by(Insult_labeled.id.desc()).all()[:5]
    return render_template('results.html', label_data=label_data)

@app.route('/change/<int:id>', methods=['POST','GET'])
def change(id):
    label_to_change = Insult_labeled.query.get_or_404(id)
    if request.method == 'POST':

        if request.form['action'] == 'Toxic':
                label_to_change.label = 1
        elif request.form['action'] == 'Normal':
                label_to_change.label = 0

      
        db.session.commit()
        return redirect('/results')
    else:
        return render_template('change.html', label_to_change=label_to_change)

if __name__ == '__main__':
    app.run(debug=True)
