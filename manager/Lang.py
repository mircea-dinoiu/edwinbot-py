# Python imports
import json
import os
import fnmatch

# Project imports
from util.render import highlight


class Lang:
    lang = dict()
    file_pattern = '*.json'
    
    def __init__(self, root):
        path = root + '/data/lang/'
        
        files = [
            os.path.join(dir_path, f)
            for dir_path, dir_names, files in os.walk(path)
            for f in fnmatch.filter(files, self.file_pattern)
        ]
        
        self.__iterator(files)

    @staticmethod
    def __util_filter_dict(data):
        for key in data:
            if not isinstance(data[key], list):
                data[key] = [data[key]]
            for variant in data[key]:
                for lang in variant:
                    if isinstance(variant[lang], list):
                        variant[lang] = '<br>'.join(variant[lang])

                    if key.startswith('ERROR_'):
                        variant[lang] = '{0} {1}'.format(
                            highlight('✖', 'Red'),
                            variant[lang]
                        )
                    elif key.startswith('SUCCESS_'):
                        variant[lang] = '{0} {1}'.format(
                            highlight('✔', 'Green'),
                            variant[lang]
                        )
            
    def __iterator(self, files):
        for file in files:
            with open(file, 'r', encoding='utf-8') as raw:
                data = json.loads(raw.read())
                self.__util_filter_dict(data)
                self.lang.update(data)