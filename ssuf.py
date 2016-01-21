#!/usr/bin/python

from flask import Flask,request,jsonify,Response,abort
from flask_sqlalchemy import SQLAlchemy
import magic
import base64
import string
import random
import os



app=Flask(__name__)
app.debug=True
app.config['APIKEY']='ldijf293'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Model

class File(db.Model):
    __tablename__='files'
    id=db.Column(db.Integer,primary_key=True)
    uid=db.Column(db.String(255),unique=True)
    path=db.Column(db.String(255),unique=True)
    def as_dict(self):
        rd=dict()
        [rd.__setitem__(k,self.__dict__[k]) for k in self.__dict__.keys() if not k.startswith('_')]
        return rd

# other functions

def check_access(json):
    if not json or not json.get('apikey'): abort(400)
    if json.get('apikey')!=app.config['APIKEY']: abort(403)
# routes

@app.route('/')
def index():
    return 'wat'

@app.route('/<uid>')
def get_file_content(uid):
    path=File.query.filter_by(uid=uid).first_or_404().path
    m = magic.open(magic.MAGIC_MIME)
    m.load()
    mime=m.file(path)
    file=open(path,'rb')
    content=file.read()
    file.close()
    return Response(content,content_type=mime)


@app.route('/api/files',methods=['PUT'])
def get_files():
    check_access(request.get_json())
    return jsonify({"files":[f.as_dict() for f in File.query.all()]})

@app.route('/api/files',methods=['POST'])
def new_file():
    data=request.get_json()
    check_access(data)
    if not data.get('content') or not data.get('filename'): abort(400)
    new_file=File()
    new_file.uid=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
    new_file.path=data.get('filename')
    db.session.add(new_file)
    db.session.commit()
    f=open(new_file.path,'wb')
    f.write(base64.b64decode(data.get('content')))
    f.close()
    return jsonify(new_file.as_dict())

@app.route('/api/files/<int:id>',methods=['PUT'])
def get_file(id):
    check_access(request.get_json())
    return jsonify(File.query.filter_by(id=id).first_or_404().as_dict())

@app.route('/api/files/<int:id>',methods=['DELETE'])
def delete_file(id):
    check_access(request.get_json())
    del_file=File.query.filter_by(id=id).first_or_404()
    os.remove(del_file.path)
    db.session.delete(del_file)
    db.session.commit()
    return jsonify({"result":"deleted"})
# main
if __name__=='__main__':
    app.run()
