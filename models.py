from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    importance = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    @property
    def priority_score(self) -> float:
        days_left = (self.due_date - date.today()).days
        urgency_weight = 10.0 if days_left <= 0 else (10.0 / max(days_left, 1))
        return round(urgency_weight + (self.importance * 2), 2)

    @property
    def status_tag(self) -> str:
        days_left = (self.due_date - date.today()).days
        if self.completed:
            return "Completed"
        if days_left < 0:
            return "Overdue"
        if days_left <= 2:
            return "Urgent"
        return "On Track"