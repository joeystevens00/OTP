from . import otp
import json
import secrets
from .otp import letters, numbers, symbols, ascii_chars, securegen
import os
import codecs
VERSION = 0.10

class ReferenceDBList:
    def __init__(self, directory=None, files=None, dbs=None):
        if directory:
            files = [  '{}/{}'.format(directory, f) for f in os.listdir(directory) ]
        if not files:
            raise ValueError('files or directory required')
        if dbs:
            self.list = dbs
        else:
            self.list = []
            for file in files:
                self.list.append(ReferenceDB.load(file))
        self.file_by_slug = {}
        for db in self.list:
            slug = db.slug
            self.file_by_slug[slug] = db.file
    def __len__(self):
        return len(self.list)
    def random_db(self):
        return secrets.choice(self.list)
    def db_from_slug(self, slug):
        return ReferenceDB.load(self.file_by_slug.get(slug))
    def get_key(self, filekeyslug):
        """
        Fetches key by {file}-{refkey}
        file == ReferenceDB file name before .json
        refkey == Reference Key in db
        """
        pass
    @classmethod
    def generate(cls, files=10, **kwargs):
        dbs = []
        file_paths = []
        if kwargs.get('directory'):
            if not os.path.exists(kwargs.get('directory')):
                os.makedirs(kwargs.get('directory'))
        for i in range(files):
            db = ReferenceDB.generate(**kwargs)
            dbs.append(db)
            file_paths.append(db.file)
        return cls(files=file_paths, dbs=dbs)

class ReferenceDB:
    def __init__(self, file, items):
        self.file = file
        self.items = items
        self.slug = file.split('/')[-1].split('\\')[-1].split('.')[0]
    def get(self, key):
        return self.items.get(key)
    def pop(self, key):
        return self.items.pop(key)
    def pop_random_key(self):
        return self.pop(self.random_key[0])
    def random_key(self):
        reference_key = secrets.choice(list(self.items.keys()))
        key = self.items.get(reference_key)
        return reference_key, key
    @classmethod
    def new_reference_key(cls, length=4):
        return securegen(length, charset=numbers+letters)
    def save(self):
        with codecs.open(self.file, 'w', 'utf-16', 'surrogatepass') as outfile:
            json.dump(self.items, outfile, ensure_ascii=False)
    @classmethod
    def load(cls, file):
        with codecs.open(file, 'r', 'utf-16', 'surrogatepass') as json_file:
            data = json.load(json_file)
        return cls(file=file, items=data)
    @classmethod
    def delete(cls, file):
        return os.remove(file)
    @classmethod
    def generate(cls, file=None, directory=None, name=None, key_length=256, reference_key_length=4, count=1000, charset=letters):
        if file is None:
            if name is None:
                name = '{}.json'.format(cls.new_reference_key(8))
            if directory is None:
                directory = "."
            file = '{}/{}'.format(directory, name)
        items = {
            cls.new_reference_key(reference_key_length) : securegen(key_length, charset=charset) for i in range(count)
        }
        db = cls(file=file, items=items)
        db.save()
        return db
