# Python imports
import json
from collections import OrderedDict


class Help:
    def __init__(self, file):
        self.commands = OrderedDict()
        self.aliases = OrderedDict()

        with open(file, 'r', encoding='utf-8') as raw:
            data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(raw.read())
        self.__iterator(data)

    @staticmethod
    def __util_get_command_description(description):
        for each in description:
            if isinstance(description[each], list):
                description[each] = '<br>'.join(description[each])
        return description

    @staticmethod
    def __util_get_command_params(params):
        new_params = dict()
        
        for each in params:
            for lang in each['name']:
                if lang not in new_params:
                    new_params[lang] = list()
                
                if each.get('hideName') is True:
                    string = ''
                    if 'before' in each and 0 < len(each['before']):
                        string = each['before']
                    if 'after' in each and 0 < len(each['after']):
                        if '' != string:
                            string = string + ' ' + each['after']
                        else:
                            string = each['after']
                    if each.get('required') is False:
                        string = '[' + string + ']'
                else:
                    string = '<' + each['name'][lang] + '>'
                    if 'before' in each and 0 < len(each['before']):
                        string = each['before'] + ' ' + string
                    if 'after' in each and 0 < len(each['after']):
                        string = string + ' ' + each['after']
                    if 'required' in each and each['required'] is False:
                        string = '[' + string + ']'
                
                new_params[lang].append(string)
        return new_params

    @staticmethod
    def __util_get_command_requirements(data):
        u = None
        b = None

        if data.get('admin') is True:
            requirements = 'Admin'
        else:
            if 'level' in data:
                requirements = 'Lvl ' + str(data['level']) + '+'
                if 'level2' in data:
                    requirements += '/' + str(data['level2']) + '+'
            else:
                requirements = 'Lvl 1+'
                if 'level2' in data:
                    requirements += '/' + str(data['level2']) + '+'
        
            if data.get('orModerator') is True:
                requirements += '|@UisM@'
            elif 'requiresUserModerator' in data or 'requiresBotModerator' in data:
                u = '@UisM@' if data.get('requiresUserModerator') else None
                b = '@BisM@' if data.get('requiresBotModerator') else None
            
        req = [requirements]
        if None != u:
            req.append(u)
        if None != b:
            req.append(b)
        return req
            
    def __iterator(self, data, parents=list()):
        for name in data:
            value = data[name]
            if 'isCategory' in value and True == value['isCategory']:
                p_copy = list(parents)
                p_copy.append(value['name'])
                if 'children' in value:
                    self.__iterator(value['children'], p_copy)
            else:
                command = {
                    'description': self.__util_get_command_description(value['description']),
                    'aliases': None,
                    'params': self.__util_get_command_params(value['params']) if 'params' in value else None,
                    'requirements': self.__util_get_command_requirements(value),
                    'parents': parents,
                    'pm': (value.get('pm') in [None, True]),
                    'room': (value.get('room') in [None, True]),
                    'slow': (value.get('slow') is True),
                    'raw': value
                }
                
                if 'aliases' in value:
                    command['aliases'] = value['aliases']
                    for each in value['aliases']:
                        self.aliases[each] = name
                self.commands[name] = command