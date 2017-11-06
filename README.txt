Remcall
-------

Remcall (short for remote method calls) is a protocol for inter
process communication (IPC) between different programming languages
using object proxying as its primary method for information exchange.
Communication using remcall requires the upfront definition of a
schema (comprised of record and enum types and more importantly
interfaces with method signatures) which then depending on the
programming language is compiled or interpreted. Both communication
participants are then free to implement any or none of the interfaces
and reference concrete objects to the other side which will be
represented using proxy objects. There is a certain distinction
between a server (waiting for connections, serving and entry point)
and a client (initiating a connection, performing the first method
call) in remcall, but the protocol allows for method calls and object
proxying in both directions. Remcall employs a binary representation
for both, its schema and its communication protocol. Communcation can
be layered on top of any bidirectional streams supporting binary data
such as TCP sockets, stdin/out, websockets.
