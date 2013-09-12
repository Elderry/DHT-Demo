dht-demo
========

A demo program for Distributed Hash Table

##About

It's a basic simulated implementation of the Chord protocol in Python.

##Usage

You'll need *twisted* installed as a development dependency. See [twisted website](http://twistedmatrix.com/trac/) for help with that.

###Running a node

At first, an initial node must be started by using -i or -initial argument.Then you can add other nodes.

**instruction:**  

    python chord.py -i nickname [-s scale] [-IP ip] [-p port]
    python chord.py nickname [-IP ip] [-p port]

###GUI

There's a GUI for a more convenient way to send and demonstrate query. You can run draw.py to start the GUI before node's start and it will listen to the port 9000.

If you want to send a query through a node, just click the node and then input your query string. When finished, target node and a path the query went through these nodes will be displayed.

If there's too many lines on the screen, you can enter space key to redraw the screen.

##Feedback

If there's some questions, feel free to contact us.

* email: `elderry@outlook.com` `zy3861@163.com`
