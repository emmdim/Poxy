This directory is now under version control and still has my own projects.

### Description

This application acts kind of like a proxy. It assumes that there is a local
dumb POX controller and a remote actual generic Openflow controller that
does all the smart stuff. The app's job is to register the switch in both 
controllers but use the local one actually only to simulate that is connected
to the controller. The remote one will contain the actual controller logic
(for example another POX app).

The main files are:

* events.py: Contains the new events created.

* async.py: Kind of a socket wrapper for writing to a socket and asynchronous
          reading

* proxy.py: The module that contains most of the logic. Lies in the middle of
          the asynchornous connection object of async.py and the basic POX 
          functionality.

* myof\_01.py: A copy of the switch hanlder of pox of\_01.py which starts also the
            proxy


### Branch Specific

In this branch (confine) the user declares the address of his switch
(each user has one switch) along with the remote controller.
Thus separate switches can be connected to separate controllers.


The user should be added before the switch is brought up.


### Execution

Start with debug on and connect to the central controler listening to the 
`IP: RADRRESS (string, default = "127.0.0.1")`
`PORT: RPORT (int, default = 6634 )`

It is also necessary to declare the MAC address of the first user.
For example
`MAC: switch_mac="00:00:00:00:00:00"`

Another possible option defines the maximum number of users that are going
to use the system. By deafualt it is 5. The option is

`max_users=5`

Example:
    
    ../.pox.py log.level --DEBUG py myof_01 --switch_mac="00:00:00:00:00:00" 
	[--rport=RPORT] [--raddress=RADRRESS] --max_users=10
	

### Interactive shell

The py instruction runs an interactive python CLI. Thus if the we want to add new
users later it can be done using the following commands:

    POX>from myof_01 import *
    POX>addUser("00:00:00:00:00:00")

Optionally the user can a specific destination other than the default (which is 
as previsiously)
    
    POX>addUser("00:00:00:00:00:00","127.0.0.2",6633)

Additionally you can list the existing users and their info with the following
command:

    POX>showUsers()