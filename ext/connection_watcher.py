from pox.core import core
from pox.lib.util import dpid_to_str
 
log = core.getLogger()
  
class MyComponent (object):
    def __init__ (self):
        core.openflow.addListeners(self)
                 
    def _handle_ConnectionUp (self, event):
        log.debug("Switch %s has come up.", dpid_to_str(event.dpid))
    
    def _handle_ConnectionDown (self, event):
        log.debug("Switch %s has gone down.", dpid_to_str(event.dpid))

                            
def launch ():
        log.debug("Launching my component")
        core.registerNew(MyComponent)
