import json
from ocdskingfisher.database import DatabaseStore


class Store:

    def __init__(self, config, database):
        self.config = config
        self.collection_id = None
        self.database = database

    def load_collection(self, collection_source, collection_data_version, collection_sample):
        self.collection_id = self.database.get_or_create_collection_id(collection_source, collection_data_version, collection_sample)

    def store_file(self, filename, url, data_type, encoding, local_filename):
        try:
            with open(local_filename, encoding=encoding) as f:
                data = json.load(f)

        except Exception as e:
            raise e
            # TODO Store error in database instead!

        self.store_json(filename, url, data_type, data)

    def store_json(self, filename, url, data_type, data):

        with DatabaseStore(database=self.database, collection_id=self.collection_id, file_name=filename) as store:

            objects_list = []
            if data_type == 'record_package_list_in_results':
                objects_list.extend(data['results'])
            elif data_type == 'release_package_list_in_results':
                objects_list.extend(data['results'])
            elif data_type == 'record_package_list' or data_type == 'release_package_list':
                objects_list.extend(data)
            else:
                objects_list.append(data)

            for json_data in objects_list:
                if not isinstance(json_data, dict):
                    raise Exception("Can not process data in file {} as JSON is not an object".format(data['filename']))

                if data_type == 'release' or data_type == 'record':
                    data_list = [json_data]
                elif data_type == 'release_package' or \
                        data_type == 'release_package_json_lines' or \
                        data_type == 'release_package_list_in_results' or \
                        data_type == 'release_package_list':
                    if 'releases' not in json_data:
                        if data_type == 'release_package_json_lines' and \
                                self.ignore_release_package_json_lines_missing_releases_error:
                            return
                        raise Exception("Release list not found in file {}".format(data['filename']))
                    elif not isinstance(json_data['releases'], list):
                        raise Exception("Release list which is not a list found in file {}".format(data['filename']))
                    data_list = json_data['releases']
                elif data_type == 'record_package' or \
                        data_type == 'record_package_json_lines' or \
                        data_type == 'record_package_list_in_results' or \
                        data_type == 'record_package_list':
                    if 'records' not in json_data:
                        raise Exception("Record list not found in file {}".format(data['filename']))
                    elif not isinstance(json_data['records'], list):
                        raise Exception("Record list which is not a list found in file {}".format(data['filename']))
                    data_list = json_data['records']
                else:
                    raise Exception("data_type not a known type")

                package_data = {}
                if not data_type == 'release':
                    for key, value in json_data.items():
                        if key not in ('releases', 'records'):
                            package_data[key] = value

                for row in data_list:
                    if not isinstance(row, dict):
                        raise Exception("Row in data is not a object {}".format(data['filename']))

                    if data_type == 'record' or \
                            data_type == 'record_package' or \
                            data_type == 'record_package_json_lines' or \
                            data_type == 'record_package_list_in_results' or \
                            data_type == 'record_package_list':
                        store.insert_record(row, package_data)
                    else:
                        store.insert_release(row, package_data)
