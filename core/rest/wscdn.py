import os
import glob
import json
from pathlib import Path
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from flask import Flask, request, escape, make_response, send_from_directory
import utils

# incase you can't install ansi2html it's won't break the api
try:
    from ansi2html import Ansi2HTMLConverter
except:
    pass

current_path = os.path.dirname(os.path.realpath(__file__))

'''
render stdout content 
'''


class Wscdn(Resource):

    def verify_file(self, filename):
        option_files = glob.glob(
            current_path + '/storages/**/options.json', recursive=True)

        # loop though all options avalible
        for option in option_files:
            json_option = utils.reading_json(option)
            stdout_path = json_option.get('WORKSPACES') + "/" + filename

            if utils.not_empty_file(stdout_path):
                return json_option.get('WORKSPACES'), os.path.normpath(filename)

            # get real path 
            p = Path(filename)
            ws = p.parts[0]
            if ws != utils.url_encode(ws):
                # just replace the first one
                filename_encode = filename.replace(ws, utils.url_encode(ws), 1)
                stdout_path_encode = json_option.get('WORKSPACES') + filename_encode
                if utils.not_empty_file(stdout_path_encode):
                    return json_option.get('WORKSPACES'), os.path.normpath(filename_encode)

        return False, False

    def get(self, filename):
        ws_path, stdout_path = self.verify_file(filename)

        if not stdout_path:
            return 'Custom 404 here', 404
        
        return send_from_directory(ws_path, stdout_path)
