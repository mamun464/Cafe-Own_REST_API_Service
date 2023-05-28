from flask import Flask, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random",methods=['GET'])
def random_cafes():
    all_cafe=db.session.query(Cafe).all()

    random_cafe=random.choice(all_cafe)

    api_data =jsonify( cafe=random_cafe.to_dict())

    # api_data= jsonify(
    #
    #     cafe ={
    #
    #         "name": random_cafe.name,
    #         "map_url": random_cafe.map_url,
    #         "img_url": random_cafe.img_url,
    #         "location": random_cafe.location,
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #         "id": random_cafe.id,
    # }
    # )

    return api_data

@app.route("/all")
def all():
    all_cafes= db.session.query(Cafe).all()
    cafe_list=[]
    for single_cafe in all_cafes:
        temp=single_cafe.to_dict()
        cafe_list.append(temp)

    return jsonify( cafe=cafe_list)

@app.route("/search")
def search():
    loc=request.args.get("loc")
    cafe=db.session.query(Cafe).filter_by(location=loc).all()

    cafe_json=jsonify(cafe=[item.to_dict() for item in cafe])

    if not cafe:

        cafe_json= jsonify(

            error= {
                "Not Found" : "Sorry, we don't have cafe at that location."
            }
        )
    return cafe_json

@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<cafe_id>",methods=["PATCH"])
def Patch(cafe_id):
    update_price=request.args.get("new_price")
    print(update_price)
    print(type(print(update_price)))
    cafe_to_update=Cafe.query.get(cafe_id)

    if cafe_to_update:
        cafe_to_update.coffee_price=update_price
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."}),200
    else:
        return jsonify(error= {"Not Found" : "Sorry, we don't have cafe at that location."}),404



@app.route("/report-closed/<cafe_id>",methods=["DELETE"])
def delete(cafe_id):
    cafe_to_delete=db.session.query(Cafe).get(cafe_id)
    api_key ="TopSecretAPIKey"
    given_api_key=request.args.get('api-key')
    if api_key == given_api_key:
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully Deleted the cafe."}),200
        else:
            return jsonify(error= {"Not Found" : "Sorry, a cafe with that id not in the database."}),404
    else:
        return jsonify(error={"Forbidden": "Sorry, That's not allowed. Make sure you have currect api_key"}), 403

    

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
