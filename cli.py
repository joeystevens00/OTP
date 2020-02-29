import sys, argparse
import otp.otp as otp
from otp.reference_db import ReferenceDB, ReferenceDBList
import secrets
import os.path
import codecs
import json
VERSION = 0.16
DEFAULT_REFERENCE_DB_FILE = '.reference_db.json'
import otp.util as util
import base64

class CLI:
    def __init__(self, args, no_exit=False):
        self.args = args
        self.db = None
        self.dbl = None
        self.no_exit = no_exit
        self.errors = []
        self.args['charset'] = self.args.get('charset')
        for k in self.args.keys():
            setattr(self, k, self.args.get(k))
        if self.charset:
            option = util.charset_options.get(self.charset.lower())
            if self.charset == 'ascii':
                self.charset = otp.ascii_chars
            elif self.charset == 'unicode':
                self.charset = otp.utf_chars
            elif self.charset == 'alphanumeric':
                self.charset = option
            else:
                raise ValueError('Unknown charset {}'.format(self.charset))
        else:
            self.charset = otp.letters
        self.encoding = util.charset_get_encoding(self.charset)
        self.input_files = {
            'message_file' : 'message',
            'key_file' : 'key'
        }

    def load_key_msg_args(self, args=None):
        if args == None:
            args = self.args
        self.key = args.get('key')
        self.message = args.get('message')

    def run(self):
        if self.verbose:
            print(self.args)

        if self.generate or self.generate_list:
            refdb_args = {}
            self.refdb_args = refdb_args
            if self.count:
                refdb_args['count'] = int(self.count)
            if self.key_length:
                refdb_args['key_length'] = int(self.key_length)
            refdb_args['charset'] = self.charset
            if self.generate:
                if self.reference_db:
                    refdb_args['file'] = self.reference_db
                self.db = ReferenceDB.generate(**refdb_args)
                print("Generated new reference database: {}".format(self.db.file))
            if self.generate_list:
                if not self.reference_db_list:
                    raise ValueError('--generate_list requires directory for list in argument --reference_db_list')
                refdb_args['directory'] = self.reference_db_list
                self.dbl = ReferenceDBList.generate(files=int(self.generate_list), **refdb_args)
                self.db = dbl.random_db()
            if not self.message:
                self.report_complete()


        self.load_input_files(self.input_files)
        if self.args['reference_db_list']:
            self.dbl = ReferenceDBList(directory=self.reference_db_list)
            if self.reference:
                refparts = self.reference.split('-')
                if len(refparts) == 2:
                    slug, self.reference = refparts
                    self.db = self.dbl.db_from_slug(slug)
            else:
                self.db = dbl.random_db()
            self.eference_db = self.db.file
        db_file = self.reference_db or DEFAULT_REFERENCE_DB_FILE
        if not self.db:
            if os.path.exists(db_file):
                self.db = ReferenceDB.load(db_file)

        if self.pop:
            if not self.message:
                if self.reference:
                    self.pop_reference_key()
                    self.report_complete()
                else:
                    raise ValueError('--pop requires a reference key')
        if not self.message:
            raise ValueError('--message, --generate, or --pop is required. Try running --help')
        noKey = not self.key and not self.reference
        if self.decrypt and noKey:
            raise ValueError('Decrypt requires either --key or --reference')

        # If have reference key
        if not self.key and not noKey:
            self.key = self.db.items.get(self.reference)
        # If no keys but just generated a database
        generatedDB = noKey and self.generate
        hasDbNoKey = not self.key and self.db
        if generatedDB or hasDbNoKey:
            self.reference, self.key = self.db.random_key()

        # Ensure key is of sufficent length
        if self.key and len(self.message) > len(self.key) and not self.unsafe_key_length:
            self.add_error("ERROR: KEY IS NOT OF SUFFICENT LENGTH TO ENCRYPT MESSAGE. Use --unsafe_key_length to disable")
            self.report_complete(exit_code=1)
        else:
            if self.key:
                if self.prefix_random_characters:
                    self.message = otp.securegen(len(key) - len(self.message), charset=self.charset) + self.message

        otp_extra_args = {}
        if self.charset == 'ascii' or self.charset == 'unicode':
            otp_extra_args['charset'] = self.charset
        mode = False if self.decrypt else True
        self.message, self.key = otp.otp(msg=self.message, key=self.key, encrypt=mode, **otp_extra_args)
        # if isinstance(msg, bytes):
        #     msg = msg.decode('utf-16', 'surrogatepass')
        reference_or_key = self.reference or self.key
        reference_or_key = '{}-{}'.format(db.slug,reference_or_key) if self.reference_db_list else reference_or_key
        self.key = reference_or_key
        self.report_complete()

    def get_message_from_file(self, mode='r', file_arg='message_file', file_value_arg='message'):
            codec_args = []
            extra_args = self.encoding_args()
            with codecs.open(self.args[file_arg], mode, *codec_args) as file:
                if file_arg == 'output_json':
                    message = json.load(file)
                    message = util.nested_operation(message, util.decodeb64, **extra_args)
                else:
                    message = file.read()
                    try:
                        message = util.decodeb64(message, **extra_args)
                    except:
                        pass
            return message

    def encoding_args(self):
        encoding = self.args.get('encoding') or util.charset_get_encoding(self.charset)
        encoding = encoding.lower()
        encoding_args = {}
        if encoding == 'utf-16':
            encoding_args['encoding'] = encoding
            encoding_args['encoding_options'] = ['surrogatepass']
        return encoding_args

    def store_message_file(self, file_location, file_contents, mode='w'):
        codec_args = []
        is_json = False
        extra_args = self.encoding_args()
        #encodeb64 = lambda x, **_x : base64.b64encode(x.encode(_x['encoding'], *_x.get('encoding_options', []))).decode('utf-8')
        if isinstance(file_contents, (dict, list, tuple)):
            is_json = True
            file_contents = util.nested_operation(file_contents, util.encodeb64, **extra_args)
        elif(isinstance(file_contents, str)):
            file_contents = util.encodeb64(file_contents, **extra_args)
        else:
            raise ValueError("Unable to handle type {} for file_contents".format(type(file_contents)))
        with codecs.open(file_location, mode, *codec_args) as message_file:
            if is_json:
                json.dump(file_contents, message_file)
            else:
                message_file.write(file_contents)

    def pop_reference_key(self, reference_key):
        if reference_key == None:
            reference_key = self.reference
        if not isinstance(reference_key, str):
            raise ValueError("Reference Key must be a string")
        if self.db:
            self.db.pop(reference_key)
            self.db.save()
        else:
            self.add_error("Unable to pop {}: No DB provided".format(reference_key))

    def add_error(self, msg):
        print(msg)
        self.errors.append(msg)

    def report_complete(self, exit_code=0):
        # Print results to STDOUT
        output_fields = {'MESSAGE':self.message, 'KEY':self.key, 'ERRORS': None}
        encoding = self.encoding
        for field in output_fields.keys():
            try:
                print(field, output_fields[field])
            except Exception as e:
                self.add_error("WARNING: while processing field {}: {}".format(field, e))

        # Delete reference key
        if self.pop:
            self.pop_reference_key()
        # Write message/key to file
        output_fields['ERRORS'] = self.errors
        keyfile_output = self.key
        if self.reference and self.db:
            keyfile_output = self.db.get(self.reference)
        output_files = {
                'output_message_file':self.message,
                'output_key_file':keyfile_output,
                'output_json':output_fields
        }
        self.process_output_files(output_files)
        if self.no_exit:
            return output_fields, self.db, exit_code
        sys.exit(exit_code)

    def process_output_files(self, output_files):
        for output_file in output_files.keys():
            file_contents = output_files[output_file]
            file_location = self.args[output_file]
            if self.args[output_file]:
                self.store_message_file(file_location, file_contents)
                file_type = output_file.split('_')[1] # output_KEY output_JSON output_MESSAGE
                print("Wrote {} to {}".format(file_type,self.args[output_file]))

    def load_input_files(self, input_files):
        for input_file_key in input_files.keys():
            input_file_value_key = input_files[input_file_key]
            if self.args[input_file_key]:
                try:
                    self.args[input_file_value_key] = self.get_message_from_file(
                        file_arg=input_file_key,
                        file_value_arg=input_file_value_key
                    )
                except UnicodeError as e:
                    #self.errors.append(e)
                    self.args[input_file_value_key] = self.get_message_from_file(
                        mode='rb',
                        file_arg=input_file_key,
                        file_value_arg=input_file_value_key
                    )
        self.load_key_msg_args()
        return self.args


def main(argv, no_exit=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", '--message', help='Message to encrypt/decrypt')
    parser.add_argument("-f", '--message_file', help='File where message to encrypt/decrypt is')
    parser.add_argument("-d", '--decrypt', help='Decrypt Message', action='store_true')
    parser.add_argument("-r", '--reference', help='Reference Key to use')
    parser.add_argument("-g", '--generate', help='Generate new reference database. Use -db to specify file path, -c for number of keys to generate, -l for length of keys', action='store_true')
    parser.add_argument("-gl", '--generate_list', help='Generate new reference database list of length. Arguments: -dbl : directory for list, -c : number of keys to generate in each db, -l for length of keys')
    parser.add_argument("-db", '--reference_db', help='Reference DB file')
    parser.add_argument("-dbl", '--reference_db_list', help='Reference DB List directory')
    parser.add_argument("-c", '--count', help='Number of keys to generate with --generate')
    parser.add_argument("-l", '--key_length', help='Length of generated keys for --generate')
    parser.add_argument("-k", '--key', help='Key to decrypt/encrypt with')
    parser.add_argument("-kf", '--key_file', help='Key file to decrypt/encrypt with')
    parser.add_argument("-p", '--pop', help='Delete key', action='store_true')
    parser.add_argument("-v", '--verbose', help='Print more stuff', action='store_true')
    parser.add_argument("-s", '--strip', help='Strip formatting from message', action='store_true')
    parser.add_argument("-ch", '--charset', help='Charset to use. Can be a custom string or one of [ascii, unicode], alphanumeric]')
    parser.add_argument("-o", '--output_message_file', help='Write raw message to file')
    parser.add_argument("-ok", '--output_key_file', help='Write key to file')
    parser.add_argument("-oj", '--output_json', help='Write message and key to JSON file')
    parser.add_argument('--unsafe_key_length', help='Allow encrypting/decrypting with key shorter than message', action='store_true')
    parser.add_argument("-rc", '--prefix_random_characters', help='If message is shorter than key prefix message with garbage.', action='store_true')
    args = vars(parser.parse_args())
    CLI(args, no_exit).run()
if __name__ == "__main__":
   main(sys.argv[1:])
