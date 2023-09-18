import glob
import subprocess
from rich.console import Console
from rich import print
from rich.prompt import Prompt
import requests
import os
import re
import shutil
console = Console()
cache_dir = os.path.expanduser('~')+'/.remine/cache/'

class NoJdkError(Exception):
    pass

def get_jdk(version = 8):
    jdk_location = glob.glob('/usr/lib/jvm/*/bin/java')

    for name in jdk_location:
        if '8' in str(name):
            if version == 8:
                return name
        else:
            result = subprocess.run([name, '--version'], text=True, capture_output=True).stdout
            if int(version) == int(result.split()[1][0:2]):
                return name
    raise NoJdkError

def get_spigot_buildtools():
    if os.path.exists('./buildtools.jar'):
        return
    buildtools = requests.get('https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar').content
    open('./buildtools.jar', mode='wb').write(buildtools)

def build_spigot(version = None, jdk_version = None, retry = False):
    try:
        jdk = str(get_jdk(jdk_version if jdk_version is not None else 8))
    except NoJdkError:
        console.log(f'[bold][red]Java {jdk_version}[/bold] is Not Found. Please Install.')
        exit()
    os.chdir(cache_dir)
    os.makedirs('build', exist_ok=True)
    os.chdir('build')
    get_spigot_buildtools()
    if retry:
        pass
    else:
        console.log('Building started.')
    result = subprocess.run(
            [jdk, '-jar', 'buildtools.jar', '--rev', version if version is not None else 'latest'],
            text=True, capture_output=True
    )

    if result.stderr is None:
        return

    else:
        if 'but you are using' in result.stderr:
            error = str(result.stderr).split('\n')[4]
            jdk_ver = re.findall(r'\[(.+)\]', error)[0][5:7]
            console.log('JDK version error detected. Retrying with ', get_jdk(jdk_ver))
            build_spigot(version, jdk_version = jdk_ver, retry=True)
            return
        else:
            shutil.copy(f'./spigot-{version}.jar', f'../spigot-{version}.jar')

def download_paper(version = None):
    os.chdir(cache_dir)
    if version == None:
        response = requests.get('https://api.papermc.io/v2/projects/paper') 
        version = response.json()['versions'].pop()
    response = requests.get(f'https://api.papermc.io/v2/projects/paper/versions/{version}')
    try:
        build_number = response.json()['builds'].pop()
    except:
        print('[red]ERROR!')
        exit()
    response = requests.get(f'https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build_number}/downloads/paper-{version}-{build_number}.jar')
    if response.status_code == requests.codes.ok:
        pass
    else:
        print('[red]ERROR!')
        exit()
    open(f'{cache_dir}paper-{version}.jar', 'wb').write(response.content)

def download_purpur(version = None):
    os.chdir(cache_dir)
    if version == None:
        response = requests.get('https://api.purpurmc.org/v2/purpur') 
        version = response.json()['versions'].pop()
    response = requests.get(f'https://api.purpurmc.org/v2/purpur/{version}/latest/download')
    if response.status_code == requests.codes.ok:
        pass
    else:
        print('[red]ERROR!')
        exit()
    open(f'{cache_dir}purpur-{version}.jar', 'wb').write(response.content)


def serverdownload(version = None, type = 'paper'):
    os.makedirs(cache_dir, exist_ok=True)
    if glob.glob(f'{cache_dir}{type}-{version}.jar') == []:
        if type == 'spigot':
            with console.status('[bold][orange]Building Spigot'):
                build_spigot(version)
        elif type == 'paper':
            with console.status('[bold][blue]Downloading Paper'):
                download_paper(version)
        elif type == 'purpur':
            with console.status('[bold][purple]Downloading Purpur'):
                download_purpur(version)
        elif type == 'vanilla':
            exit()
        else:
            console.log('[red]Sorry, this is an Error. ;)')
            exit()
        console.log('[green][bold]Successfully Done!')
    else:
        print('[green]Use cached server.')
