import glob
import subprocess
from rich.console import Console
from rich import print
from rich.prompt import Prompt
import requests
import os
import re
from time import sleep
import shutil

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
        console.log('Use Downloaded Buildtools')
        return
    buildtools = requests.get('https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar').content
    with open('./buildtools.jar', mode='wb') as f:
        f.write(buildtools)

def build_spigot(version = None, jdk_version = None):
    try:
        jdk = str(get_jdk(jdk_version if jdk_version is not None else 8))
    except NoJdkError:
        console.log(f'[bold][red]Java {jdk_version}[/bold] is Not Found. Please Install.')
        exit()
    os.chdir(cache_dir)
    os.makedirs('build', exist_ok=True)
    os.chdir('build')
    get_spigot_buildtools()
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
            console.log('JDK version error detected. Trying with ', get_jdk(jdk_ver))
            build_spigot(version, jdk_version = jdk_ver)
            return
        else:
            console.log('[green][bold]Building successfully Done!')
            shutil.copy(f'./spigot-{version}.jar', f'../spigot-{version}.jar')

if __name__ == '__main__':
    version = Prompt.ask('Which Version to use?', default='Latest')
    if version == 'Latest':
        version = None
    cache_dir = os.path.expanduser('~')+'/.remine/cache/'
    os.makedirs(cache_dir, exist_ok=True)
    console = Console()
    if glob.glob(f'{cache_dir}spigot-{version}.jar') == []:
        with console.status('[bold][blue]Building Spigot'):
            build_spigot(version)
    else:
        print('[green]Use cached server.')
