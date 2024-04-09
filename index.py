# Copyright 2024 Jacques Berger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from flask import Flask
from flask import abort
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from .database import Database

app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.route('/')
def landing_page():
    return redirect('/entreprises')


@app.route('/entreprises')
def entreprises_liste():
    all_entreprises = get_db().get_entreprises()
    all_entreprises.sort(key=sort_entreprises)
    return render_template('entreprises.html', entreprises=all_entreprises)


@app.route('/nouvelle-entreprise', methods=["GET", "POST"])
def entreprise_add():
    if request.method == "GET":
        return render_template('entreprise-edit.html')
    else:
        validation_result = validate_entreprise(request.form)
        if validation_result["is_valid"]:
            get_db().add_entreprise(request.form["nom"])
            return redirect('/entreprises')
        else:
            return render_template('entreprise-edit.html', result=validation_result)


@app.route('/entreprise/<id>')
def entreprise_display(id):
    entreprise = get_db().get_entreprise(id)
    if entreprise is None:
        abort(404)
    else:
        return render_template('entreprise-display.html', entreprise=entreprise)


@app.route('/entreprise/<entreprise_id>/nouvelle-interaction', methods=["GET", "POST"])
def interaction_add(entreprise_id):
    entreprise = get_db().get_entreprise(entreprise_id)
    if entreprise is None:
        abort(404)
    else:
        if request.method == "GET":
            return render_template('interaction-edit.html', entreprise=entreprise)
        else:
            validation_result = validate_interaction(request.form, entreprise["id"])
            if validation_result["is_valid"]:
                get_db().add_interaction(datetime.date.fromisoformat(request.form["moment"]), request.form["description"], entreprise["id"])
                return redirect('/entreprise/' + str(entreprise["id"]))
            else:
                return render_template('interaction-edit.html', entreprise=entreprise, result=validation_result)


def sort_entreprises(properties):
    return properties["nom"]


def validate_entreprise(entreprise):
    result = {}
    result["is_valid"] = True
    result["global_errors"] = []
    
    if "nom" not in entreprise or len(entreprise["nom"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("Le nom d'entreprise est obligatoire.")

    return result


def validate_interaction(interaction, entreprise_id):
    result = {}
    result["is_valid"] = True
    result["global_errors"] = []

    print(interaction["moment"])
    if "moment" not in interaction or len(interaction["moment"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("La date de l'interaction est obligatoire.")
    elif not validate_isodate_format(interaction["moment"]):
        result["is_valid"] = False
        result["global_errors"].append("Le format de la date de l'interaction est incorrect.")

    if "description" not in interaction or len(interaction["description"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("La description de l'interaction est obligatoire.")

    if "entreprise_id" not in interaction or interaction["entreprise_id"] != str(entreprise_id):
        result["is_valid"] = False
        result["global_errors"].append("Le lien avec l'entreprise a été compromis. Veuillez recharger la page et recommencer.")

    return result


def validate_isodate_format(string):
    try:
        datetime.date.fromisoformat(string)
        return True
    except:
        return False
