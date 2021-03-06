# Copyright 2015 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

'''
Separates out the core asm module out of an emscripten output file.

This is useful because it lets you load the asm module first, then the main script, which on some browsers uses less memory
'''

import os, sys

sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import asm_module

infile = sys.argv[1]
asmfile = sys.argv[2]
otherfile = sys.argv[3]

everything = open(infile).read()
module = asm_module.AsmModule(infile).asm_js

module = module[module.find('=')+1:] # strip the initial "var asm =" bit, leave just the raw module as a function
if 'var Module' in everything:
  everything = everything.replace(module, 'Module["asm"]')
else:
  # closure compiler removes |var Module|, we need to find the closured name
  # seek a pattern like (e.ENVIRONMENT), which is in the shell.js if-cascade for the ENVIRONMENT override
  import re
  m = re.search(r'\((\w+)\.ENVIRONMENT\)', everything)
  if not m:
    m = re.search(r'(\w+)\.arguments\s*=\s*\[\];', everything)
  assert m, 'cannot figure out the closured name of Module statically'
  closured_name = m.group(1)
  everything = everything.replace(module, closured_name + '["asm"]')

o = open(asmfile, 'w')
o.write('Module["asm"] = ')
o.write(module)
o.write(';')
o.close()

o = open(otherfile, 'w')
o.write(everything)
o.close()

