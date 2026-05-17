import logging
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date

from models import db, Task

for logger_name in ["fastmcp", "mcp", "werkzeug"]:
    logger = logging.getLogger(logger_name)
    logger.propagate = True
    logger.handlers = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    instance_path=os.path.join(BASE_DIR, "instance")
)

os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"sqlite:///{os.path.join(app.instance_path, 'tasks.db')}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/')
def index():
    all_tasks = Task.query.all()
    sorted_tasks = sorted(
        all_tasks,
        key=lambda t: t.priority_score,
        reverse=True
    )
    return render_template(
        'index.html',
        tasks=sorted_tasks,
        today=date.today()
    )


@app.route('/add', methods=['POST'])
def add_task():
    due_date_str = request.form.get('due_date')

    new_task = Task(
        title=request.form.get('title'),
        due_date=datetime.strptime(
            due_date_str,
            '%Y-%m-%d'
        ).date(),
        importance=int(request.form.get('importance'))
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed = not task.completed

    db.session.commit()

    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=False, use_reloader=False)