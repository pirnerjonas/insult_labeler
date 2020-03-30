from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '58f2cae6bd981e8433d756d6ec34c1cd'
# here all 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db' # three slash relative path
app.config['SQLALCHEMY_BINDS'] = {'label' : 'sqlite:///label.db'}
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

class Label(db.Model):
    __bind_key__ = 'label'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    label = db.Column(db.Integer)

    def __repr__(self):
        return '<Label %r>' % self.id

@app.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue'

    else:
        # load all tasks
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')

    except:
        'error deleting'

@app.route('/label', methods=['POST','GET'])
def label():
    if request.method == 'POST':
        # load first task in db 
        try:
            task = Todo.query.order_by(Todo.date_created).first_or_404()
            if request.form['action'] == 'Toxic':
                label = Label(content=task.content, label=1)
            elif request.form['action'] == 'Normal':
                label = Label(content=task.content, label=0)
            # create entry in label db
            db.session.add(label)
            # delete entry in task db
            db.session.delete(task)
            db.session.commit()
            return redirect('/label')
        except:
            flash(f'All data is labeled', 'message')
            return redirect('/results')
    else:
        task = Todo.query.order_by(Todo.date_created).first()
        return render_template('label.html', task=task)

@app.route('/results')
def results():
    label_data = Label.query.all()
    return render_template('results.html', label_data=label_data)

@app.route('/change/<int:id>', methods=['POST','GET'])
def change(id):
    label_to_change = Label.query.get_or_404(id)
    if request.method == 'POST':
        label_to_change.label = request.form['label']
        db.session.commit()
        return redirect('/results')
    else:
        return render_template('change.html', label_to_change=label_to_change)


'''    max_id = db.session.query(func.max(Todo.id)).scalar()
    with counter.get_lock():
        counter.value += 1
        out = counter.value
    if request.method == 'POST':
        if out <= max_id:
            if request.form['action'] == 'Toxic':
                task = Todo.query.filter_by(id=out).first()
                return render_template('label.html', task=task)

            elif request.form['action'] == 'Normal':
                task = Todo.query.filter_by(id=out).first()
                return render_template('label.html', task=task)
        else:
            # all entries were labeled
            counter.value = 0
            return redirect('/')
    else:
        task = Todo.query.order_by(Todo.date_created).first()
        return render_template('label.html', task=task)'''

if __name__ == '__main__':
    app.run(debug=True)
