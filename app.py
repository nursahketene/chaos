import requests, json
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization = db.Column(db.String(1000), nullable=False)
    profession = db.Column(db.String(1000), nullable=False)
    job_description = db.Column(db.String(1000), nullable=False)


    def __repr__(self):
        return '<Job %r>' % self.id

pp = pprint.PrettyPrinter(indent=4)

@app.route('/')
def index():
    # Lets check if there are any jobs in the database
    # If not fetch some data from the API endpoint!
    organization = db.session.query(func.count(Job.organization).label('organization_count'), Job.organization).group_by(Job.organization).all()
    professions = db.session.query(func.count(Job.profession).label('profession_count'), Job.profession).group_by(Job.profession).all()

    if len(organization) < 1:
        # There are no jobs
        # Get jobs
        print('*********** Populating db for the first time!')
        results = requests.get('http://gis.vantaa.fi/rest/tyopaikat/v1/Opetusala').json()
        for job in results:
            new_job = Job(
                organization=job['organisaatio'],
                profession=job['ammattiala'],
                job_description=job['tyotehtava']
            )
            try:
                db.session.add(new_job)
                db.session.commit()
            except:
                print('There was an error with one of the tasks:', new_job)
        organization = db.session.query(func.count(Job.organization).label('organization_count'), Job.organization).group_by(Job.organization).all()
        professions = db.session.query(func.count(Job.profession).label('profession_count'), Job.profession).group_by(Job.profession).all()
    # Now we need to fetch data from the dabase
    # # Lets group them by organization
    data = {'organization': organization, 'professions': professions}
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)