import os, socket, time
import shutil, string, random

from core import utils
from pprint import pprint
from configparser import ConfigParser, ExtendedInterpolation
import string

# Console colors
W = '\033[1;0m'   # white
R = '\033[1;31m'  # red
G = '\033[1;32m'  # green
O = '\033[1;33m'  # orange
B = '\033[1;34m'  # blue
Y = '\033[1;93m'  # yellow
P = '\033[1;35m'  # purple
C = '\033[1;36m'  # cyan
GR = '\033[1;37m'  # gray

__author__ = '@j3ssiejjj'
__version__ = '1.2'

def banner():
    print(r"""{1}

                       `@@`
                      @@@@@@
                    .@@`  `@@.
                    :@      @:
                    :@  {5}:@{1}  @:                       
                    :@  {5}:@{1}  @:                       
                    :@      @:                             
                    `@@.  .@@`
                      @@@@@@
                        @@
                     {0}@{1}  {1}@@  {0}@{1}               
                    {0}+@@{1} {1}@@ {0}@@+{1}                    
                 {5}@@:@#@,{1}{1}@@,{5}@#@:@@{1}           
                ;@+@@`#@@@@#`@@+@;
                @+ #@@@@@@@@@@# +@
               @@  @+`@@@@@@`+@  @@
               @.  @   ;@@;   @  .@
              {0}#@{1}  {0}'@{1}          {0}@;{1}  {0}@#{1}

                     
             Osmedeus v{5}{6}{1} by {2}{7}{1}

                    ¯\_(ツ)_/¯
        """.format(C, G, P, R, B, GR, __version__, __author__))

def parsing_config(config_path, args):
    options = {}

    ##some default path
    github_api_key = str(os.getenv("GITROB_ACCESS_TOKEN"))
    cwd = str(os.getcwd())

    #just hardcode if gopath not loaded
    go_path = cwd + "/plugins/go"
    # go_path = str(os.getenv("GOPATH")) + "/bin"
    # if "None" in go_path:
    #     go_path = cwd + "/plugins/go"

    bot_token = str(os.getenv("SLACK_BOT_TOKEN"))
    log_channel = str(os.getenv("LOG_CHANNEL"))
    status_channel = str(os.getenv("STATUS_CHANNEL"))
    report_channel = str(os.getenv("REPORT_CHANNEL"))
    stds_channel = str(os.getenv("STDS_CHANNEL"))
    verbose_report_channel = str(os.getenv("VERBOSE_REPORT_CHANNEL"))


    if os.path.isfile(config_path):
        utils.print_info('Config file detected: {0}'.format(config_path))
        #config to logging some output
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(config_path)
    else:
        utils.print_info('New config file created: {0}'.format(config_path))
        shutil.copyfile(cwd + '/template-config.conf', config_path)

        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(config_path)

    workspace = cwd + "/workspaces/"
    config.set('Enviroments', 'cwd', cwd)
    config.set('Enviroments', 'go_path', go_path)
    config.set('Enviroments', 'github_api_key', github_api_key)
    config.set('Enviroments', 'workspaces', str(workspace))

    if args.debug:
        config.set('Slack', 'bot_token', 'bot_token')
        config.set('Slack', 'log_channel', 'log_channel')
        config.set('Slack', 'status_channel', 'status_channel')
        config.set('Slack', 'report_channel', 'report_channel')
        config.set('Slack', 'stds_channel', 'stds_channel')
        config.set('Slack', 'verbose_report_channel', 'verbose_report_channel')
    else:
        config.set('Slack', 'bot_token', bot_token)
        config.set('Slack', 'log_channel', log_channel)
        config.set('Slack', 'status_channel', status_channel)
        config.set('Slack', 'report_channel', report_channel)
        config.set('Slack', 'stds_channel', stds_channel)
        config.set('Slack', 'verbose_report_channel', verbose_report_channel)

    ##config of the tool
    if args.slow:
        speed = "slow"
    else:
        speed = "quick"

    module = str(args.module)
    debug = str(args.debug)
    force = str(args.force)

    config.set('Mode', 'speed', speed)
    config.set('Mode', 'module', module)
    config.set('Mode', 'debug', debug)
    config.set('Mode', 'force', force)

    ##target stuff
    #parsing agument
    git_target = args.git if args.git else None
    burpstate_target = args.burp if args.burp else None
    target_list = args.targetlist if args.targetlist else None
    company = args.company if args.company else None
    direct_input = args.input if args.input else None

    if args.target:
        target = args.target
        output = args.output if args.output else args.target
        company = args.company if args.company else args.target

        strip_target = target.replace('https://', '').replace('http://', '')
        if '/' in strip_target:
            strip_target = strip_target.split('/')[0]

        if args.workspace:
            if args.workspace[-1] == '/':
                workspace = args.workspace + options['env']['STRIP_TARGET']
            else:
                workspace = args.workspace + '/' + options['env']['STRIP_TARGET']
        else:
            workspace += strip_target

        if not direct_input:
            try:
                ip = socket.gethostbyname(strip_target)
            except:
                ip = "None"
                utils.print_bad("Something wrong to connect to {0}".format(target))
        else:
            ip = None

    config.set('Target', 'input', str(direct_input))
    config.set('Target', 'git_target', str(git_target))
    config.set('Target', 'burpstate_target', str(burpstate_target))
    config.set('Target', 'target_list', str(target_list))
    config.set('Target', 'output', str(output))
    config.set('Target', 'target', str(target))
    config.set('Target', 'strip_target', str(strip_target))
    config.set('Target', 'company', str(company))
    config.set('Target', 'ip', str(ip))
    config.set('Enviroments', 'workspace', str(workspace))


    #create workspace folder for the target
    utils.make_directory(workspace)

    #set random password if default password detect
    if config['Server']['password'] == 'super_secret':
        new_pass = ''.join(random.choice(string.ascii_lowercase)
                           for i in range(6)).upper()
        config.set('Server', 'password', new_pass)


    #save the config
    with open(config_path, 'w') as configfile:
        config.write(configfile)


    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_path)
    sections = config.sections()

    for sec in sections:
        for key in config[sec]:
            # if key = 
            options[key.upper()] = config.get(sec, key)

    ######
    ## Store this to a json file

    return options

