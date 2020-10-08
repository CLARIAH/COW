# notes on performance by @melvin

So upon this initial analysis it seems hard to make major improvements for CoW. I think the speedup gains that I saw are in the range of 25% to 75% faster (e.g. instead of 5000 lines taking 35 seconds, I think it's possible to get that to 25 seconds). Though, it's still a guess whether it's actually possible, but it seems quite promising that it's possible. (edited) 

Another thing I found is that if you give it twice as much input, then it takes twice as long to complete. This shows that there are no big performance bugs in CoW

The bulk of the performance happens in the process function, so that's the place to look for optimization

25% to 50% of the full performance seems to be fully there because of Jinja and IRIBaker
For example, if get_property_url (that uses a lot of Jinja and IRIBaker) returns something simple, the time drops from 35 seconds on the file that I'm testing to 23 seconds (edited) 



# Practical recommendation
A practical performance tip that I found is the following though:
Find out how many threads you have on your computer (I use htop , you can get it by doing `sudo apt-get install htop`)
And then run CoW with one process less than you have threads. Example: I have 12 threads, so I run CoW with 11 --processes

So I run CoW with: 

`python3 ../cow/src/csvw_tool.py convert openarch_persons_deaths_v2.csv --processes 11`

A rule of thumb is that 5000 rows takes about 40 seconds

`wc -l openarch_persons_deaths_v2.csv gives 36054733 rows`

So that should take (with 11 --processes)

`> ((36054733 / (11 * 5000) ) * 40) / 3600`

`[1] 7.283784`
about 7+ hours

# Advanced
found one performance improvement:
1m4,328s vs 2m19,058s

Use this Python interpreter instead of the normal one: https://www.pypy.org/
pypy.orgpypy.org
PyPy
A fast, compliant alternative implementation of Python Download PyPy What is PyPy ? Documentation (external link) On average, PyPy is 4.2 times faster than CPython PyPy trunk (with JIT)

Here's what I did (you probably need to adapt it a bit)
# Download it 
https://www.pypy.org/download.html
# Extract it
`/home/melvin/Downloads/pypy3.7-v7.3.2-linux64/bin/pypy3 -m ensurepip`

`~/Downloads/pypy3.7-v7.3.2-linux64/bin/pypy3 -mpip install -r requirements.txt`

#Convert 

`~/Downloads/pypy3.7-v7.3.2-linux64/bin/pypy3.7 ~/clariah/cow/src/csvw_tool.py convert ~/clariah/examples/deaths_50000.csv`
