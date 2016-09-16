# YOLOFuzZ
I had an idea and I've decided to seriously work on it in my spare time. https://pastebinthehacker.blogspot.com.au/2016/09/yolofuzz.html

Idea: A fuzzer that flips jmp instructions

Why?
Instead of working really hard to find input that covers the code base, just force it to get run.

Won't that just crash shit constantly?
Probably.
I'm hoping I can triage crashes and progress in a way that makes it useful.
Later plans include automagic analysis.



Goals/Milestones/Plans:

- Plan the architechure. Try some ideas. fuck shit up (done)
- get something that flips jumps (done)
- sort out all the config shit (done)
- smooth out the user interaction bit (meh, configs are pretty fun)

- Add analysis
	- make a graph of the program using the jmps

- add the option to get dropped into a gdb session on crash
- add ban list for specific jmps