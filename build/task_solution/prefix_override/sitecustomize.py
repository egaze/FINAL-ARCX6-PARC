import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jachin/FINAL-ARCX6-PARC/install/task_solution'
