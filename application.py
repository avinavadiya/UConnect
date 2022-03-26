from flask import Flask, jsonify, request
import pymongo

import time
import datetime

client = pymongo.MongoClient(
    "mongodb+srv://Krunal:yU7H2koJcMx4mhAU@cluster0.3gia0.mongodb.net/LibConnect?retryWrites=true&w=majority")

db = client["LibConnect"]

user_col = db["user"]

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():

    try:
        req = request.json
        user = user_col.find_one({"email": req["email"]}, {"_id": 0})
        if user:
            if user["password"] == req["password"]:
                return jsonify({
                    "message": "User logged in."
                }), 200

            else:
                return jsonify({
                    "message": "Invalid credentials"
                }), 401

        else:
            return jsonify({
                "message": "User not found."
            }), 404

    except Exception as e:
        jsonify({
            "message", str(e)
        }), 500


@app.route("/get_categories")
def get_categories():
    try:
        categories_col = db["categories"]

        categories = categories_col.find({}, {"_id": 0})

        op = []

        for c in categories:
            op.append(c)

        return jsonify(op), 200

    except Exception as e:
        jsonify({
            "message", str(e)
        }), 500


@app.route("/books/<category>/")
@app.route("/books/<category>/<isbn>")
def get_books(category: str, isbn: str = None):
    try:
        col = db[category]

        cursor = None
        if isbn is None:
            cursor = col.find({}, {"ISBN": 1, "name": 1, "_id": 0})

        else:
            cursor = col.find({"ISBN": isbn}, {"_id": 0})

        op = []

        for d in cursor:
            op.append(d)

        return jsonify(op), 200

    except Exception as e:
        jsonify({
            "message", str(e)
        }), 500


@app.route("/users/", methods=["POST"])
def get_users():
    try:

        req = request.json

        cursor = user_col.find({"email": req["email"]}, {
                               "_id": 0, "password": 0})

        op = []

        for d in cursor:
            op.append(d)

        return jsonify(op), 200

    except Exception as e:
        jsonify({
            "message", str(e)
        }), 500


@app.route("/user/issuebook", methods=["POST"])
def issuebook():
    try:
        req = request.json

        user = user_col.find_one({"email": req["email"]}, {
                                 "_id": 0, "password": 0})

        category = db[req["category"]]

        book = category.find_one({"ISBN": req["ISBN"]}, {"_id": 0})

        for b in book["books"]:
            if b["book_id"] == req["book_id"]:
                if b["is_available"] is False:
                    return jsonify({
                        "message": "Book unavailable."
                    }), 400

                else:
                    if len(user["issued_books"]) == 5:
                        return jsonify({
                            "message": "Issue book limit reached."
                        }), 406

                    book["available_books"] = book["available_books"] - 1
                    b["is_available"] = False

                    b["issue_date"] = datetime.datetime.utcnow()
                    b["return_date"] = datetime.datetime.utcnow() + \
                        datetime.timedelta(days=15)

                    category.update_one({"ISBN": req["ISBN"]}, {"$set": book})

                    user["issued_books"].append({
                        "ib_id": b["book_id"],
                        "name": book["name"],
                        "category": req["category"],
                        "ISBN": book["ISBN"],
                        "issue_date": b["issue_date"],
                        "return_date": b["return_date"]
                    })

                    user_col.update_one({"email": req["email"]}, {"$set": {
                        "issued_books": user["issued_books"]
                    }})

                    return jsonify({
                        "message": "Book issued"
                    }), 200

        return jsonify({
            "message": "Nothing changed"
        }), 202

    except Exception as e:
        jsonify({
            "message": str(e)
        }), 500




@app.route("/get_institutes")
def get_institutes():
    try:
        institutes_col = db["Institutes"]

        institutes = institutes_col.find({}, {"_id": 0})

        op = []

        for c in institutes:
            op.append(c)

        return jsonify(op), 200

    except Exception as e:
        jsonify({
            "message", str(e)
        }), 500



@app.route("/get_institute/<department>/")
def get_institute(department: str):
    try:
        col = db[department]

        institutes = col.find({}, {"_id": 0})

        op = []

        for c in institutes:
            op.append(c)

        return jsonify(op), 200


    except Exception as e:
        jsonify({
            "message", str(e)
        }), 500


if __name__ == "__main__":
    app.run()
