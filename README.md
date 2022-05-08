# DecisionProv

This repository was created for the part II Computer Science Tripos Dissertation at the University of Cambridge. The goal is to create records in the PROV format to record the reasons for actions in a smart home.

It consists of some python scripts, which can be run upon downloading the code and creating an OpenHab setup (https://www.openhab.org). 

The provenance monitor requires a ProvRuleNotification item to be created inside OpenHab, which is sent the name of the rule upon a rule firing.

The provenance reconstructor needs to be fed the events.log file from the OpenHab logs (put it in data/events.log) and it will produce a provenance database over the events which can be sent to a Neo4J database.
