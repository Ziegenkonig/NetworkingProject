I included the old readme in here cause im to lazy to write up install instructions again.

Basically, the only thing that changed in this project is:
1) New Picture
2) 'New' Readme
3) New python program in Core Project/ServerSpace named SelectiveRepeatServer
4) New python program in Core Project/ClientSpace named SelectiveRepeatClient
5) Renamed alternating bit client to AlternatingBitClient
6) Renamed alternating bit client to AlternatingBitServer

INSTALL instructions are the same, except you can use gitbash for this, and it works fully
this time*



*NOTE that I ran into an small error while implementing this, where once you get to the 256th
packet, it errors. This is because I have the message for the packet being encoded into
bytes, and I don't know what else to use because whenever I change it, it ends up being
way to big for the receiving window. HOWEVER, I think you will see that I have successfully
implemented SelectiveRepeat, and a ton of Moby Dick downloads this time.