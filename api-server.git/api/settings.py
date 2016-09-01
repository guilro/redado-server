import logging
import os
import yaml

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'apitest'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']


def iter_domain():
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'domain')
    assert os.path.exists(dir), "Directory doesn't exist: {}".format(dir)
    for sub_dir, dirs_name, filenames in os.walk(dir):
        for dir_name in dirs_name[:]:
            if dir_name.startswith('.'):
                dirs_name.remove(dir_name)
        for filename in filenames:
            if not filename.endswith(".yaml"):
                continue
            yaml_file_path = os.path.join(sub_dir, filename)
            with open(yaml_file_path) as yaml_file:
                try:
                    resource = os.path.split(os.path.splitext(yaml_file_path)[0])[1]
                    logging.info("Loaded domain file {}".format(resource))
                    yield resource, yaml.load(yaml_file)
                except (UnicodeDecodeError, yaml.constructor.ConstructorError, yaml.parser.ParserError, yaml.scanner.ScannerError):
                    logging.warning("Invalid syntax in YAML file {}".format(yaml_file_path))

DOMAIN = {}

for domain, definition in iter_domain():
    if 'mongo_indexes' in definition:
        for index_name, index in definition['mongo_indexes'].items():
            fields = definition['mongo_indexes'][index_name]['fields']
            for i, pair in enumerate(fields):
                fields[i] = (pair[0], pair[1])
            if 'options' in definition['mongo_indexes'][index_name]:
                definition['mongo_indexes'][index_name] = (
                    fields,
                    definition['mongo_indexes'][index_name]['options']
                )
            else:
                definition['mongo_indexes'][index_name] = fields
    DOMAIN[domain] = definition