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


import sqlite3
import datetime


def _build_entreprise(result_set_item):
    entreprise = {}
    entreprise["id"] = result_set_item[0]
    entreprise["nom"] = result_set_item[1]
    return entreprise

def _build_interaction(result_set_item):
    interaction = {}
    interaction["id"] = result_set_item[0]
    interaction["moment"] = result_set_item[1]
    interaction["description"] = result_set_item[2]
    return interaction

def _build_rappel(result_set_item):
    rappel = {}
    rappel["id"] = result_set_item[0]
    rappel["activation"] = result_set_item[1]
    rappel["note"] = result_set_item[2]
    return rappel

def _build_rappel_todo(result_set_item):
    rappel = {}
    rappel["id"] = result_set_item[0]
    rappel["activation"] = result_set_item[1]
    rappel["note"] = result_set_item[2]
    rappel["entreprise_id"] = result_set_item[3]
    rappel["entreprise_nom"] = result_set_item[4]
    return rappel

def _build_resume_quotidien(result_set_item):
    interaction = {}
    interaction["description"] = result_set_item[0]
    interaction["entreprise_nom"] = result_set_item[1]
    return interaction



class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/minimal.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_entreprises(self):
        cursor = self.get_connection().cursor()
        query = ("select id, nom from entreprise")
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_entreprise(item) for item in all_data]

    def get_entreprise(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = ("select id, nom from entreprise where id = ?")
        cursor.execute(query, (entreprise_id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_entreprise(item)

    def add_entreprise(self, nom):
        connection = self.get_connection()
        query = ("insert into entreprise(nom) values(?)")
        connection.execute(query, (nom,))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId

    def get_interactions(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = ("select id, moment, description from interaction where entreprise_id = ?")
        cursor.execute(query, (entreprise_id,))
        all_data = cursor.fetchall()
        return [_build_interaction(item) for item in all_data]

    def add_interaction(self, moment, description, entreprise_id):
        connection = self.get_connection()
        query = ("insert into interaction(moment, description, entreprise_id) values(?,?,?)")
        connection.execute(query, (moment, description, entreprise_id,))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId
    
    def add_rappel(self, activation, note, entreprise_id):
        connection = self.get_connection()
        query = ("insert into rappel(done, activation, note, entreprise_id) values(0,?,?,?)")
        connection.execute(query, (activation, note, entreprise_id,))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId
    
    def delete_rappel(self, rappel_id):
        connection = self.get_connection()
        query = ("delete from rappel where id = ?")
        connection.execute(query, (rappel_id,))
        connection.commit()
    
    def get_rappels_non_termines(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = ("select id, activation, note from rappel where entreprise_id = ? and done = 0")
        cursor.execute(query, (entreprise_id,))
        all_data = cursor.fetchall()
        return [_build_rappel(item) for item in all_data]

    def get_rappels_todo(self):
        cursor = self.get_connection().cursor()
        query = ("select rappel.id, rappel.activation, rappel.note, entreprise.id, entreprise.nom from rappel inner join entreprise on (entreprise.id = rappel.entreprise_id) where rappel.done = 0 and rappel.activation <= ?")
        cursor.execute(query, (datetime.date.today(),))
        all_data = cursor.fetchall()
        return [_build_rappel_todo(item) for item in all_data]

    def get_resume_quotidien(self, date):
        cursor = self.get_connection().cursor()
        query = ("select interaction.description, entreprise.nom from interaction inner join entreprise on (interaction.entreprise_id = entreprise.id) where interaction.moment = ?")
        cursor.execute(query, (date,))
        all_data = cursor.fetchall()
        return [_build_resume_quotidien(item) for item in all_data]
