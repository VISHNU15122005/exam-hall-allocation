import click
from app import create_app
from app.extensions import db
from app.models import Admin

app = create_app()


@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """Create an admin login. Usage: flask --app run.py create-admin admin admin123"""
    with app.app_context():
        if Admin.query.filter_by(username=username).first():
            print(f"Admin '{username}' already exists.")
            return
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin '{username}' created.")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
