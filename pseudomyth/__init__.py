# coding=utf-8

from __future__ import print_function, unicode_literals

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser

from random import choice
from sys import argv, exit
import os
import shutil

try:
    from shlex import quote
except ImportError:
    from pipes import quote

try:
    from subprocess import getoutput, getstatusoutput
except ImportError:
    from commands import getoutput, getstatusoutput
import re

CONFIG = {}

try:
    string_input = raw_input
except NameError:
    # this is python 3
    string_input = input


def wait():
    """
    Await user input.
    """

    try:
        string_input('')
    except KeyboardInterrupt:
        exit()


def open_command():
    """
    Get what we can reasonably assume is this system's general-purpose `open`
    command.
    """

    path_dirs = os.environ.get('PATH').split(':')
    fmt = '{cmd} {{filenames}}'

    for candidate, path in ((c, p) for c in [
        'xdg-open',  # most linux distros
        'open',  # os x
        'cygstart', 'cygstart.exe',  # cygwin
    ] for p in path_dirs):
        if os.path.isdir(path) and candidate in os.listdir(path):
            return fmt.format(cmd=candidate)

    print(
        "Your system doesn't have an `open` command that I know to look for, "
        "and you haven't configured a custom player command, so I don't know "
        "how I should play video files.\n\n"
        "If you create a file at ~/.pseudomyth and set it up with a shell "
        "command I can use to play video files, that'd be helpful. As an "
        "example, the author's looks something like this:\n\n"
        "[DEFAULT]\n"
        "command=mplayer -fs {filenames}"
    )
    exit(1)


def populate_config():
    config_path = os.path.expanduser('~/.pseudomyth')

    if os.path.exists(config_path):
        parser = RawConfigParser(dict_type=dict)
        parser.read(config_path)
        CONFIG.update(parser.defaults())


def fullwidth(string):
    # zenhan is broken, we need to do this manually
    chars = {
        '0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５',
        '6': '６', '7': '７', '8': '８', '9': '９',
    }

    return ''.join([chars[c] for c in string])


class Series():
    """ A series. Contains episodes. """
    def __init__(self, name):
        self.name = name
        self.episodes = []
        self.op = self.ed = False

    def __repr__(self):
        bonus = ''
        if self.op:
            bonus += 'OP '
        if self.ed:
            bonus += 'ED '

        return '%s %r %s' % (self.name, [e.epno for e in self.episodes], bonus)

    def append(self, episode):
        if episode.epno in ['op', 'ed']:
            setattr(self, episode.epno, episode)
        else:
            self.episodes.append(episode)
            self.episodes = sorted(self.episodes,
                                   key=lambda episode: episode.epno)


class Episode():
    """ An episode within a series, and its associated file. """
    def __init__(self, filename):
        self.parsed = False
        self.filename = filename

        # resolve aliases
        if getstatusoutput('getTrueName')[0] != 32512:
            self.truefilename = getoutput('getTrueName "%s"' % filename)
        else:
            self.truefilename = self.filename

        exts = ['mkv', 'avi', 'mp4', 'mpg', 'webm', 'mov', 'ogg', 'wmv', 'flv',
                'm4v']

        if (not os.path.isdir(filename)
                and filename.split('.')[-1].lower() in exts):
            self.parse(os.path.splitext(filename)[0])

    def __repr__(self):
        return '%s - %i' % (self.series, self.epno)

    def parse(self, filename):
        filename = filename.replace('_', ' ')

        # remove repeated spaces
        while '  ' in filename:
            filename = filename.replace('  ', ' ')

        # remove metadata (things in brackets)
        metadata = re.findall('[\(\[].*?[\)\]]', filename)
        for m in metadata:
            filename = filename.replace(m, '').strip()

        epno = None
        epno_matches = [
            # S01E01
            r'\bS\d+E(?P<epno>\d+)\b',
            # 01v2
            r'\b(?P<epno>\d+)v\d+\b',
            # - 01
            r'\s-\s(?P<epno>\d+)\b',
            # ep( )01
            r'ep ?(?P<epno>\d+)\b',
            # ep. 01
            r'ep\. (?P<epno>)\d+\b',
            # 01
            r'\b(?P<epno>\d+)\b',
        ]

        for regex in epno_matches:
            try:
                epno = int(list(re.finditer(
                    regex, filename, flags=re.I
                ))[0].group('epno'))
            except IndexError:
                pass
            else:
                break

        if epno is None:
            # it might be an opening or an ending or an OVA
            op_matches = [r'(?i)\bOP\d*\b']
            for regex in op_matches:
                if re.search(regex, filename):
                    epno = 'op'

            ed_matches = [r'(?i)\bED\d*\b']
            for regex in ed_matches:
                if re.search(regex, filename):
                    epno = 'ed'

            one_matches = [r'(?i)\bSpecial\b', r'(?i)\bOVA\b']
            for regex in one_matches:
                if re.search(regex, filename):
                    epno = 0

        if epno is None:
            # potentially a film or something
            epno = 0

        series = None

        series_matches = [
            r'(?i)^.*?(?=\sS\d+E\d+\b)',  # bento S1E01
            r'(?i)^.*?(?=\sep\.?\s*\d+\b)',  # bento ep(.)(|)
            r'(?i)^.*?(?=\s-\s(?=\d+|Special|OVA|OP\d*|ED\d*)\b)',  # bento - 0
            r'(?i)^.*?\s(?=\d|OP\d*\b|ED\d*\b|Special|OVA\b)',  # bento 0
            r'(?i)^.*$',  # bento
        ]

        for regex in series_matches:
            try:
                series = re.findall(regex, filename)[0].strip()
            except IndexError:
                pass
            else:
                break

        if series is None:
            print(' :: abandoning parse of', self.filename, 'at series')
            return

        self.epno = epno
        self.series = series

        self.parsed = True
        # print '%s - %i %r' % (series, epno, metadata)


if not argv[-1] == 'legacy':
    populate_config()

    if not os.path.exists('consumed'):
        os.makedirs('consumed')

    serieslist = []

    files = [name for name in os.listdir('.') if not name.startswith('.')]

    for filename in files:
        episode = Episode(filename)
        series_names = [s.name for s in serieslist]

        if episode.parsed and episode.series not in series_names:
            series = Series(episode.series)
            series.append(episode)
            serieslist.append(series)

        elif episode.parsed:
            series = [s for s in serieslist if s.name == episode.series][0]
            series.append(episode)

    weighted = []
    for series in serieslist:
        for episode in series.episodes:
            weighted.append(series)

    total = len(weighted)
    keion_count = fullwidth(str(total))

    if total != 1:
        plural = 'Ｓ'
    else:
        plural = ''

    print('／人{e} ‿‿ {e}人＼  ＬＥＴ’Ｓ　ＷＡＴＣＨ　{count}　ＫＥＩＯＮ{s}！'.format(
        e='\x1b[31m◕\x1b[0m',
        count=keion_count,
        s=plural,
    ))

    for series in sorted(serieslist, key=lambda series: series.name):
        print(series)

    if serieslist:
        print(
            "\nWhen you're ready, press enter to start playing stuff or ^C "
            "to exit")

    for n in range(len(weighted)):
        wait()

        series = choice(weighted)
        playlist = []

        series = choice(weighted)

        episode = series.episodes.pop(0)
        weighted.remove(series)

        if series.op:
            playlist.append(series.op.truefilename)

        playlist.append(episode.truefilename)

        if series.ed:
            playlist.append(series.ed.truefilename)

        configured_player = CONFIG.get('command')
        if configured_player is None:
            configured_player = open_command()

        command = configured_player.format(
            filenames=' '.join([quote(f) for f in playlist])
        )

        print('\r -- playing...', end='')
        status, output = getstatusoutput(command)

        if status == 0:
            shutil.move(episode.filename, 'consumed/%s' % episode.filename)
        else:
            print(
                "\n\nThe playback command freaked out and I'm assuming "
                "playback was not successful.\n\n"
                "{file} has not been moved and I'm gonna quit now so you can "
                "try to work out what happened. For reference, the command "
                "that I ran was:\n\n"
                "{command}\n\n"
                "And the output of said command was:\n\n"
                "{output}".format(
                    file=quote(episode.filename),
                    command=command,
                    output=output,
                )
            )
            exit(1)

        print('\r%i/%i - %s' % (n+1, total, episode), end='')

else:
    # manual series entry for when the above bullshit inevitably breaks
    showlist = []

    while True:
        newkeion = string_input('')
        if newkeion == '':
            break
        else:
            showlist.append(newkeion)

    # showlist.append('strike witches')

    total = len(showlist)
    n = 1

    for n in range(len(showlist)):
        nextshow = choice(showlist)
        print('%i/%i - %s' % (n+1, total, nextshow), end='')
        showlist.remove(nextshow)
        string_input('')
