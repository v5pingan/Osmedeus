import os, time
from core import execute
from core import slack
from core import utils

class IPSpace(object):
    ''' Scanning vulnerable service based version '''
    def __init__(self, options):
        utils.print_banner("IP Discovery")
        utils.make_directory(options['WORKSPACE'] + '/ipspace')
        self.module_name = self.__class__.__name__
        self.options = options

        if utils.resume(self.options, self.module_name):
            utils.print_info("Detect is already done. use '-f' options to force rerun the module")
            return

        slack.slack_noti('status', self.options, mess={
            'title':  "{0} | {1}".format(self.options['TARGET'], self.module_name),
            'content': 'Start IP Discovery for {0}'.format(self.options['TARGET'])
        })
        self.initial()
        utils.just_waiting(self.options, self.module_name)
        try:
            self.conclude()
        except:
            utils.print_bad("Something wrong with conclude for {0}".format(self.module_name))

        slack.slack_noti('good', self.options, mess={
            'title':  "{0} | {1} ".format(self.options['TARGET'], self.module_name),
            'content': 'Done IP Discovery for {0}'.format(self.options['TARGET'])
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

        utils.just_waiting(self.options, self.module_name, seconds=2)
        #just save commands
        logfile = utils.replace_argument(self.options, '$WORKSPACE/log.json')
        utils.save_all_cmd(self.options, logfile)

    #update the main json file
    def conclude(self):
        utils.print_banner("Conclusion for {0}".format(self.module_name))
        main_json = utils.reading_json(utils.replace_argument(self.options, '$WORKSPACE/$COMPANY.json'))

        ips_file = utils.replace_argument(self.options, '$WORKSPACE/ipspace/$OUTPUT-ipspace.txt')
        with open(ips_file, 'r') as s:
            ips = s.read().splitlines()
        main_json['IP Space'] = ips

        #write that json again
        utils.just_write(utils.replace_argument(self.options, '$WORKSPACE/$COMPANY.json'), main_json, is_json=True)
        
        utils.print_banner("{0} Done".format(self.module_name))
        
