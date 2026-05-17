"""
MCP Server for Smart Task Manager.
Provides tools for Claude to interact with the task database via the Model Context Protocol.
"""

import os
from fastmcp import FastMCP
from flask import Flask
from datetime import datetime

from models import db, Task

# Flask app only for DB context
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

mcp = FastMCP("Smart-Task-Manager")


@mcp.tool()
def list_tasks():
    """
    List all tasks sorted by priority.
    
    Returns:
        list: A list of dictionaries containing task details (id, title, due_date, 
              importance, completed, priority_score, status).
    """

    with app.app_context():
        tasks = Task.query.all()

        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.priority_score,
            reverse=True
        )

        return [
            {
                "id": t.id,
                "title": t.title,
                "due_date": str(t.due_date),
                "importance": t.importance,
                "completed": t.completed,
                "priority_score": t.priority_score,
                "status": t.status_tag
            }
            for t in sorted_tasks
        ]


@mcp.tool()
def add_task(title: str, due_date: str, importance: int):
    """
    Add a new task to the database.
    
    Args:
        title (str): The title or description of the task.
        due_date (str): The due date of the task in 'YYYY-MM-DD' format.
        importance (int): The importance level of the task on a scale of 1 to 5.
        
    Returns:
        dict: A dictionary containing the success status and the new task_id.
    """

    with app.app_context():

        task = Task(
            title=title,
            due_date=datetime.strptime(
                due_date,
                "%Y-%m-%d"
            ).date(),
            importance=importance
        )

        db.session.add(task)
        db.session.commit()

        return {
            "success": True,
            "task_id": task.id
        }


@mcp.tool()
def complete_task(task_id: int):
    """
    Toggle the completion status of a specific task.
    
    Args:
        task_id (int): The unique identifier of the task to toggle.
        
    Returns:
        dict: A dictionary with the success status and new 'completed' boolean value,
              or an error message if the task is not found.
    """

    with app.app_context():

        task = Task.query.get(task_id)

        if not task:
            return {"error": "Task not found"}

        task.completed = not task.completed

        db.session.commit()

        return {
            "success": True,
            "completed": task.completed
        }


@mcp.tool()
def delete_task(task_id: int):
    """
    Delete a specific task from the database.
    
    Args:
        task_id (int): The unique identifier of the task to delete.
        
    Returns:
        dict: A dictionary containing the success status, or an error message if the task is not found.
    """

    with app.app_context():

        task = Task.query.get(task_id)

        if not task:
            return {"error": "Task not found"}

        db.session.delete(task)
        db.session.commit()

        return {"success": True}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    mcp.run()