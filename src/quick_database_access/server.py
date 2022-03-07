from flask import Flask, render_template, request, url_for, flash, redirect
import sqlalchemy
from sqlalchemy import create_engine, inspect

app = Flask(__name__)


def get_db_connection():
    engine = create_engine('mysql://ahdoebm1:20220303@SRV018.img.med.uni-tuebingen.de/bioinf_heredivar_ahdoebm1')
    return engine



@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


if __name__ == '__main__':
    con = get_db_connection()
    inspector = inspect(con)
    print(inspector.get_columns('variant'))
    #app.run(debug=True)
