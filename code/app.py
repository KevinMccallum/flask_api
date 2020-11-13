from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

USER_DATA = {
    "admin": "hola"
}


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://rsjpdwpovqvffk:f03eab6898fd67e601adbc7aa14cb97413d71961cb8eace50c36521baa33c6cc@ec2-3-220-222-72.compute-1.amazonaws.com:5432/d65apm2nb3g4vq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Person(db.Model):
    __tablename__ = "personas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    fecha_nacimiento = db.Column(db.String(255))
    puesto = db.Column(db.String(255))

    def __init__(self, name, fecha_nacimiento, puesto):
        self.name = name
        self.fecha_nacimiento = fecha_nacimiento
        self.puesto = puesto

    def __repr__(self):
        return '%s/%s/%s/%s' % (self.id, self.name, self.fecha_nacimiento, self.puesto)


class Item(Resource):
    @auth.login_required
    def get(self, id):
        data = Person.query.get(id)
        print(data)
        dataDict = {
            'id': str(data).split('/')[0],
            'name': str(data).split('/')[1],
            'fecha_nacimiento': str(data).split('/')[2],
            'puesto': str(data).split('/')[3]
        }
        return jsonify(dataDict)

    @auth.login_required
    def delete(self, id):
        delData = Person.query.filter_by(id=id).first()
        db.session.delete(delData)
        db.session.commit()
        return jsonify({'status': 'Data '+id+' is deleted from PostgreSQL!'})

    @auth.login_required
    def put(self, id):
        body = request.json
        newName = body['name']
        newDate = body['fecha_nacimiento']
        newPos = body['puesto']
        editData = Person.query.filter_by(id=id).first()
        editData.name = newName
        editData.fecha_nacimiento = newDate
        editData.puesto = newPos
        db.session.commit()
        return jsonify({'status': 'Data '+id+' is updated from PostgreSQL!'})


class ItemList(Resource):

    @auth.login_required
    def get(self):
        data = Person.query.order_by(Person.id).all()
        dataJson = []
        for i in range(len(data)):
            dataDict = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
                'fecha_nacimiento': str(data[i]).split('/')[2],
                'puesto': str(data[i]).split('/')[3]
            }
            dataJson.append(dataDict)
        return jsonify(dataJson)

    @auth.login_required
    def post(self):
        body = request.json
        name = body['name']
        fecha_nacimiento = body['fecha_nacimiento']
        puesto = body["puesto"]

        data = Person(name, fecha_nacimiento, puesto)
        db.session.add(data)
        db.session.commit()

        return jsonify({
            'status': 'Data is posted to PostgreSQL!',
            'name': name,
            'fecha_nacimiento': fecha_nacimiento,
            'puesto': puesto
        })


api.add_resource(Item, '/data/<string:id>')
api.add_resource(ItemList, '/data')

app.run(port=5000, debug=True)
