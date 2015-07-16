#DHT-Demo

A demo program for Distributed Hash Table, implemented Chord protocol in Python.

##Environment

You'll need *twisted* installed as a development dependency. See [twisted website](http://twistedmatrix.com/trac/) for help.

##Running

At first, an initial node must be started by using -i or -initial argument. Then you can add other nodes.

###instruction:

    python chord.py -i <nickname> [-s scale] [-IP ip] [-p port]
    python chord.py <nickname> [-IP ip] [-p port]

###notice:

1. Nicknames must be unique.
2. The initial node's address must be 'localhost', 8000.

##GUI

There's a GUI for a more convenient way to send and demonstrate query. You can run draw.py to start the GUI before node's start and it will listen to port 9000.

If you want to send a query through a node, just click the node and then input your query string. When finished, target node and a path the query went through these nodes will be displayed.

If there're too many lines on screen, you can enter space to redraw.

##Test Example

Using 3 console windows, run in each one:
	python Draw.py
	python Chord.py -i nodeA -s 10 --IP 127.0.0.1 -p 8470
	python Chord.py nodeB --IP 127.0.0.1 -p 8471

##Feedback

Any questions, feel free to contact us.

* email: `elderry@outlook.com` `zy3861@163.com`
