from app import app,db
from flask import render_template

@app.errorhandler(404)
def no_data_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def unexpected_error(error):
    db.session.rollback()
    return render_template('500.html'), 500