
# Strack - Dynamic program analysis

**Experimental**

_This program is licensed to you under the terms of the GNU General Public License version 3_



## Installation

FwdProxy requires : python 2.7 and strace

On Debian/Ubuntu :

    sudo apt-get install strace
    git clone https://github.com/danielrocher/strack.git
    cd strack
    sudo make install




## Usage

    ./strack.py --help
    usage: strack.py [-h] [-v] [-p PROFIL_FILENAME] [-a] [-d] [-l LEVELDEBUG]
                     TRACE
    
    positional arguments:
      TRACE                 A Pid number (ex. 545) OR PidName (ex. sshd) OR start
                            program to trace (ex. /usr/sbin/sshd)
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show version
      -p PROFIL_FILENAME, --profile PROFIL_FILENAME
                            profile file
      -a, --addrules        add new rules in profile file
      -d, --debug           Debug
      -l LEVELDEBUG, --leveldebug LEVELDEBUG
                            level for debug


## Uninstall

    sudo make uninstall


**TODO WRITE ME**