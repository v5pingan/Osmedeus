import os
from core import execute
from core import slack
from core import utils

class CorsScan(object):
    """docstring for PortScan"""
    def __init__(self, options):
        utils.print_banner("CORS Scanning")
        utils.make_directory(options['WORKSPACE'] + '/cors')
        self.module_name = self.__class__.__name__
        self.options = options
        if utils.resume(self.options, self.module_name):
            utils.print_info("It's already done. use '-f' options to force rerun the module")
            return
        slack.slack_noti('status', self.options, mess={
            'title':  "{0} | {1}".format(self.options['TARGET'], self.module_name),
            'content': 'Start Scanning CORS for {0}'.format(self.options['TARGET'])
        })
        self.initial()
        utils.just_waiting(self.options, self.module_name)
        slack.slack_noti('good', self.options, mess={
            'title':  "{0} | {1} ".format(self.options['TARGET'], self.module_name),
            'content': 'Done Scanning CORS for {0}'.format(self.options['TARGET'])
        })


    def initial(self):
        self.run()
    
    def run(self):
        commands = execute.get_commands(self.options, self.module_name).get('routines')
        for item in commands:
            utils.print_good('Starting {0}'.format(item.get('banner')))
            #really execute it
            execute.send_cmd(self.options, item.get('cmd'), item.get(
                'output_path'), item.get('std_path'), self.module_name)

        utils.just_waiting(self.options, self.module_name, seconds=10)
        #just save commands
        logfile = utils.replace_argument(self.options, '$WORKSPACE/log.json')
        utils.save_all_cmd(self.options, logfile)

