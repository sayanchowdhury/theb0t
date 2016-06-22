#!/usr/bin/env python
'''fpaste - a cli frontend for the fpaste.org pastebin'''
#
# Copyright 2008, 2010 Fedora Unity Project (http://fedoraunity.org)
# Author: Jason 'zcat' Farrell <farrellj@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
VERSION = '0.3.7.4'
USER_AGENT = 'fpaste/' + VERSION
SET_DESCRIPTION_IF_EMPTY = 1  # stdin, clipboard, sysinfo
#FPASTE_URL = 'http://fpaste.org/'
FPASTE_URL = 'http://paste.fedoraproject.org/'

import os
import sys
import urllib
import urllib2
import subprocess
import json
from optparse import OptionParser, OptionGroup, SUPPRESS_HELP


def is_text(text, maxCheck=100, pctPrintable=0.75):
    '''returns true if maxCheck evenly distributed chars in text are >= pctPrintable% text chars'''
    # e.g.: /bin/* ranges between 19% and 42% printable
    from string import printable
    nchars = len(text)
    if nchars == 0:
        return False
    ncheck = min(nchars, maxCheck)
    inc = float(nchars) / ncheck
    i = 0.0
    nprintable = 0
    while i < nchars:
        if text[int(i)] in printable:
            nprintable += 1
        i += inc
    pct = float(nprintable) / ncheck
    return (pct >= pctPrintable)


def confirm(prompt="OK?"):
    '''prompt user for yes/no input and return True or False'''
    prompt += " [y/N]: "
    try:
        ans = raw_input(prompt)
    except EOFError:    # already read sys.stdin and hit EOF
        # rebind sys.stdin to user tty (unix-only)
        try:
            mytty = os.ttyname(sys.stdout.fileno())
            sys.stdin = open(mytty)
            ans = raw_input()
        except:
            print >> sys.stderr, "could not rebind sys.stdin to %s after sys.stdin EOF" % mytty
            return False

    if ans.lower().startswith("y"):
        return True
    else:
        return False


def get_shortened_url(long_url, password):
    '''Get shortened URL from paste data'''

    # NOTE: this uses password, not paste_password
    if password:
        params = urllib.urlencode({'mode': 'json', 'password': password})
    else:
        params = 'mode=json'

    req = urllib2.Request(url=long_url + '/', data=params)
    try:
        f = urllib2.urlopen(req)
    except urllib2.URLError:
        return False

    # We know that short_url is always the third last line in the json output
    # Iterating over each line is a bad idea. It'll break everytime it
    # encounters a "short_url" string.
    try:
        result = json.loads('{' + f.readlines()[-3] + '}')['short_url']
    except ValueError, e:
        return False
    return result


def paste(text, options):
    '''send text to fpaste.org and return the URL'''
    import re
    if not text:
        print >> sys.stderr, "No text to send."
        return [False, False]

    # if sent data exceeds maxlength, server dies without error returned, so, we'll truncate the input here,
    # until the server decides to truncate instead of die
    author = options.nick
    if len(author) > 50:
        author = author[0:50 - 3] + "..."

    params = urllib.urlencode({'paste_lang': options.lang, 'paste_data': text,
                               'paste_private': options.make_private,
                               'paste_expire': options.expires,
                               'paste_password': options.password,
                               'paste_user': author,
                               'api_submit': 'true', 'mode': 'json'})
    pasteSizeKiB = len(params) / 1024.0

    # 512KiB appears to be the current hard limit (20110404); old limit was
    # 16MiB
    if pasteSizeKiB >= 512:
        print >> sys.stderr, "WARNING: your paste size (%.1fKiB) is very large and may be rejected by the server. A pastebin is NOT a file hosting service!" % (
            pasteSizeKiB)
    # verify that it's most likely *non-binary* data being sent.
    if not is_text(text):
        print >> sys.stderr, "WARNING: your paste looks a lot like binary data instead of text."
        if not confirm("Send binary data anyway?"):
            return [False, False]

    req = urllib2.Request(url=options.url, data=params,
                          headers={'User-agent': USER_AGENT})
    if options.proxy:
        if options.debug:
            print >> sys.stderr, "Using proxy: %s" % options.proxy
        req.set_proxy(options.proxy, 'http')

    print >> sys.stderr, "Uploading (%.1fKiB)..." % pasteSizeKiB

    try:
        f = urllib2.urlopen(req)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, "Error Uploading: %s" % e.reason
        elif hasattr(e, 'code'):
            print >> sys.stderr, "Server Error: %d - %s" % (e.code, e.msg)
            if options.debug:
                print f.read()
        return [False, False]

    try:
        response = json.loads(f.read())
    except ValueError, e:
        print >> sys.stderr, "Error: Server did not return a correct JSON response"
        return [False, False]

    if 'error' in response['result']:
        error = response['result']['error']
        if error == 'err_spamguard_php':
            print >> sys.stderr, "Error: Poster's IP address is listed as malicious"
        elif error == 'err_spamguard_noflood':
            print >> sys.stderr, "Error: Poster is trying to flood"
        elif error == 'err_spamguard_stealth':
            print >> sys.stderr, "Error: The paste triggered the spam filter"
        elif error == 'err_spamguard_ipban':
            print >> sys.stderr, "Error: Poster's IP address is banned"
        elif error == 'err_author_numeric':
            print >> sys.stderr, "Error: Poster's alias should be alphanumeric"
        else:
            print >> sys.stderr, "Error: %s" % error
        sys.exit(-1)

    id = [i[1]["id"] for i in response.iteritems()].pop()
#        for k,j in i.iteritems():
#            print j, k
    if options.make_private == 'yes':
        private_hash = [i[1]["hash"] for i in response.iteritems()].pop()
        url = "{0}{1}/{2}".format(options.url, id, private_hash)
    else:
        url = "{0}{1}".format(options.url, id)

    short_url = get_shortened_url(url, options.password)
    if short_url:
        return [url, short_url]
    else:
        return [url, False]

#    url = f.geturl()
#    if re.match(FPASTE_URL + '?.+', url):
#        return url
#    elif urllib2.urlparse.urlsplit(url).path == '/static/limit/':
#        # instead of returning a 500 server error, fpaste.org now returns "http://fedoraunity.org/static/limit/" if paste too large
#        print >> sys.stderr, "Error: paste size (%.1fKiB) exceeded server limit.  %s" % (pasteSizeKiB, url)
#        return False
#    else:
#        print >> sys.stderr, "Invalid URL '%s' returned. This should not happen. Use --debug to see server output" % url
#        if options.debug:
#            print f.read()
#        return False


def sysinfo(show_stderr=False, show_successful_cmds=True, show_failed_cmds=True):
    '''returns commonly requested (and some fedora-specific) system info'''
    # 'ps' output below has been anonymized: -n for uid vs username, and -c for short processname

    # cmd name, command, command2 fallback, command3 fallback, ...
    cmdlist = [
        ('OS Release',         '''lsb_release -ds''',
         '''cat /etc/*-release | uniq''', 'cat /etc/issue', 'cat /etc/motd'),
        ('Kernel',             '''uname -r ; cat /proc/cmdline'''),
        ('Desktop(s) Running', '''ps -eo comm= | grep -E '(gnome-session|startkde|startactive|xfce.?-session|fluxbox|blackbox|hackedbox|ratpoison|enlightenment|icewm-session|od-session|wmaker|wmx|openbox-lxde|openbox-gnome-session|openbox-kde-session|mwm|e16|fvwm|xmonad|sugar-session|mate-session|lxqt-session|cinnamon)' '''),
        ('Desktop(s) Installed', '''ls -m /usr/share/xsessions/ | sed 's/\.desktop//g' '''),
        ('SELinux Status',      '''sestatus''', '''/usr/sbin/sestatus''',
         '''getenforce''', '''grep -v '^#' /etc/sysconfig/selinux'''),
        ('SELinux Error Count',
         '''selinuxenabled && journalctl --since yesterday |grep avc: |grep -Eo "comm=\"[^ ]+" |sort |uniq -c |sort -rn'''),
        ('CPU Model',
         '''grep 'model name' /proc/cpuinfo | awk -F: '{print $2}' | uniq -c | sed -re 's/^ +//' ''', '''grep 'model name' /proc/cpuinfo'''),
        ('64-bit Support',     '''grep -q ' lm ' /proc/cpuinfo && echo Yes || echo No'''),
        ('Hardware Virtualization Support',
         '''grep -Eq '(vmx|svm)' /proc/cpuinfo && echo Yes || echo No'''),
        ('Load average',       '''uptime'''),
        ('Memory usage',       '''free -m''', 'free'),
        #('Top',                '''top -n1 -b | head -15'''),
        ('Top 5 CPU hogs',     '''ps axuScnh | awk '$2!=''' + \
         str(os.getpid()) + '''' | sort -rnk3 | head -5'''),
        ('Top 5 Memory hogs',  '''ps axuScnh | sort -rnk4 | head -5'''),
        ('Disk space usage',   '''df -hT''', 'df -h', 'df'),
        ('Block devices',      '''blkid''', '''/sbin/blkid'''),
        ('PCI devices',        '''lspci''', '''/sbin/lspci'''),
        ('USB devices',        '''lsusb''', '''/sbin/lsusb'''),
        ('DRM Information',
         '''journalctl -k -b | grep -o 'kernel:.*drm.*$' | cut -d ' ' -f 2- '''),
        ('Xorg modules',       '''grep LoadModule /var/log/Xorg.0.log ~/.local/share/xorg/Xorg.0.log | cut -d \\" -f 2 | xargs'''),
        ('GL Support',         '''glxinfo | grep -E "OpenGL version|OpenGL renderer"'''),
        ('Xorg errors',
         '''grep '^\[.*(EE)' /var/log/Xorg.0.log ~/.local/share/xorg/Xorg.0.log | cut -d ':' -f 2- '''),
        ('Kernel buffer tail', '''dmesg | tail'''),
        ('Last few reboots',   '''last -x -n10 reboot runlevel'''),
        ('DNF Repositories',   '''dnf -C repolist''',
         '''ls -l /etc/yum.repos.d''', '''grep -v '^#' /etc/yum.conf'''),
        ('DNF Extras',         '''dnf -C list extras'''),
        ('Last 20 packages installed', '''rpm -qa --nodigest --nosignature --last | head -20''')]
    #('Installed packages', '''rpm -qa --nodigest --nosignature | sort''', '''dpkg -l''') ]
    si = []

    print >> sys.stderr, "Gathering system info",
    for cmds in cmdlist:
        cmdname = cmds[0]
        cmd = ""
        for cmd in cmds[1:]:
            sys.stderr.write('.')  # simple progress feedback
            p = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            if p.returncode == 0 and out:
                break
            else:
                if show_stderr:
                    print >> sys.stderr, "sysinfo Error: the cmd \"%s\" returned %d with stderr: %s" % (
                        cmd, p.returncode, err)
                    print >> sys.stderr, "Trying next fallback cmd..."
        if out:
            if show_successful_cmds:
                si.append(('%s (%s)' % (cmdname, cmd), out))
            else:
                si.append(('%s' % cmdname, out))
        else:
            if show_failed_cmds:
                si.append(('%s (failed: "%s")' %
                           (cmdname, '" AND "'.join(cmds[1:])), out))
            else:
                si.append(('%s' % cmdname, out))

    # return in readable indented format
    sistr = "=== fpaste %s System Information (fpaste --sysinfo) ===\n" % VERSION
    for cmdname, output in si:
        sistr += "* %s:\n" % cmdname
        if not output:
            sistr += "     N/A\n\n"
        else:
            for line in output.split('\n'):
                sistr += "     %s\n" % line

    return sistr


def generate_man_page():
    '''TODO: generate man page from usage'''
    pass


def summarize_text(text):
    # use beginning/middle/end content snippets as a description summary. 120 char limit
    # "36chars ... 36chars ... 36chars" == 118 chars
    # TODO: nuking whitespace in huge text files might be expensive; optimize
    # for b/m/e segments only
    sniplen = 36
    seplen = len(" ... ")
    tsum = ""
    text = " ".join(text.split())   # nuke whitespace
    tlen = len(text)

    if tlen < sniplen + seplen:
        tsum += text
    if tlen >= sniplen + seplen:
        tsum += text[0:sniplen] + " ..."
    if tlen >= (sniplen * 2) + seplen:
        tsum += " " + text[tlen / 2 -
                           (sniplen / 2):(tlen / 2) + (sniplen / 2)] + " ..."
    if tlen >= (sniplen * 3) + (seplen * 2):
        tsum += " " + text[-sniplen:]
    #print >> sys.stderr, str(len(tsum)) + ": " + tsum

    return tsum


def main():
    validExpiresOpts = ['1800', '21600', '86400', '604800', '2592000']
    validSyntaxOpts = ["cpp",
                       "diff",
                       "gdb",
                       "javascript",
                       "text",
                       "perl",
                       "php",
                       "python",
                       "ruby",
                       "xml",
                       "abap",
                       "6502acme",
                       "actionscript",
                       "actionscript3",
                       "ada",
                       "algol68",
                       "apache",
                       "applescript",
                       "apt_sources",
                       "asm",
                       "asp",
                       "autoconf",
                       "autohotkey",
                       "autoit",
                       "avisynth",
                       "awk",
                       "bash",
                       "basic4gl",
                       "bf",
                       "bibtex",
                       "blitzbasic",
                       "bnf",
                       "boo",
                       "c",
                       "c_loadrunner",
                       "c_mac",
                       "caddcl",
                       "cadlisp",
                       "cfdg",
                       "cfm",
                       "chaiscript",
                       "cil",
                       "clojure",
                       "cmake",
                       "cobol",
                       "cpp",
                       "cpp-qt",
                       "csharp",
                       "css",
                       "cuesheet",
                       "d",
                       "dcs",
                       "delphi",
                       "diff",
                       "div",
                       "dos",
                       "dot",
                       "e",
                       "ecmascript",
                       "eiffel",
                       "email",
                       "epc",
                       "erlang",
                       "f1",
                       "falcon",
                       "fo",
                       "fortran",
                       "freebasic",
                       "fsharp",
                       "4cs",
                       "gambas",
                       "gdb",
                       "genero",
                       "genie",
                       "gettext",
                       "glsl",
                       "gml",
                       "gnuplot",
                       "go",
                       "groovy",
                       "gwbasic",
                       "haskell",
                       "hicest",
                       "68000devpac",
                       "hq9plus",
                       "html4strict",
                       "icon",
                       "idl",
                       "ini",
                       "inno",
                       "intercal",
                       "io",
                       "j",
                       "java",
                       "java5",
                       "javascript",
                       "jquery",
                       "6502kickass",
                       "kixtart",
                       "klonec",
                       "klonecpp",
                       "latex",
                       "lb",
                       "lisp",
                       "locobasic",
                       "logtalk",
                       "lolcode",
                       "lotusformulas",
                       "lotusscript",
                       "lscript",
                       "lsl2",
                       "lua",
                       "m68k",
                       "magiksf",
                       "make",
                       "mapbasic",
                       "matlab",
                       "mirc",
                       "mmix",
                       "modula2",
                       "modula3",
                       "mpasm",
                       "mxml",
                       "mysql",
                       "newlisp",
                       "nsis",
                       "oberon2",
                       "objc",
                       "objeck",
                       "ocaml",
                       "ocaml-brief",
                       "oobas",
                       "oracle11",
                       "oracle8",
                       "oxygene",
                       "oz",
                       "pascal",
                       "pcre",
                       "per",
                       "perl",
                       "perl6",
                       "pf",
                       "php",
                       "php-brief",
                       "pic16",
                       "pike",
                       "pixelbender",
                       "plsql",
                       "postgresql",
                       "povray",
                       "powerbuilder",
                       "powershell",
                       "progress",
                       "prolog",
                       "properties",
                       "providex",
                       "purebasic",
                       "python",
                       "q",
                       "qbasic",
                       "rails",
                       "rebol",
                       "reg",
                       "robots",
                       "rpmspec",
                       "rsplus",
                       "ruby",
                       "sas",
                       "scala",
                       "scheme",
                       "scilab",
                       "sdlbasic",
                       "smalltalk",
                       "smarty",
                       "sql",
                       "systemverilog",
                       "6502tasm",
                       "tcl",
                       "teraterm",
                       "text",
                       "thinbasic",
                       "tsql",
                       "typoscript",
                       "unicon",
                       "vala",
                       "vb",
                       "vbnet",
                       "verilog",
                       "vhdl",
                       "vim",
                       "visualfoxpro",
                       "visualprolog",
                       "whitespace",
                       "whois",
                       "winbatch",
                       "xbasic",
                       "xml",
                       "xorg_conf",
                       "xpp",
                       "z80",
                       "zxbasic"]
    validClipboardSelectionOpts = ['primary', 'secondary', 'clipboard']
    validPrivateOpts = ['yes', 'no']
    ext2lang_map = {'sh': 'bash', 'bash': 'bash', 'bat': 'bat', 'c': 'c', 'h': 'c', 'cpp': 'cpp', 'css': 'css', 'html': 'html4strict', 'htm': 'html4strict', 'ini': 'ini', 'java': 'java', 'js': 'javascript',
                    'jsp': 'java', 'pl': 'perl', 'php': 'php', 'php3': 'php', 'py': 'python', 'rb': 'ruby', 'rhtml': 'html4strict', 'sql': 'sql', 'sqlite': 'sql', 'tcl': 'tcl', 'vim': 'vim', 'xml': 'xml'}

    usage = """\
Usage: %%prog [OPTION]... [FILE]...
  send text file(s), stdin, or clipboard to the %s pastebin and return the URL.

Examples:
  %%prog file1.txt file2.txt
  dmesg | %%prog
  (prog1; prog2; prog3) | fpaste
  %%prog --sysinfo -d "my laptop" --confirm
  %%prog -n codemonkey -d "problem with foo" -l python foo.py""" % FPASTE_URL

    parser = OptionParser(usage=usage, version='%prog ' + VERSION)
    parser.add_option('', '--debug', dest='debug',
                      help=SUPPRESS_HELP, action="store_true", default=False)
    parser.add_option('', '--proxy', dest='proxy', help=SUPPRESS_HELP)

    # pastebin-specific options first
    fpasteOrg_group = OptionGroup(parser, "fpaste.org Options")
    fpasteOrg_group.add_option(
        '-n', dest='nick', help='your nickname; default is "%default";', metavar='"NICKNAME"')
    fpasteOrg_group.add_option('-l', dest='lang', help='language of content for syntax highlighting; default is "%default"; use "list" to show all ' +
                               str(len(validSyntaxOpts)) + ' supported langs', metavar='"LANGUAGE"')
    fpasteOrg_group.add_option('-x', dest='expires', help='time before paste is removed; default is %default seconds; valid options: ' +
                               ', '.join(validExpiresOpts), metavar='EXPIRES')
    fpasteOrg_group.add_option('-P', '--private', help='make paste private; default is %default; valid options: ' +
                               ', '.join(validPrivateOpts), dest='make_private', metavar='"PRIVATE"')
    fpasteOrg_group.add_option(
        '-U', '--URL', help='URL of fpaste server; default is %default', dest='url', metavar='"FPASTE URL"')
    fpasteOrg_group.add_option(
        '-d', '--password', help='password for paste; default is %default', dest='password', metavar='"PASSWORD"')

    parser.add_option_group(fpasteOrg_group)
    # other options
    fpasteProg_group = OptionGroup(parser, "Input/Output Options")
    fpasteProg_group.add_option('-i', '--clipin', dest='clipin',
                                help='read paste text from current X clipboard selection [requires: xsel]', action="store_true", default=False)
    fpasteProg_group.add_option('-o', '--clipout', dest='clipout',
                                help='save returned paste URL to X clipboard', action="store_true", default=False)
    fpasteProg_group.add_option('', '--selection', dest='selection',
                                help='specify which X clipboard to use. valid options: "primary" (default; middle-mouse-button paste), "secondary" (uncommon), or "clipboard" (ctrl-v paste)', metavar='CLIP')
    fpasteProg_group.add_option('', '--fullpath', dest='fullpath',
                                help='use pathname VS basename for file description(s)', action="store_true", default=False)
    fpasteProg_group.add_option('', '--pasteself', dest='pasteself',
                                help='paste this script itself', action="store_true", default=False)
    fpasteProg_group.add_option('', '--sysinfo', dest='sysinfo',
                                help='paste system information', action="store_true", default=False)
    fpasteProg_group.add_option('', '--printonly', dest='printonly',
                                help='print paste, but do not send', action="store_true", default=False)
    fpasteProg_group.add_option('', '--confirm', dest='confirm',
                                help='print paste, and prompt for confirmation before sending', action="store_true", default=False)
    parser.add_option_group(fpasteProg_group)

# Let default be anonymous.
#    p = subprocess.Popen('whoami', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    (out, err) = p.communicate ()
#    if p.returncode == 0 and out:
#        user = out[0:-1]
#    else:
#        print >> sys.stderr, "WARNING Could not run whoami. Posting anonymously."

    parser.set_defaults(nick='', lang='text', make_private='yes',
                        expires='2592000', selection='primary', password='', url=FPASTE_URL)
    (options, args) = parser.parse_args()

    # Check for trailing slash
    if options.url[-1] != '/':
        options.url = options.url + '/'

    if options.lang.lower() == 'list':
        print 'Valid language syntax options:'
        for opt in validSyntaxOpts:
            print opt
        sys.exit(0)
    if options.clipin:
        if not os.access('/usr/bin/xsel', os.X_OK):
            # TODO: try falling back to xclip or dbus
            parser.error(
                'OOPS - the clipboard options currently depend on "/usr/bin/xsel", which does not appear to be installed')
    if options.clipin and args:
        parser.error(
            "Sending both clipboard contents AND files is not supported. Use -i OR filename(s)")
    for optk, optv, opts in [('language', options.lang, validSyntaxOpts), ('expires', options.expires, validExpiresOpts), ('clipboard selection', options.selection, validClipboardSelectionOpts)]:
        if optv not in opts:
            parser.error("'%s' is not a valid %s option.\n\tVALID OPTIONS: %s" % (
                optv, optk, ', '.join(opts)))

    fileargs = args
    if options.fullpath:
        fileargs = [os.path.abspath(x) for x in args]
    else:
        # remove potentially non-anonymous path info from file path
        # descriptions
        fileargs = [os.path.basename(x) for x in args]

    # guess lang for some common file extensions, if all file exts similar,
    # and lang not changed from default
    if options.lang == 'text':
        all_exts_similar = False
        for i in range(0, len(args)):
            all_exts_similar = True
            ext = os.path.splitext(args[i])[1].lstrip(os.extsep)
            if i > 0 and ext != ext_prev:
                all_exts_similar = False
                break
            ext_prev = ext
        if all_exts_similar and ext in ext2lang_map.keys():
            options.lang = ext2lang_map[ext]

    # get input from mutually exclusive sources, though they *could* be
    # combined
    text = ""
    if options.clipin:
        xselcmd = 'xsel -o --%s' % options.selection
        #text = os.popen(xselcmd).read()
        p = subprocess.Popen(xselcmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (text, err) = p.communicate()
        if p.returncode != 0:
            if options.debug:
                print >> sys.stderr, err
            parser.error(
                "'xsel' failure. this usually means you're not running X")
        if not text:
            parser.error("%s clipboard is empty" % options.selection)
    elif options.pasteself:
        text = open(sys.argv[0]).read()
        options.lang = 'python'
        options.nick = 'Fedora Unity'
    elif options.sysinfo:
        text = sysinfo(options.debug)
    elif not args:   # read from stdin if no file args supplied
        try:
            text += sys.stdin.read()
        except KeyboardInterrupt:
            print >> sys.stderr, "\nUSAGE REMINDER:\n   fpaste waits for input when run without file arguments.\n   Paste your text, then press <Ctrl-D> on a new line to upload.\n   Try `fpaste --help' for more information.\nExiting..."
            sys.exit(1)
    else:
        for i, f in enumerate(args):
            if not os.access(f, os.R_OK):
                parser.error("file '%s' is not readable" % f)
            if (len(args) > 1):     # separate multiple files with header
                text += '#' * 78 + '\n'
                text += '### file %d of %d: %s\n' % (
                    i + 1, len(args), fileargs[i])
                text += '#' * 78 + '\n'
            text += open(f).read()
    if options.debug:
        print 'nick: "%s"' % options.nick
        print 'lang: "%s"' % options.lang
        print 'text (%d): "%s ..."' % (len(text), text[:80])

    if options.printonly or options.confirm:
        try:
            if is_text(text):
                # when piped to less, sometimes fails with [Errno 32] Broken
                # pipe
                print text
            else:
                print "DATA"
        except IOError:
            pass
    if options.printonly:   # print only what would be sent, and exit
        sys.exit(0)
    elif options.confirm:   # print what would be sent, and ask for permission
        if not confirm("OK to send?"):
            sys.exit(1)

    [url, short_url] = paste(text, options)
    if url:
        # try to save URL in clipboard, and warn but don't error
        if options.clipout:
            if not os.access('/usr/bin/xsel', os.X_OK):
                print >> sys.stderr, 'OOPS - the clipboard options currently depend on "/usr/bin/xsel", which does not appear to be installed'
            else:
                xselcmd = 'xsel -i --%s' % options.selection
            #os.popen(xselcmd, 'wb').write(url)
                p = subprocess.Popen(xselcmd, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                (out, err) = p.communicate(input=url)
                if p.returncode != 0:
                    if options.debug:
                        print >> sys.stderr, err
                    print >> sys.stderr, "WARNING: URL not saved to clipboard"
                else:
                    print "URL copied to primary clipboard"

        if not short_url:
            print >> sys.stderr, "WARNING: Could not shorten URL"
            print url
        else:
            print short_url + " -> " + url

    else:
        sys.exit(1)

    if options.pasteself:
        print >> sys.stderr, "install fpaste to local ~/bin dir by running:    mkdir -p ~/bin; curl " + \
            url + "raw/ -o ~/bin/fpaste && chmod +x ~/bin/fpaste"

    if __name__ == '__main__':
        sys.exit(0)
    return short_url, url


if __name__ == '__main__':
    try:
        if '--generate-man' in sys.argv:
            generate_man_page()
        else:
            main()
    except KeyboardInterrupt:
        print "\ninterrupted."
        sys.exit(1)
