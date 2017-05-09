"""
Licensed Materials - Property of IBM
Framework Web Solutions Enabler - WebSphere aka WSE-W
(C) COPYRIGHT International Business Machines Corp., 2012
All Rights Reserved *

Introduction
------------
wsadminlib-wse is an library to be used in addition with the "standard wsadminlib".

At the top of your script, you should load wsadminlib-wse by using something like this:
execfile('wsadminlib-wse.py')

There's no need to code the load of wsadminlib - execfile('wsadminlib.py')
as it is done in this lib.

Note: when developing new methods herein, you can test them
quickly by starting wsadmin.sh -lang jython, and issuing
execfile('wsadminlib-wse.py') every time you save this file.
"""

execfile('wsadminlib.py')

##############################################################################
# Function added for WSE-W project - modify JVM ThreadPool value
#
def modifyApplicationServerThreadPool(nodename, servername, threadPoolName, min, max, timeout, isGrowable):
    """Modify Thread pool parameter of an application server."""
    server_id = getServerByNodeAndName( nodename, servername )
    tp = _splitlines(AdminConfig.list('ThreadPool', server_id))
    for tpname in tp:
       if tpname.startswith(threadPoolName + '(' ):
          tp_id = tpname[len(threadPoolName):]
          AdminConfig.modify(tp_id, '[[name %s] [minimumSize %s] [maximumSize %s] [inactivityTimeout %s] [description ""] [isGrowable %s]]' % (threadPoolName, min, max, timeout, isGrowable))
       
##############################################################################
# Function added for WSE-W project - modify Process Execution UMASK
#
def modifyProcessExecutionUmask(nodename, servername, umask):
    """Configure datasource JNDI name for persistence sessions database with multi row schema option."""
    server_id = getServerByNodeAndName( nodename, servername )
    proc_exec_id =  AdminConfig.list('ProcessExecution', server_id)
    AdminConfig.modify(proc_exec_id, '[[umask %s]]' % (umask))

##############################################################################
# Function added for WSE-W project - configure session management datasource
#
def configureSessionPersistence(nodename, servername, sessionDBJndiName, user_id, password):
    """Configure datasource JNDI name for persistence sessions database with multi row schema option."""
    server_id = getServerByNodeAndName( nodename, servername )
    session_manager = AdminConfig.list('SessionManager', server_id)
    tuning_params = AdminConfig.list('TuningParams', server_id)
    AdminConfig.modify(session_manager,'[[sessionPersistenceMode "DATABASE"]]')
    AdminConfig.modify(tuning_params,'[[usingMultiRowSchema "true"]]')
    session_db = AdminConfig.list('SessionDatabasePersistence',session_manager)
    AdminConfig.modify(session_db,'[[userId %s] [password %s] [datasourceJNDIName %s]]' % (user_id, password, sessionDBJndiName))

    m = "configureSessionPersistence:"
    sop(m, "AdminConfig.modify(datasourceJNDIName %s)" % (sessionDBJndiName))

##############################################################################
# Function added for WSE-W project - define cookie path
#
def setCookiePath(nodename, servername, cookieName, cookiePath):
    """Set cookie path for the application server."""
    server_id = getServerByNodeAndName( nodename, servername )
    cookie = AdminConfig.list('Cookie', server_id)

    AdminConfig.modify(cookie, '[[maximumAge "-1"] [name %s] [domain ""] [secure "true"] [path %s]]' % (cookieName, cookiePath))
    
    m = "setCookiePath:"
    sop(m, "AdminConfig.modify(%s)" % (cookiePath ))
