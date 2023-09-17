from rich.prompt import Prompt
from srvdl import serverdownload

version = Prompt.ask('Which Version to use?', default='Latest')
if version == 'Latest':
    version = None
type = Prompt.ask('Which Server type to use?', choices=['vanilla', 'paper', 'purpur', 'spigot'], default='paper')

serverdownload(version, type)
