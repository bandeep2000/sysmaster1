
#!/usr/bin/env python

import time

date_time = '2007-02-05 16:15:18'
pattern = '%Y-%m-%d %H:%M:%S'
epoch = int(time.mktime(time.strptime(date_time, pattern)))
print epoch 
