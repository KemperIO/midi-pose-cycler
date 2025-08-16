# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

# Simplified version for bundled mido - removed packaging dependency
__version__ = "1.3.0"

class SimpleVersion:
    """Simple version object to replace packaging.version.Version"""
    def __init__(self, version_string):
        self.version_string = version_string
        parts = version_string.split('.')
        self.major = int(parts[0]) if len(parts) > 0 else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.micro = int(parts[2]) if len(parts) > 2 else 0
    
    def __str__(self):
        return self.version_string
    
    def __repr__(self):
        return f"SimpleVersion('{self.version_string}')"

version_info = SimpleVersion(__version__)