import sys
import os
import re
import sre
import string
import random
import time
import socket
from java.util import StringTokenizer
from java.io import *
from java.lang import Integer
from java.lang import String

'''
createCoreGroup
createDynamicCluster

'''
def _listWebServers():
	result = []
	nodes = AdminTask.listNodes().splitlines()
	for node in nodes:
		webservers = AdminTask.listServers('[-serverType WEB_SERVER -nodeName ' + node + ']').splitlines()
		for webserver in webservers:
			result.append(AdminConfig.showAttribute(webserver, 'name'))
	return result	

def _nodeList():
	nodes = AdminConfig.list("Node").splitlines()
	result = []
	for node in nodes:
		result.append(AdminConfig.showAttribute(node,"name"))
	return result

def _getNodeNames():
	nodes = AdminConfig.list("Node").splitlines()
	result = []
	for node in nodes:
		if re.search("nodeagent" , ''.join(AdminConfig.list("Server",node).splitlines())):
			result.append(AdminConfig.showAttribute(node,"name"))
	return result

def _manipulate_string (new_node, node):
	ln=len(new_node)
	new_ln = ln -2
	new_node_prefix = new_node[:-2]
	new_node_postfix = new_node[new_ln:]
	new_node_postfix = string.atoi(new_node_postfix)     
	while new_node in node:
		new_node_postfix = new_node_postfix + 1   
		if new_node_postfix < 10:
			new_node=new_node_prefix+str(0)+str(new_node_postfix)
		else:
			new_node=new_node_prefix +str(new_node_postfix)
	return new_node

def _random_wait():
    period = 0
    for i in range(0, 3):
		period = period + random.randrange(0, 101, 2)
    period = (period )/2
    print "This is waiting for a period of %d seconds" %(period)
    time.sleep(period)

###  renameNode #### 	
def renameNode(new_node_name):
	print "renameNode.py"
	first_val=new_node_name
	_random_wait()

	node_List = _getNodeNames()
	new_node_name = _manipulate_string (new_node_name, node_List)

	while new_node_name.startswith("CloudBurstNode"):
		_random_wait()
		node_List = _getNodeNames()
		new_node_name = _manipulate_string (first_val, node_List)

	print "new_node_name @", new_node_name

###  renameCell #### 
def renameCell (new_cell_name, new_node_name, old_node_name):
	print "renameCell.py"
	try:
		hostname      = socket.gethostname()
		print ""
		print "------------------------------------------------"
		print " Changing Cell Name to : " +new_cell_name
		print "------------------------------------------------"
		print ""
		AdminTask.renameCell(['-newCellName ' '"'+new_cell_name+'"'+' -regenCerts true '+ '-nodeName '+'"'+old_node_name+'"' +' -hostName ' '"'+hostname+'"'])
		print "Saving New cell information..."
		AdminConfig.save()
		AdminTask.renameNode(['-nodeName ' '"'+old_node_name+'"'+ ' -newNodeName ' '"'+new_node_name+'"'])
		print "Saving New Node information..."
		AdminConfig.save()
	except Exception, e:
		print "Exception Occurred -", str(e)


###  getNodeIHS #### 
def getNodeIHS(nodeName, memberName):	
	print "getNodeIHS.py"
	_random_wait()

	node_List = _nodeList()
	listWebServers_l = _listWebServers()
	nodeName 	=  _manipulate_string (nodeName, node_List)
	memberName	=  _manipulate_string (memberName, listWebServers_l)

	print "nodeName @", nodeName 
	print "memberName @", memberName 

###  createIHS ####
def createIHS (nodeName, memberName, hostName, adminUserID, adminPasswd):
	print "createIHS.py"
	IHS_port="80"
	IHS_Install_root="/opt/IBM/WebSphere/HTTPServer"
	dmgr_config ="/opt/IBM/WebSphere/Profiles/DefaultDmgr01/config"
	IHS_Plugin_Path="/opt/IBM/WebSphere/Plugins"
	IHS_Config_Path="/opt/IBM/WebSphere/HTTPServer/conf/httpd.conf"
	IHS_WindowsServiceName=""
	IHS_ErrorLog_Path="" #"/opt/IBM/HTTPServer/logs/error_log"
	IHS_AccessLog_Path="" #"/opt/IBM/HTTPServer/logs/access_log"
	IHS_WebProtocol="HTTP"

	_random_wait()

	node_List = _nodeList()
	listWebServers_l = _listWebServers()
	nodeName 	=  _manipulate_string (nodeName, node_List)
	memberName	=  _manipulate_string (memberName, listWebServers_l)

	print "nodeName: ", nodeName
	print "memberName:", memberName
	print "listWebServers_l", listWebServers_l

	try:
		AdminTask.createUnmanagedNode('[-nodeName ' +nodeName +' -hostName ' +hostName +' -nodeOperatingSystem linux]')
	except:
		print "Already exists"

	print "Saving config..."
	AdminConfig.save( )

	try:
		AdminTask.createWebServer(nodeName, '[-name '+ memberName+ ' -templateName IHS -serverConfig [-webPort ' + IHS_port + ' -serviceName -webInstallRoot ' + IHS_Install_root + ' -webProtocol HTTP -configurationFile -errorLogfile -accessLogfile -pluginInstallRoot '+ IHS_Plugin_Path + ' -webAppMapping ALL] -remoteServerConfig [-adminPort 8008 -adminUserID ' + adminUserID +' -adminPasswd  '+ adminPasswd + ' -adminProtocol HTTP]]')

	except:
		print "Member Already Exists"

	print ""
	print "Saving config..."
	AdminConfig.save( )

###  bluepages ####
def bluepages(cell, node, scopeName):
	print "bluepages.py"
	AdminTask.retrieveSignerInfoFromPort('[-host bluepages.ibm.com -port 636 -sslConfigName NodeDefaultSSLSettings -sslConfigScopeName (cell):'+cell+':(node):'+node+' ]')

	if scopeName=='default':
		AdminTask.retrieveSignerFromPort('[-keyStoreName NodeDefaultTrustStore -keyStoreScope (cell):'+cell+':(node):'+node+' -host bluepages.ibm.com -port 636 -certificateAlias bluepages -sslConfigName NodeDefaultSSLSettings -sslConfigScopeName (cell):'+cell+':(node):'+node+']')

	if scopeName=='dmgr':
		AdminTask.retrieveSignerFromPort('[-keyStoreName CellDefaultTrustStore -keyStoreScope (cell):'+cell+' -host bluepages.ibm.com -port 636 -certificateAlias bluepages -sslConfigName CellDefaultSSLSettings -sslConfigScopeName (cell):'+cell+']')

	AdminConfig.save()

def createJMS (Factory_Name,JNDI_Name,QMGR_NAME,QMGR_HOST_NAME,QMGR_PORT_NUMBER,QMGR_CHANNEL_NAME,cluster_Name):
	print "createJMS.py"
	try:
		mq_queue_manager_name = QMGR_NAME
		mq_host_name = QMGR_HOST_NAME	
		mq_channel_port = QMGR_PORT_NUMBER
		mq_channel_name = QMGR_CHANNEL_NAME
		cluster_Name = cluster_Name.replace('\n', '')
		
		#Factory_Name, Factory_Type, JNDI_Name, QMGR_NAME, QMGR_HOST_NAME, QMGR_PORT_NUMBER, QMGR_CHANNEL_NAME, cluster_scope

		# Create JMS Resources
		# Create Queue Connection Factory
		# ClusterName = AdminConfig.getid("/ServerCluster:/").split('(')[0]
		print ""
		print "------------------------------------------------"
		print " Configuring JMS Resources"
		print " Queue Manager Name: " + mq_queue_manager_name
		print " Queue Manager Host: " + mq_host_name
		print " Queue Manager Port: " + mq_channel_port
		print " Queue Manager Channel Name: " + mq_channel_name
		print " Cluster Name	: " + mq_channel_name
		print "------------------------------------------------"

		#cluster_scope = AdminConfig.getid('/ServerCluster:' + AdminConfig.getid("/ServerCluster:/").split('(')[0])
		cluster_scope=AdminConfig.getid("/ServerCluster:" + cluster_Name + "/")
		print "cluster_scope:   " + cluster_scope
		# Here we are only using WMQ as queue connection factory, it can be extended to leverage on JMS features
		Factory_Type="QCF"
		createWMQConnectionFactory(Factory_Name, Factory_Type, JNDI_Name, QMGR_NAME, QMGR_HOST_NAME, QMGR_PORT_NUMBER, QMGR_CHANNEL_NAME, cluster_scope)

		# Create the Queue Connection Factory

		print ""
		print "------------------------------------------------"
		print " JMS Resource Configuration Completed!!!"
		print "------------------------------------------------"
		print ""
		AdminConfig.save()
	except Exception, e:
		print "wow i am here with exception in progm -", e


weight ="2"

def _idToName(nameList):
	nameLists = []
	nameLists=re.split('\(',nameList)
	return nameLists[0]
	
def _createCluster(clusterName, nodeName, namePrefix, weight, app,  serverMember):

   cellName = AdminControl.getCell()
   cell = AdminConfig.getid("/Cell:" + cellName + "/")
 
   #---------------------------------------------------------
   # Construct the attribute list to be used in creating a ServerCluster 
   # attribute.      
   #---------------------------------------------------------
   nameAttr = ["name", clusterName]
   descAttr = ["description", ""]
   prefAttr = ["preferLocal", "true"]
   stateAttr = ["stateManagement", [["initialState", "STOP"]]]
   attrs = []
   attrs.append(nameAttr)
   attrs.append(descAttr)
   attrs.append(prefAttr)
   attrs.append(stateAttr)
  
   #---------------------------------------------------------
   # Create the server cluster 
   #---------------------------------------------------------
   
   try:
	cluster = AdminConfig.create("ServerCluster", cell, attrs)
	
   except:
	cluster = AdminConfig.getid("/ServerCluster:" + clusterName + "/")
	

   #---------------------------------------------------------
   # Create the server Members
   #---------------------------------------------------------
   
   node = AdminConfig.getid("/Node:" + nodeName + "/")
   attrsMember = []
   nameAttr = ["memberName", serverMember]
   weightAttr = ["weight", weight]
   attrsMember = [["memberName", serverMember], ["weight", "2"]]
     
   try:
	print "cluster: %s" %(_idToName(cluster))
	print "node: %s" %(_idToName(node))
	print "attrsMember: %s" %(attrsMember)
	
	server = AdminConfig.createClusterMember(cluster, node, attrsMember)
	print "server: %s" %(_idToName(server))  
   except Exception, e:
	print 'Error occured while creating servers', e.value
   
   print "createCluster: saving config changes."
   AdminConfig.save()

def getNodeNames_old():
	nodes = AdminConfig.list("Node").splitlines()
	result = []
	for node in nodes:
		nodeName = AdminConfig.showAttribute(node,"name")
		servers = AdminConfig.list("Server",node).splitlines()
		value = ''.join(servers)
		if re.search("nodeagent" , value):
			result.append(nodeName)
	return result

def getNodeNames():
	nodes = AdminConfig.list("Node").splitlines()
	result = []
	for node in nodes:
		if re.search("nodeagent" , ''.join(AdminConfig.list("Server",node).splitlines())):
			result.append(AdminConfig.showAttribute(node,"name"))
	return result



def createCluster2(clusterName, nodeName, namePrefix, weight, app,  serverMember):
	try:
		clusterID=AdminConfig.getid("/ServerCluster:"+ clusterName +"/")
		if (len(clusterID) == 0): 
			nodeNames = getNodeNames()
			for nodeName in nodeNames: 
				_createCluster(clusterName, nodeName, "", int(weight), "", memberName)
				AdminTask.startMiddlewareServer('[-serverName %s -nodeName %s ]' % (clusterName, nodeName))
				startCluster(clusterName)		
	except Exception, e:
		print 'Error occured:', e.value

	print ""
	print "Saving config..."
	AdminConfig.save( )

def appStatusOnClusterMember ( clusterName, appName ):

	global AdminControl
	global AdminConfig

	clusterID=AdminConfig.getid("/ServerCluster:"+ clusterName +"/")

	if (len(clusterID) != 0):
		clusterObj = AdminControl.completeObjectName("type=Cluster,name="+clusterName+",*" )
		clusterStatus = AdminControl.getAttribute(clusterObj, "state" )
		print "cluster Status:", clusterStatus
		running = "websphere.cluster.running"
		partialstart = "websphere.cluster.partial.start"
		starting = "websphere.cluster.starting" 
		stopped = "websphere.cluster.stopped"
          
		statusCheck=0
		while ( statusCheck <= 3 and clusterStatus != running ):
			print "%s" % time.ctime()
			clusterStatus =  AdminControl.getAttribute(clusterObj, "state" )
			print "Cluster Status: " + clusterStatus;
			statusCheck += 1
			time.sleep(60) 
			if ( clusterStatus == stopped ):
				print "Cluster Status: ", clusterStatus, ", so ending the program"
				sys.exit(1)
			#Endif
		#EndWhile
	else:
		print "Error: ", clusterName, "does not exist. Please pass the right clusterName"
		sys.exit(1)
	#EndIf

	# List the servers in a cluster
	clusterList=AdminConfig.list('ClusterMember', clusterID)
	servers=clusterList.split("\n")

	for serverID in servers:
		serverName=AdminConfig.showAttribute(serverID, 'memberName')
		#  Prints Only Running Cluster Members
		aServer = AdminControl.completeObjectName("type=Server,name=" + serverName + ",*")
		if aServer == "":
			print "Server,", serverName, "is down. Please start the server."
			print ""
		else:
			aState=AdminControl.getAttribute(aServer, 'state')
			print "Server", serverName, "is in a", aState, "state"
			appStatus = AdminControl.queryNames("WebSphere:type=Application,name="+appName+",process="+serverName+",*")
			if appStatus == "":
				print "Application,", appName, "is not running on", serverName, "\n"
			else:
				print "Application,", appName, "is running on", serverName, "\n"
			#Endif
		#Endif
	#Endfor


def serverList():
	nodes = wsadminToList(AdminConfig.list("Node"))
	for node in nodes:
		nodeName = AdminConfig.showAttribute(node,"name")
		servers = wsadminToList(AdminConfig.list("Server",node))
		print "    server Name in the Node " + nodeName + " Are   "
		for server in servers:
			aServer = AdminConfig.showAttribute(server,"name")
			print "     Name        "   +    aServer      
	return aServer

def getNodeNames():
	nodes = wsadminToList(AdminConfig.list("Node"))
	result = []
	for node in nodes:
		nodeName = AdminConfig.showAttribute(node,"name")
		servers = wsadminToList(AdminConfig.list("Server",node))
		value = ''.join(servers)
		if re.search("nodeagent" , value):
			result.append(nodeName)
	return result	
	
def nodeList():
	nodes = wsadminToList(AdminConfig.list("Node"))
	for node in nodes:
		nodeName = AdminConfig.showAttribute(node,"name")
		print "    Node Name in the Cell Are        "
		print "    Node Name        "   +    nodeName
	return nodeName

def serverClusterList():
	"""Return list of names of server clusters"""
	cluster_ids = wsadminToList(AdminConfig.list( "ServerCluster" ))
	result = []
	for cluster_id in cluster_ids:
		result.append(AdminConfig.showAttribute(cluster_id,"name"))
	return result

def listWebServer():
	webServers = AdminTask.listServers('[-serverType WEB_SERVER ]')
	webServers = webServers.split("\n")
	serverList = []
	result = []
	for webServer in webServers:
	    serverList=re.split('[(]',webServer)
	    result.append(serverList[0])
	return result

def listUnmanagedNode():
	result = []
	nodes = AdminTask.listUnmanagedNodes()
	nodes = nodes.split("\n")
	for node in nodes:
		result.append(node)
	return result

def _splitlist(s):
	if s[0] != '[' or s[-1] != ']':
		raise "Invalid string: %s" % s
	return s[1:-1].split(' ')

def _splitlines(s):
	rv = [s]
	if '\r' in s:
		rv = s.split('\r\n')
	elif '\n' in s:
		rv = s.split('\n')
		if rv[-1] == '':
			rv = rv[:-1]
	return rv
	
def wsadminToList(inStr):
    outList=[]
    if (len(inStr)>0 and inStr[0]=='[' and inStr[-1]==']'):
        inStr = inStr[1:-1]
        tmpList = inStr.split(" ")
    else:
        tmpList = inStr.split("\n") #splits for Windows or Linux
    for item in tmpList:
        item = item.rstrip();       #removes any Windows "\r"
        if (len(item)>0):
           outList.append(item)
    return outList
#endDef	

def mapModulesToServers(listCluster):
	webServers = AdminTask.listServers('[-serverType WEB_SERVER ]')
	webServers = webServers.split("\n")
	cellName = AdminControl.getCell()
	pos1='.*'
	parms =""

	for webServer in webServers:
		serverList=re.split('[(/|]',webServer)
		parms += "WebSphere:cell=%s,node=%s,server=%s" %(serverList[2], serverList[4], serverList[6]) + '+'
	parms += 'WebSphere:cell=%s,cluster=%s' %(cellName, listCluster)
	return parms

def mapModulesToServersEx(listCluster):
	webServers = AdminTask.listServers('[-serverType WEB_SERVER ]')
	webServers = webServers.split("\n")
	cellName = AdminControl.getCell()
	pos1='.*'
	parms =""

	for webServer in webServers:
		serverList=re.split('[(/|]',webServer)
		parms += "WebSphere:cell=%s,node=%s,server=%s" %(serverList[2], serverList[4], serverList[6]) + '+'
	parms += 'WebSphere:cell=%s,cluster=%s' %(cellName, listCluster)
	return pos1 + ' ' + pos1 + ' ' + parms	

def updateMapModulesToServers():
	print "updateMapModulesToServers.py"
	try:
		_excp_ = 0
		listApps = wsadminToList(AdminApp.list())
		listClusters = serverClusterList()
		#listUnmanagedNodes = listUnmanagedNode()
		#listWebServers = listWebServer()
		cellName = AdminControl.getCell()
		
		for listCluster in listClusters:
			appName = AdminApp.list("WebSphere:cell="+cellName+",cluster="+listCluster+"")
			appName = appName.split("\n")
			for app in listApps:
				if app in appName:
					parms = mapModulesToServersEx(listCluster)
					AdminApp.edit(app, ['-MapModulesToServers', '[[ ' +parms+ ']]'])
					AdminConfig.save()
					
		print "Saving..."

	except:
		_type_, _value_, _tbck_ = sys.exc_info()
		error = `_value_`
		print "Error Installing Application"
		print "Error Message = "+error
	#endTry 	

global setJvmDisableJIT
def setJvmDisableJIT ( nodeName, serverName, disableJIT ):
	global AdminConfig, DEBUG_, INFO_
	aJvmID = getJvmID(nodeName, serverName)
	aJvmAttrs = [["disableJIT", disableJIT]]
	modifyJvmAttrs(aJvmID, aJvmAttrs)
#endDef

global setJvmDebugMode
def setJvmDebugMode ( nodeName, serverName, debugMode ):
	global AdminConfig, getJvmID, modifyJvmAttrs
	aJvmID = getJvmID(nodeName, serverName)
	aJvmAttrs = [["debugMode", debugMode]]
	modifyJvmAttrs(aJvmID, aJvmAttrs)
#endDef

global setJvmHeapSize
def setJvmHeapSize ( nodeName, serverName, initialHeap, maxHeap ):
	global AdminConfig
	aJvmID = getJvmID(nodeName, serverName)
	aJvmAttrs = [["initialHeapSize", initialHeap], ["maximumHeapSize", maxHeap]]
	modifyJvmAttrs(aJvmID, aJvmAttrs)
#endDef

################### Utility methods ###########################
global getJvmID
def getJvmID ( nodeName, serverName ):
	global AdminConfig
	aServerID = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/" )
	aJvmID = AdminConfig.list("JavaVirtualMachine", aServerID )
	return aJvmID
#endDef

global modifyJvmAttrs
def modifyJvmAttrs ( aJvmID, ajvmAttrs ):
	global AdminConfig, DEBUG_, INFO_
	aJvmSettings = AdminConfig.show(aJvmID )
	log(DEBUG_, "\nsetJVM initialJvmSettings: \n"+aJvmSettings )
	
	AdminConfig.modify(aJvmID, ajvmAttrs )
	aJvmSettings = AdminConfig.show(aJvmID )
	log(INFO_, "\nsetJVM changedJvmSettings: \n"+aJvmSettings )
#endDef

def _propagateKeyring(dmgr_path, cell, node, webServerName):
	objNameString = AdminControl.completeObjectName('WebSphere:name=PluginCfgGenerator,*')
	verb = 'propagateKeyring'
	args = '[' + dmgr_path + ' ' + cell + ' ' + node + ' ' + webServerName + ']'
	types = '[java.lang.String java.lang.String java.lang.String java.lang.String]'
	print AdminControl.invoke(objNameString,verb,args,types)
	
def propagateKeyring(dmgr_path):
	print "propagateKeyring.py"
	dmgr_path=dmgr_path+"/config"
	cell = AdminControl.getCell()
	nodes = AdminTask.listNodes().splitlines()

	for node in nodes:
		webservers = AdminTask.listServers('[-serverType WEB_SERVER -nodeName ' + node + ']').splitlines()
		for webserver in webservers:
			webserverName = AdminConfig.showAttribute(webserver, 'name')
			generator = AdminControl.completeObjectName('type=PluginCfgGenerator,*')
			print "Generating plugin-cfg.xml for " + webserverName + " on " + node
			result = AdminControl.invoke(generator, 'generate', dmgr_path + ' ' + cell + ' ' + node + ' ' + webserverName + ' false')
			print "Propagating plugin-cfg.xml for " + webserverName + " on " + node
			result = AdminControl.invoke(generator, 'propagate', dmgr_path + ' ' + cell + ' ' + node + ' ' + webserverName)
		AdminConfig.save()
		
		try:
			_propagateKeyring(dmgr_path, cell, node, webServerName)
			webserverCON = AdminControl.completeObjectName('type=WebServer,*')		
			print "Stopping " + webserverName + " on " + node
			AdminControl.invoke(webserverCON, 'stop', '[' + cell + ' ' + node + ' ' + webserverName + ']')
		except:
			print "error on stop " + e

		try:
			print "Starting " + webserverName + " on " + node
			result = AdminControl.invoke(webserverCON, 'start', '[' + cell + ' ' + node + ' ' + webserverName + ']')
		except:
			print "Error on start" + e

	AdminConfig.save()
		
def VariableSubstitutionEntry_wip( nodes,servers, symbolicName, value ):
	print "VariableSubstitutionEntry.py"
	cell = AdminControl.getCell()
	# Set a WAS variable to point to SharedLib
	print "Update the Variable Map"
	variableMap = AdminConfig.list("VariableMap").split();
	# Find the variable map for the server.
	for v in variableMap:
		if (v.find("/server") >= 0):
			variableMap = v
	print "Updating Variable Map: " + variableMap
	params = [];
	params.append(["symbolicName", symbolicName]);
	params.append(["value", value]);
	params.append(["description", "Root folder containing shared libs"]);
	AdminConfig.create("VariableSubstitutionEntry", variableMap, params);
	AdminConfig.save()
	AdminNodeManagement.syncActiveNodes()

def createWebsphereVariable_wip( nodes, symbolicName, value ):
	print "VariableSubstitutionEntry.py"
	cell = AdminControl.getCell()
	# Set a WAS variable to point to SharedLib
	print "Update the Variable Map"
	variableMap = AdminConfig.list("VariableMap").split();
	# Find the variable map for the server.
	for v in variableMap:
		if (v.find("/server") >= 0):
			variableMap = v
	print "Updating Variable Map: " + variableMap
	params = [];
	params.append(["symbolicName", symbolicName]);
	params.append(["value", value]);
	params.append(["description", "Root folder containing shared libs"]);
	#AdminConfig.create("VariableSubstitutionEntry", variableMap, params);
	AdminConfig.create('VariableSubstitutionEntry', '(cells/WTS_Cell01|variables.xml#VariableMap_1)', '[[symbolicName "UNIVERSAL_JDBC_DRIVER_PATH"] [description ""] [value "/opt/IBM/WebSphere/AppServer/universalDriver/lib"]]')
	AdminConfig.save()
	
#--------------------------------------------------------------------
# Procedure:	getConfigItemId
# Description:	Gets the Config Item Identifie
#
# Parameters:	scope
#			scopeName
#			nodeName    (only used for server scope)
#			objectType
#			item
#
# Returns:	ConfItemId
#--------------------------------------------------------------------
def getConfigItemId (scope, scopeName, nodeName, objectType, item):
	global AdminConfig

	scope = scope.title()
	if (scope == "Cell"):
		confItemId = AdminConfig.getid("/Cell:"+scopeName+"/"+objectType+":"+item)
	elif (scope == "Node"):
		confItemId = AdminConfig.getid("/Node:"+scopeName+"/"+objectType+":"+item)
	elif (scope == "Cluster"):
		confItemId = AdminConfig.getid("/ServerCluster:"+scopeName+"/"+objectType+":"+item)
	elif (scope == "Server"):
		confItemId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+scopeName+"/"+objectType+":"+item)
	#endIf
	return confItemId
#endDef

def getVirtualHostByName():
	"""Return the id of the named VirtualHost"""
	hosts = AdminConfig.list( 'VirtualHost' )
	hostlist = _splitlines(hosts)
	for host_id in hostlist:
		name = AdminConfig.showAttribute( host_id, "name" )
		if name == virtualhostname:
			return host_id
	return None

#******************************************************************************
# Procedure:   	createVirtualHost
# Description:	Create a new virtual host. If it already exists, modify it by
#			adding a host alias.
#****************************************************************************** 
def createVirtualHost_wip2 ( vhostName, dnsHost, port ):
	cellId = AdminConfig.list("Cell").split("\n")[0]
	cellName = getName (cellId)
	vhId = getConfigItemId("Cell", cellName, "", "VirtualHost", vhostName)
	if (len(vhId) == 0):
		# create virtual host
		try:
			_excp_ = 0
			vHost = AdminConfig.create( "VirtualHost", cellId, [["name", vhostName]] )
		except:
			_type_, _value_, _tbck_ = sys.exc_info()
			vHost = `_value_`
			_excp_ = 1
		#endTry 
		if (_excp_ ):
			print "Caught Exception creating virtual host"
			print vHost
			return
		#endIf 
	#endIf

	addHostAlias(vhostName, dnsHost, port)

#endDef

#--------------------------------------------------------------------
# Procedure:	addHostAlias
# Description:  	Adds host alias if it doesn't already exist
#
# Parameters:	hostName 	(eg: "default_host")
#			dnsHost 	(eg: "*")
#			port 		(eg: 9085)
#
# Returns:	None
#--------------------------------------------------------------------
def addHostAlias_wip ( hostName, dnsHost, port ):
	global AdminConfig, AdminControl
	port.replace('\n', '')
	hostTarget = findConfigTarget(hostName, "VirtualHost")
	if (hostTarget == 0):
		print "Can not find "+hostName
		return
      #endIf

	# determine whether alias exists
	oNeedToDefine = 1
	aliasList = AdminConfig.list("HostAlias", hostTarget).splitlines()
	if (aliasList != ['']):
		for HAEntry in aliasList:
			oHostName = AdminConfig.showAttribute(HAEntry, "hostname")
			oPort = AdminConfig.showAttribute(HAEntry, "port")
			if oHostName == dnsHost:
				if oPort == port:
					print "The hostname "+hostName+ " has already defined host alias: "+HAEntry
					print "New entry will not be added."
					oNeedToDefine = 0
					break 
 				#endIf 
			#endIf 
		#endFor 
	#endIf

	if (oNeedToDefine == 1):
		attrHA = [["hostname", dnsHost], ["port", port]]
		print "Adding Host Alias to "+hostName
		try:
			_excp_ = 0
			hAlias = AdminConfig.create( "HostAlias", hostTarget, attrHA )
		except:
			_type_, _value_, _tbck_ = sys.exc_info()
			hAlias = `_value_`
			_excp_ = 1
		#endTry 
		if (_excp_ ):
			print "Caught Exception creating host alias"
			print hAlias
			return
		#endIf 

	#endIf 
	return


#endDef 

#--------------------------------------------------------------------
# Procedure:	findConfigTarget
# Description: 	Determine if there is a config element for given
#			name and type
#
# Parameters:	nameSearch	 
#			type		(Cell, Node, JDBCProvider)
#
# Returns:	targetName = success 
#		0  = does not exist
#--------------------------------------------------------------------
def findConfigTarget ( nameSearch, type ):
	global AdminApp, AdminConfig

	elements = AdminConfig.list(type)
	if (elements == " "):
		return 0
	#endIf
	elementList = elements.splitlines()
	for element in elementList:
		element=element.rstrip()
		if (len(element) > 0 ):
			name=AdminConfig.showAttribute(element,"name")
			if (nameSearch == name):
				return element
			#endIf
		#endIf
	#endFo
	return 0	
#endDef 

#-----------------------------------------------------------------
# getName - Return the base name of the config object.
#-----------------------------------------------------------------

def createVirtualHost_wip (vhostName, port, dnsHost):
	print "createVirtualHost.py"
	try:
		portList = []
		portList=re.split('[-:*;$#%@]',port)
		
		vHost = AdminConfig.getid("/Deployment:"+vhostName+"/" )
		
		if (len(vHost) > 0):
			print "Virtual Host exist: Updating Aliases"
			addHostAlias(vhostName, dnsHost, portNumber)
			#endIf
		else:
			for item in portList:
				portNumber = item.rstrip()
				createVirtualHost ( vhostName, dnsHost, portNumber )
			#endFor
		
		print "Saving..."
		AdminConfig.save()
	except Exception, e:
		print "Exception occured -", e

def createProperty(nodeName, serverName, name, value):
	print "createProperty.py"
	#AdminConfig.create('Property', '(cells/SYM_Cell/nodes/SYM_Node01/servers/SCHEDSERVER01|server.xml#JavaVirtualMachine_1435204944246)', '[[validationExpression ""] [name "WRS_HOME_REPORT"] [description ""] [value "/birt/MRS"] [required "false"]]') 

	cell = AdminControl.getCell()
	node = nodeName

	server = AdminConfig.getid('/Cell:'+cell+'/Node:'+node+'/Server:'+servername+'/')
	jvm = AdminConfig.list('JavaVirtualMachine', server)
	 
	AdminConfig.create('Property', jvm, '[[validationExpression ""] [name "' + name + '"] [description ""] [value ' + value + '] [required "false"]]')

	#AdminConfig.save() 


	#AdminConfig.create('Property', '(cells/SYM_Cell/nodes/SYM_Node01/servers/EXESERVER01|server.xml#JavaVirtualMachine_1435293346266)', '[[validationExpression ""] [name "WRS_REPORT_DOCUMENT"] [description ""] [value "/rpt"] [required "false"]]') 
	
#--------------------------------------------------------------------]
#INSTALL Services APP
#---------------------------------------------------------------------
# Deployment options

nl = os.linesep  
#http://pic.dhe.ibm.com/infocenter/wasinfo/v8r0/index.jsp?topic=%2Fcom.ibm.websphere.express.doc%2Finfo%2Fexp%2Fae%2Frxml_taskoptions.html
#http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/index.jsp?topic=%2Fcom.ibm.websphere.express.doc%2Finfo%2Fexp%2Fae%2Frxml_7libapp.html
	#    appName         - application name
	#    earFileName     - earFileName file
	#    deployejb       - deploy ejb (true|false)
	#    deployws        - deploy webservices (true|false)
	#    defaultBindings - use default binding (true|false)
	#    earMetaData     - use MetaData from earFileName (true|false)
	#    dbType          - ejb deploy db type
	#    target[0]       - node name or cluster name
	#    target[1]       - server name

def createFile(fileName, user_string):
    my_file = open(fileName,'w') 
    my_file.write(user_string) 
    my_file.close()

def startApp(appname, clustername):
	cell = AdminControl.getCell( )
	cluster = AdminConfig.getid("/ServerCluster:"+clustername+"/" )
	memberlist = AdminConfig.showAttribute(cluster, "members" )
	members = memberlist.split(" ")
	for member in members:
		member = member.replace('[','' ).replace(']','')
		mname = AdminConfig.showAttribute(member, "memberName" )
		mnode = AdminConfig.showAttribute(member, "nodeName" )
		server = AdminControl.completeObjectName("cell="+cell+",node="+mnode+",name="+mname+",type=Server,*" )
		if (server != ""):
			status = AdminControl.getAttribute(server, "state" )
			if (status == "STARTED"):
				print ""
				print "Starting application "+appname+" on server "+mname+" and node "+mnode
				try:
					appManager = AdminControl.queryNames("cell="+cell+",node="+mnode+",type=ApplicationManager,process="+mname+",*" )
					AdminControl.invoke(appManager, "startApplication", appname )
					print "Application "+appname+" on server "+mname+" and node "+mnode+" started successfully"
				except:
					print "Error starting application "+appname+" on server "+mname+" and node "+mnode
			#endIf 
		#endIf 
	#endFor 

def configureRolesRestricted(fileName):
	value =''
	array =''
	try:
		f = open(fileName, 'r')
		value =  f.readlines()
		for elem in value:
			array += '[' + elem.replace(nl, '') + ' Yes No "" ""] '
	except:
		_type_, _value_, _tbck_ = sys.exc_info()
		error = `_value_`
		print "Error Message = "+error

	return array

def wsadminToList(inStr):
    outList=[]
    if (len(inStr)>0 and inStr[0]=='[' and inStr[-1]==']'):
        inStr = inStr[1:-1]
        tmpList = inStr.split(" ")
    else:
        tmpList = inStr.split(nl) #splits for Windows or Linux
    for item in tmpList:
        item = item.rstrip();       #removes any Windows "\r"
        if (len(item)>0):
           outList.append(item)
    return outList
#endDef	

def retrieveRoles(earFileName):
   ret = []
   taskInfo = AdminApp.taskInfo(earFileName, 'MapRolesToUsers')
   pos = taskInfo.find('Role:')
   while (pos != -1):
      pos += len('Role:')
      end = taskInfo.find(nl, pos)
      role = taskInfo[pos:end].strip()
      ret.append(role)
      pos = taskInfo.find('Role:', end)
   return ret

'''
def setSharedLibrary(nodeName, sharedLibDir, appName):
	global AdminConfig
	print 'setSharedLibrary:nodeName ' + nodeName
	cellName = AdminControl.getCell( )
	n1 = AdminConfig.getid("/Cell:" + cellName + "/Node:"+nodeName+"/");
	print 'setSharedLibrary:sharedLibDir ' + sharedLibDir
	library = AdminConfig.create('Library', n1, [['name','impactSharedLibrary'], 'classPath',sharedLibDir]]);
	print 'setSharedLibrary:appName ' + appName 
	deployment = AdminConfig.getid("/Deployment:" + appName);
	appDeploy = AdminConfig.showAttribute(deployment, 'deployedObject');
	classLoad1 = AdminConfig.showAttribute(appDeploy, 'classloader');
	AdminConfig.create('LibraryRef',classLoad1,[['libraryName','impactSharedLibrary']]);
	AdminConfig.save();
	print 'setSharedLibrary successful'
	return

	


AdminConfig.create('Library', node, [['name','test2'],['classPath',['C:/Program Files/JDBCDriver/test.jar']]])

AdminConfig.create('Library', AdminConfig.getid('/Cell:DmgrCell_9/ServerCluster:HVWebCluster_1/'), '[[nativePath ""] [name "IST_libraries2"] [isolatedClassLoader true] [description "IST Shared Libraries"] [classPath "/clrguivol/apps/enc/istgui/lib/hibernate-jpa-2.0-api-1.0.0.Final.jar;/clrguivol/apps/enc/istgui/lib/cglib-nodep-2.1_3.jar"]]')

sharedLibDir = sys.argv[2]
sharedLibDirEsc = '\"' + sharedLibDir + '\"'
setSharedLibrary(nodeName, sharedLibDirEsc, appName)   
'''

def setClassloaderToParentLast(appname):
    deployments = AdminConfig.getid("/Deployment:%s/" % (appname) )
    deploymentObject = AdminConfig.showAttribute(deployments, "deployedObject")
    AdminConfig.modify(deploymentObject, [['warClassLoaderPolicy', 'SINGLE']])
    classloader = AdminConfig.showAttribute(deploymentObject, "classloader")
    AdminConfig.modify(classloader, [['mode', 'PARENT_LAST']])
    modules = AdminConfig.showAttribute(deploymentObject, "modules")
    arrayModules = modules[1:len(modules)-1].split(" ")
    for module in arrayModules:
        if module.find('WebModuleDeployment') != -1:
            AdminConfig.modify(module, [['classloaderMode', 'PARENT_LAST']])	

def installApps(appName, earFileName, ClusterName, virtualHostName, installType):
	print "installApps.py"
	deployejb = "false"
	deployws = "false"
	defaultBindings = "true"
	earMetaData = "false"
	dbType = "DB2UDB_V82"
	target = [ClusterName]
	try:
		_excp_ = 0
		#listApp = wsadminToList(AdminApp.list())
		# this is a new function, needs to be tested before rolling out as an official version
		applications = AdminApp.list()
		listApp = applications.split(nl)
		
		if (len(listApp) > 0):
			for app in listApp:
				if app == appName:
					now = '.'+str(time.strftime( '%Y-%m-%d_%H_%M_%S', time.localtime() ))
					AdminApp.export(appName, earFileName+now)
					AdminApplication.uninstallApplication(appName)
					AdminConfig.save()
					
		error = installApp ( appName, earFileName, deployejb, deployws, defaultBindings, earMetaData, dbType, target, virtualHostName)
		AdminConfig.save()
		
		if ( installType not in ('simple', 'na', '' )):
			#AdminApplication.configureClassLoaderLoadingModeForAnApplication(appName,  "PARENT_LAST")
			setClassloaderToParentLast(appName)
			AdminApplication.configureClassLoaderPolicyForAnApplication(appName, "SINGLE")

		roles = retrieveRoles(earFileName)
		if (len(roles) > 0):
			AdminApp.edit(appName, ['-MapRolesToUsers', roles])
		
		AdminConfig.save()
		
		print "Saving..."
		
		print ""
		print "------------------------------------------------"
		print " Application install OK: " + appName
		print "------------------------------------------------"
		print ""
		AdminNodeManagement.syncActiveNodes()
	except:
		_type_, _value_, _tbck_ = sys.exc_info()
		error = `_value_`
		print "Error Installing Application"
		print "Error Message = "+error
	#endTry 
	
def createMSSQLJDBCProvider (ClusterName, ds_jdbc_name, DefaultPathName, DefaultNativePathName):
	scope=""
	ds_jdbc_name = ds_jdbc_name.strip()
	emptyspace = ' '
	if (emptyspace in ds_jdbc_name):
		ds_jdbc_name = '"'+ds_jdbc_name+'"'

	if (ClusterName =='na'):
		scope='Cell'
		ClusterName=AdminControl.getCell()
	else:
		scope='Cluster'

	JDBCProvider = AdminTask.createJDBCProvider('[-scope '+ scope+ '='+ ClusterName+' -databaseType "SQL Server" -providerType "Microsoft SQL Server JDBC Driver" -implementationType "Connection pool data source" -name ' + ds_jdbc_name + ' -description "Microsoft SQL Server JDBC Driver. This provider is configurable in version 6.1.0.15 and later nodes." -classpath [ '+ DefaultPathName + ' ] -nativePath [${MICROSOFT_JDBC_DRIVER_NATIVEPATH} ] ]') 
	AdminConfig.save()
	return JDBCProvider
	

def createMSSQLDatasource(ds_jdbc_name, jndiName, Alias, databaseName, portNumber, serverName, providerId):
	ds_jdbc_name = ds_jdbc_name.rstrip()
	emptyspace = ' '
	if (emptyspace in ds_jdbc_name):
		ds_jdbc_name = '"'+ds_jdbc_name+'"'
	
	MSSQLDatasource = AdminTask.createDatasource(providerId, '[-name '+ds_jdbc_name +' -jndiName '+ jndiName +' -dataStoreHelperClassName com.ibm.websphere.rsadapter.MicrosoftSQLServerDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias '+Alias +' -configureResourceProperties [[databaseName java.lang.String '+ databaseName +' ] [portNumber java.lang.Integer ' +portNumber + ' ] [serverName java.lang.String '+serverName + ' ]]]') 
	
	#MSSQLDatasource = AdminTask.createDatasource(providerId,['-name',ds_jdbc_name,'-jndiName',jndiName,'-dataStoreHelperClassName','com.ibm.websphere.rsadapter.DB2UniversalDataStoreHelper','-componentManagedAuthenticationAlias',Alias,'-xaRecoveryAuthAlias',Alias,'-configureResourceProperties','[[databaseName java.lang.String '+databaseName+'] [driverType java.lang.Integer 4] [serverName java.lang.String  '+serverName+']  [portNumber java.lang.Integer  '+portNumber+']]'])	
	
	MappingModule = AdminConfig.create('MappingModule', MSSQLDatasource, '[[authDataAlias '+Alias +'] [mappingConfigAlias ""]]')  
	#AdminConfig.modify(MSSQLDatasource, '[[name "'+ds_jdbc_name+'_CF"] [authDataAlias "'+Alias +'"] [xaRecoveryAuthAlias ""]]')
	AdminConfig.save()

def _createJAASDataSource (Database, db_alias, db_uid, ds_jdbc_name, ds_jndi_name, Database_name_url, Server_name, Port_number, ClusterName):
	DefaultXA = "false"
	DefaultNativePathName = ""
	DefaultDriverType = "4"
	DefaultStmtCacheSize = "60"
	
	if (ClusterName =='na'):
		print "Setting the Scope as Cell"
		clusterId = getCellId ()
	else:
		print "Setting the Scope as Cluster"
		clusterId = AdminConfig.getid("/ServerCluster:" + ClusterName + "/")

	# create J2C aliases
	createJAASAuthData(db_alias, db_uid, db_uid) 	
	AdminConfig.save()
	
	#driverName = driverName.replace('\n', '')
	if (Database == "DB2"):
		DefaultProviderType = "DB2 Universal"
		DefaultPathName =  "/opt/db2/db2jcc.jar;/opt/db2/db2jcc_license_cu.jar"
	elif (Database == "MSSQL"):
		DefaultProviderType = "SQL Server"
		DefaultPathName =  "/opt/IBM/WebSphere/AppServer/lib/ext/sqljdbc.jar;/opt/IBM/WebSphere/AppServer/lib/ext/sqljdbc4.jar"	
	elif (Database == "Oracle"):	
		DefaultProviderType = "Oracle"
		DefaultPathName = "/opt/IBM/WebSphere/AppServer/lib/ext/ojdbc6.jar"		
	
	# create JDBCProvider
	Provider = []
	if (Database == "DB2" or Database == "Oracle"): 
		Provider = createJDBCProvider(DefaultProviderType, DefaultXA, clusterId, DefaultPathName, DefaultNativePathName, ds_jdbc_name )
	elif (Database == "MSSQL"):
		providerId = createMSSQLJDBCProvider (ClusterName, ds_jdbc_name, DefaultPathName, DefaultNativePathName)
		createMSSQLDatasource(ds_jdbc_name, ds_jndi_name, db_alias, Database_name_url, Port_number, Server_name, providerId)
	
	print "%s Provider Created" %(DefaultProviderType)
	AdminConfig.save()

	# create Data sources
	created_ds=""
	if (Database == "DB2" or Database == "Oracle"): 
		created_ds = createDatasource(ds_jdbc_name, ds_jndi_name, DefaultStmtCacheSize, db_alias, Provider)
	AdminConfig.save()
	
	if (Database == "DB2"): 
		updateDB2orDerbyDatasource (created_ds, Database_name_url, Server_name, Port_number, DefaultDriverType)
	elif (Database == "Oracle"):
		updateOracleDatasource(created_ds, Database_name_url)
	#endIf
	
	print "Saving..."
	AdminConfig.save()	
#endDef 

def createJAASDataSource (Database, db_alias, db_uid, ds_jdbc_name, ds_jndi_name, Database_name_url, Server_name, Port_number, ClusterName):
	print "createJAASDataSource.py"
	try:
		_createJAASDataSource (Database, db_alias, db_uid, ds_jdbc_name, ds_jndi_name, Database_name_url, Server_name, Port_number, ClusterName)
	except Exception, e:
		print "Wow I am here with exception in program createJAASDataSource -", e

#-----------------------------------------------------------------
# WARNING: Jython/Python is extremly sensitive to indentation
# errors. Please ensure that tabs are configured appropriately
# for your editor of choice.
#-----------------------------------------------------------------

#-----------------------------------------------------------------
# getInput - Obtain generic input from the user. If default value
#            provided, return default value if nothing is entered.
#-----------------------------------------------------------------
def getInput (prompt, defaultValue):
	print ""
	print prompt
	retValue = sys.stdin.readline().strip() 
	if (retValue == ""):
		retValue = defaultValue
	#endIf

	return retValue
#endDef

#-----------------------------------------------------------------
# getValidInput - Obtain valid input from the user based on list of
#            valid options. Continue to query user if the invalid
#            options are entered. Return default value if nothing
#            is entered.
#-----------------------------------------------------------------
def getValidInput (prompt, defaultValue, validOptions):
	validate = 1     

	while (validate):
		print ""
		print prompt
		retValue = sys.stdin.readline().strip()

		if (retValue == ""):
			retValue = defaultValue
			validate = 0
		#endIf
                
		if (validate and validOptions.count(retValue) > 0):
			# Is retValue one of the valid options
			validate = 0
		#endIf
	#endWhile

	return retValue
#endDef

#-----------------------------------------------------------------
# getName - Return the base name of the config object.
#-----------------------------------------------------------------
def getName (objectId):
	endIndex = (objectId.find("(c") - 1)
	stIndex = 0
	if (objectId.find("\"") == 0):
		stIndex = 1
	#endIf
	return objectId[stIndex:endIndex+1]
#endDef


#-----------------------------------------------------------------
# getCellId - Return the cell id. It is assumed that only one cell
#            exists.
#-----------------------------------------------------------------
def getCellId ():
	cell = AdminConfig.list("Cell").split("\n")
	if (len(cell) != 1):
		print "Cell is not available.  This script assumes that there is one and only one cell available."
		print "Exiting..."
		sys.exit()
	#endIf

	return cell[0]
#endDef

#-----------------------------------------------------------------
# getNodeId - Return the node id of the existing node if in a single
#           server environment. If in an ND environment query the
#           user to determine desired node.
#-----------------------------------------------------------------
def getNodeId (prompt):
	nodeList = AdminConfig.list("Node").split("\n")

	if (len(nodeList) == 1):
		node = nodeList[0]
	else:
		print ""
		print "Available Nodes:"
                
		nodeNameList = []

		for item in nodeList:
			item = item.rstrip()
			name = getName(item) 

			nodeNameList.append(name)
			print "   " + name
		#endFor

		DefaultNode = nodeNameList[0]
		if (prompt == ""):
			prompt = "Select the desired node"
		#endIf

		nodeName = getValidInput(prompt+" ["+DefaultNode+"]:", DefaultNode, nodeNameList )

		index = nodeNameList.index(nodeName)
		node = nodeList[index]
	#endElse

	return node
#endDef

#-----------------------------------------------------------------
# getServerId - Return the server id of the existing server if
#           in a single server environment. If in an ND environment
#           query the user to determine desired server.
#-----------------------------------------------------------------
def getServerId (prompt):
	serverList = AdminConfig.list("Server").split("\n")

	if (len(serverList) == 1):
		server = serverList[0]
	else:
		print ""
		print "Available Servers:"
		
		serverNameList = []                

		for item in serverList:
			item = item.rstrip()
			name = getName(item)

			serverNameList.append(name)
			print "   " + name
		#endFor

		DefaultServer = serverNameList[0]
		if (prompt == ""):
			prompt = "Select the desired server"
		#endIf                
		serverName = getValidInput(prompt+" ["+DefaultServer+"]:", DefaultServer, serverNameList )

		index = serverNameList.index(serverName)
		server = serverList[index]
	#endElse

	return server
#endDef

#-----------------------------------------------------------------
# getServer1Id - Return the id for server1 if it exists
#-----------------------------------------------------------------
def getServer1Id ():
	serverList = AdminConfig.getid("/Server:server1/").split("\n")

	if (len(serverList) != 1):
		print "More than one default server (server1) available."
		print "Exiting..."
		sys.exit()
	#endIf

	return serverList[0]
#endDef

#-----------------------------------------------------------------
# getNodeIdFromServerId - Return the node id based on the node
#            name found within the server id
#-----------------------------------------------------------------
def getNodeIdFromServerId (serverId):
	nodeName = serverId.split("/")[3]

	return AdminConfig.getid("/Node:" + nodeName + "/")
#endDef



	#endElse
#endDef

#-----------------------------------------------------------------
# createJDBCProvider - Create a new JDBC Provider if one with the
#            same name does not exist in the specified scope. Otherwise,
#            return the existing JDBCProvider. The 3 types or providers
#            currently supported include DB2 JCC, DB2 CLI, and Oracle.
#-----------------------------------------------------------------
def createJDBCProvider (provider, XA, scopeId, path, nativePath, driverName):
	
	XA = XA.lower()
	
	print "Creating JDBC provider of type " + provider

	if (provider == "DB2 Universal"):
		name = "DB2 Universal JDBC Driver Provider Only"
		if (XA == "true"):
			name = "DB2 Universal JDBC Driver Provider Only (XA)"
		#endIf
	elif (provider == "DB2 iSeries (Toolbox)"):
		name = "DB2 UDB for iSeries Provider Only (Toolbox)"
		if (XA == "true"):
			name = "DB2 UDB for iSeries Provider Only (Toolbox XA)"
		#endIf
	elif (provider == "DB2 iSeries (Native)"):
		name = "DB2 UDB for iSeries Provider Only (Native)"
		if (XA == "true"):
			name = "DB2 UDB for iSeries Provider Only (Native XA)"
		#endIf
	elif (provider == "DB2 for zOS Local"):
		name = "DB2 for zOS Local JDBC Provider Only (RRS)"
	elif (provider == "Derby"):
		name = "Derby JDBC Provider"
		if (XA == "true"):
			name = "Derby JDBC Provider Only (XA)"
		#endIf
	elif (provider == "Oracle"):
		name = "Oracle JDBC Driver Provider Only"
		if (XA == "true"):
			name = "Oracle JDBC Driver Provider Only (XA)"
		#endIf
	elif (provider == "Embedded MS SQL Server"):
		name = "WebSphere embedded ConnectJDBC driver for MS SQL Server Provider Only"
		if (XA == "true"):
			name = "WebSphere embedded ConnectJDBC driver for MS SQL Server Provider Only (XA)"
		#endIf
	elif (provider == "SQL Server"):
		name = "Microsoft SQL Server JDBC Driver"
		if (XA == "true"):
			name = "Microsoft SQL Server JDBC Driver (XA)"
		#endIf
	elif (provider == "Informix"):
		name = "Informix JDBC Driver Provider Only"
		if (XA == "true"):
			name = "Informix JDBC Driver Provider Only (XA)"
		#endIf
	#endIf

	print " "
	print "Creating JDBC Provider " + driverName + " ... at scope " + scopeId + "   .... "

	# Check if the JDBC provider already exists	

	scopeName = getName(scopeId)

	stIndex = (scopeId.find("|") + 1)
	endIndex = (scopeId.find(".") - 1)
	scope = scopeId[stIndex:endIndex+1]

	print "Scope is :" + scope + " ....."
	cellName=AdminControl.getCell()
	providerId = ""
	if (scope == "cell"):
		providerId = AdminConfig.getid("/Cell:"+scopeName+"/JDBCProvider:\""+driverName+"\"/" )
	elif (scope == "node"):
		providerId = AdminConfig.getid("/Node:"+scopeName+"/JDBCProvider:\""+driverName+"\"/" )
	elif (scope == "server"):
		providerId = AdminConfig.getid("/Server:"+scopeName+"/JDBCProvider:\""+driverName+"\"/" )
	elif (scope == "cluster"):
		providerId = AdminConfig.getid("/Cell:"+cellName+"/ServerCluster:"+scopeName+"/JDBCProvider:\""+driverName+"\"/" )
	#endIf

	print "ProviderID is : " + providerId + "..."
	if (providerId == ""):
		print "  Provider Name:        " + driverName
		print "  Classpath:            " + path
		print "  Native path:          " + nativePath
		print "  XA enabled:           " + XA

		template = AdminConfig.listTemplates("JDBCProvider", name+"(")
			
		providerId = AdminConfig.createUsingTemplate("JDBCProvider", scopeId, [["name", driverName], ["classpath", path], ["nativepath", nativePath]], template)
		print "JDBC ProviderID:        " + providerId
#		AdminConfig.modify(providerId, '[[name "Oracle JDBC Driver Provider Only"] [implementationClassName "oracle.jdbc.pool.OracleConnectionPoolDataSource"] [isolatedClassLoader "false"] [description "Oracle JDBC Driver (XA)"]]')

		# Template creates a datasource with the same name as the provider
		# Delete this datasource
		dsId = ""
		dsList = AdminConfig.list("DataSource")
		if (len(dsList) > 0):
			for item in dsList.split("\n"):
				item = item.rstrip()
				provider = AdminConfig.showAttribute(item, "provider" )
				if (providerId == provider):
					dsId = item
					print "Found DS"
				#endIf
			#endFor
		#endIf
		if (dsId != ""):
			AdminConfig.remove(dsId)
		#endIf

		print driverName + " provider created successfully!"
	else:
		print driverName + " provider already exists!"
	#endElse
	
	return [providerId,name]
#endDef



def createDatasource (datasourceName, jndiName, stmtCacheSz, authAliasName, providerId):
	# Connection pool properties
	maxConnections =    50
	minConnections =    10

	print " "
	print "Creating DataSource " + datasourceName + "..."
	
	# Check if the DataSource already exists
	dsId = ""
	dsList = AdminConfig.getid("/DataSource:" + datasourceName + "/")
	if (len(dsList) > 0):
		for item in dsList.split("\n"):
			item = item.rstrip()
			provider = AdminConfig.showAttribute(item, "provider" )
			if (providerId == provider):
				dsId = item
			#endIf
		#endFor
	#endIf

	if (dsId == ""):
		print "  Datasource Name:       " + datasourceName
		print "  JNDI Name:             " + jndiName
		print "  Statement Cache Size:  " + str(stmtCacheSz)	
		print "  AuthAliasName:         " + authAliasName
		
		# Map provider to datasource template
		providerName = getName(providerId)
		
		providerToDsDict = {"DB2 UDB for iSeries Provider Only (Native XA)":"DB2 UDB for iSeries (Native XA) DataSource",
					"DB2 UDB for iSeries Provider Only (Native)":"DB2 UDB for iSeries (Native) DataSource",
					"DB2 UDB for iSeries Provider Only (Toolbox XA)":"DB2 UDB for iSeries (Toolbox XA) DataSource",
					"DB2 UDB for iSeries Provider Only (Toolbox)":"DB2 UDB for iSeries (Toolbox) DataSource",
					"DB2 Universal JDBC Driver Provider Only (XA)":"DB2 Universal JDBC Driver XA DataSource",
					"DB2 Universal JDBC Driver Provider Only":"DB2 Universal JDBC Driver DataSource",
					"DB2 for zOS Local JDBC Provider Only (RRS)":"DB2 for zOS Local JDBC Driver DataSource (RRS)",
					"Derby JDBC Provider Only":"Derby JDBC Driver DataSource",
					"Derby JDBC Provider Only (XA)":"Derby JDBC Driver XA DataSource",
					"Oracle JDBC Driver Provider Only (XA)":"Oracle JDBC Driver XA DataSource",
					"Oracle JDBC Driver Provider Only":"Oracle JDBC Driver DataSource",
					"WebSphere embedded ConnectJDBC driver for MS SQL Server Provider Only (XA)":"WebSphere embedded ConnectJDBC for SQL Server XA DataSource",
					"WebSphere embedded ConnectJDBC driver for MS SQL Server Provider Only":"WebSphere embedded ConnectJDBC for SQL Server DataSource",
					"Informix JDBC Driver Provider Only (XA)":"Informix JDBC Driver XA DataSource",
					"Informix JDBC Driver Provider Only":"Informix JDBC Driver DataSource"}

		dsName = providerToDsDict[providerName]
		
		template =  AdminConfig.listTemplates("DataSource", dsName)
		attr = [["name", datasourceName], ["jndiName", jndiName], ["statementCacheSize", stmtCacheSz]]
		if (authAliasName != ""):
			attr.append(["authDataAlias", authAliasName])
			attr.append(["xaRecoveryAuthAlias", authAliasName])
		#endIf
		dsId = AdminConfig.createUsingTemplate("DataSource", providerId, attr, template)

		#Update connection pool sizings
		pool = AdminConfig.showAttribute(dsId, "connectionPool")
		AdminConfig.modify(pool, [["maxConnections", maxConnections], ["minConnections", minConnections]])

		#Determine RRA
		tempName = providerId[providerId.rfind("/")+1 : providerId.rfind("|")]
		if (providerId.find("/servers/") > 0):
			radapter = AdminConfig.getid("/Server:" + tempName + "/J2CResourceAdapter:WebSphere Relational Resource Adapter/")
		elif (providerId.find("/nodes/") > 0):
			radapter = AdminConfig.getid("/Node:" + tempName + "/J2CResourceAdapter:WebSphere Relational Resource Adapter/")
		elif (providerId.find("(cells/") > 0):
			radapter = AdminConfig.getid("/Cell:" + tempName + "/J2CResourceAdapter:WebSphere Relational Resource Adapter/")
		#endIf
		
		#Create CMPConnectionFactory
		tempList = AdminConfig.listTemplates('CMPConnectorFactory','default')
		template = ""
		if (len(tempList) > 0):
			for item in tempList.split("\n"):
				item = item.rstrip()
				if (item[0:20] == "CMPConnectorFactory("):
					template = item
					break
				#endIf
			#endFor
		#endIf
		
		attr = [["name", datasourceName + "_CF"], ["cmpDatasource", dsId]]
		cmpFact_id = AdminConfig.createUsingTemplate("CMPConnectorFactory", radapter, attr, template)

		print datasourceName + " created successfully!"
	else:
		print datasourceName + " already exists in this JDBC Provider!"
	#endIf

	return dsId
#endDef

def addDatasourceProperty (datasourceId, name, value):
    parms = ["-propertyName", name, "-propertyValue", value]
    AdminTask.setResourceProperty(datasourceId, parms)
#endDef 

def updateDB2orDerbyDatasource (datasourceId, dbname, hostname, port, driverType):
	resourceProps = AdminConfig.list("J2EEResourceProperty", datasourceId).split("\n")
	for item in resourceProps:
		item = item.rstrip()
		propName = getName(item)
		if (propName == "serverName"):
			AdminConfig.modify(item, [["value", hostname]])
		#endIf
		if (propName == "portNumber"):
			AdminConfig.modify(item, [["value", port]])
		#endIf
		if (propName == "databaseName"):
			AdminConfig.modify(item, [["value", dbname]])
		#endIf
		if (propName == "driverType"):
			AdminConfig.modify(item, [["value", driverType]])
		#endIf
	#endFor
#endDef

def updateInformixDatasource (datasourceId, dbname, serverName, port, ifxHost, lockMode):
	resourceProps = AdminConfig.list("J2EEResourceProperty", datasourceId).split("\n")
	for item in resourceProps:
		item = item.rstrip()
		propName = getName(item)
		if (propName == "serverName"):
			AdminConfig.modify(item.rstrip(), [["value", serverName]])
		#endIf
		if (propName == "portNumber"):
			AdminConfig.modify(item, [["value", port]])
		#endIf
		if (propName == "databaseName"):
			AdminConfig.modify(item, [["value", dbname]])
		#endIf
		if (propName == "informixLockModeWait"):
			AdminConfig.modify(item, [["value", lockMode]])
		#endIf
		if (propName == "ifxIFXHOST"):
			AdminConfig.modify(item, [["value", ifxHost]])
		#endIf
	#endFor
#endDef

def updateOracleDatasource(datasourceId, url):
        resourceProps = AdminConfig.list("J2EEResourceProperty", datasourceId).split("\n")
        for item in resourceProps:
                item = item.rstrip()
                propName = getName(item)
                if (propName == "URL"):
                        AdminConfig.modify(item, [["value", url]])
                #endIf
        #endFor
#endDef

def updateOracleDatasourceForApp (datasourceId, sid, hostname, port):
	resourceProps = AdminConfig.list("J2EEResourceProperty", datasourceId).split("\n")
	url = "jdbc:oracle:thin:@" + hostname + ":" + port + ":" + sid        
	for item in resourceProps:
		item = item.rstrip()
		propName = getName(item)
		if (propName == "URL"):
			AdminConfig.modify(item, [["value", url]])
		#endIf
	#endFor
#endDef



#-----------------------------------------------------------------
# enableSIBService - Enable the SIB Service on the specified
#            server.
#-----------------------------------------------------------------
def enableSIBService (serverId):
	serverName = getName(serverId)

	service = ""
	serviceList = AdminConfig.list("SIBService")
	for item in serviceList.split("\n"):
		item = item.rstrip()
		if (item.find("servers/" + serverName + "|") >= 0):
			service = item
		#endIf
	#endFor

	print " "
	print "Enabling SIB Service on " + serverName + "..."

	if (service == ""):                 
		print "Unable to find SIB Service!"
	else:
		parms = [["enable", "true"]]
		AdminConfig.modify(service, parms )
		print "SIB Service enabled successfully!"
	#endElse
#endDef

#-----------------------------------------------------------------
# createSIBus - Create a new SIBus if one does not exist. Otherwise,
#            return the existing SIBus.
#-----------------------------------------------------------------
def createSIBus_wip ( busName, authAlias ):
	print " "
	print "Creating SIBus " + busName + "..."

	# Check if the SIBus already exists

	SIBus = AdminConfig.getid("/SIBus:"+busName+"/" )
	if (SIBus == ""):
		parms = ["-bus", busName, "-interEngineAuthAlias", authAlias]
		SIBus = AdminTask.createSIBus(parms )
                
		print busName + " created successfully!"
	else:
		print busName + " already exists!"
	#endElse

	return SIBus
#endDef



#-----------------------------------------------------------------
# createSIBusRole - Add user role
#-----------------------------------------------------------------

#endDef

#-----------------------------------------------------------------
# addSIBusMember - Add the specified server or cluster to the
#            SIBus if it does not already exist. Assumes that the
#            specified SIBus already exists.
#-----------------------------------------------------------------
def addSIBusMember_wip ( busId, fileStore, targetArgs, dataStoreArgs ):
	#    busName          - SIBus name
	#    fileStore [0]    - create file store, otherwise create data store
 	#    fileStore [1]    - logDirectory - directory where fileStore is located (only used if fileStore[0] = true)
	#    targetArgs[0]    - cluster name or node name
	#    targetArgs[1]    - server name
	#    dataStoreArgs[0] - defaultDS - create default DS (true|false)
	#    dataStoreArgs[1] - dsJndi - jndi name of the datastore (only used if defaultDS = false)

	busName = getName(busId)
	if (len(targetArgs) == 1):
		clusterName = targetArgs[0]
		nodeName = "dummy"
		serverName = "dummy"
	else:
		nodeName = targetArgs[0]
		serverName = targetArgs[1]
		clusterName = "dummy"
	#endElse

	if (len(dataStoreArgs) == 2):
		defaultDS = dataStoreArgs[0]
		dsJndi = dataStoreArgs[1]
		defaultDS = defaultDS.lower()
	#endIf

	# Check if the bus member already exists
	parms = ["-bus", busName]
	busMembers = AdminTask.listSIBusMembers(parms).split("\n")
	member = ""
	if (busMembers[0] != ""):
		for item in busMembers:
			item = item.rstrip()
			cluster = AdminConfig.showAttribute(item, "cluster" )
			node = AdminConfig.showAttribute(item, "node" )
			server = AdminConfig.showAttribute(item, "server" )

			if (cluster == clusterName  or ( server == serverName  and node == nodeName ) ):
				member = item
				break
			#endIf
		#endFor
	#endIf
	
	if (member == ""):
		print ""
		if (len(targetArgs) == 1):
			print "Adding SIBus member " + clusterName + "..."
			parms = ["-bus", busName, "-cluster", clusterName]
		else:
			print "Adding SIBus member " + nodeName + " - " + serverName + "..."
			parms = ["-bus", busName, "-node", nodeName, "-server", serverName]
		#endElse

		print "  File Store:            " + fileStore[0]
		if (fileStore[0] == "true"):
			parms.append("-fileStore")
			if (fileStore[1] != "default" and fileStore[1] != ""):
				print "  File Store Location:   " + fileStore[1]
				parms.append("-logDirectory")
                        	parms.append(fileStore[1])
			#endIf
		else:
			parms.append("-dataStore")
			print "  Default DataSource:    " + defaultDS
			parms.append("-createDefaultDatasource")
			parms.append(defaultDS)
			if (defaultDS == "false"):
				print "  Datasource JNDI Name:  " + dsJndi
				parms.append("-datasourceJndiName")
				parms.append(dsJndi)
			#endIf
		#endElse

		member = AdminTask.addSIBusMember(parms )
		print "SIBus member added successfully!"
	else:
		print "SIBus member already exists!"
	#endElse

	return member
#endDef

#-----------------------------------------------------------------
# createMessageEngine - Create a new message engine on the specified
#            target.
#-----------------------------------------------------------------
def createMessageEngine ( busId, defaultDS, dsJndi, optArgs ):
	#    busName     - SIBus name
	#    defaultDS   - create default DS (true|false)
	#    dsJndi      - jndi name of the datasource (only used if defaultDS = false)
	#    optArgs[0]  - node name or cluster name
	#    optArgs[1]  - server name

	defaultDS = defaultDS.lower()
	if (len(optArgs) == 1):
		clusterName = optArgs[0]
	else:
		nodeName = optArgs[0]
		serverName = optArgs[1]
	#endElse

	busName = getName(busId)

	print " "
	print "Creating SIB Messaging Engine..."
	print "  Bus Name:            " + busName
	print "  Default DataSource:  " + defaultDS
	if (defaultDS == "false"):
		print "  Datasource JNDI Name:  " + dsJndi
	#endIf
	if (len(optArgs) == 1):
		print "  Cluster Name:        " + clusterName
	else:
		print "  Node Name:           " + nodeName
		print "  Server Name:         " + serverName
	#endElse

	if (len(optArgs) == 1):
		parms = ["-bus", busName, "-cluster", clusterName, "-createDefaultDatasource", defaultDS]
	else:
		parms = ["-bus", busName, "-node", nodeName, "-server", serverName, "-createDefaultDatasource", defaultDS]
	#endElse

	if (defaultDS == "false"):
		parms.append("-datasourceJndiName")
		parms.append(dsJndi)
	#endIf

	me = AdminTask.createSIBEngine(parms )
	print getName(me) + "Message Engine created successfully!"
	
	return me
#endDef

#-----------------------------------------------------------------
# modifyMEDataStore - Modify the data store attributes for the
#            target messageing engine.
#-----------------------------------------------------------------

#-----------------------------------------------------------------
# createSIBDestination - Create a new SIB Destination if one with the same
#            name does not exist on the specified SIBus. Otherwise,
#            return the existing Destination.
#-----------------------------------------------------------------
def createSIBDestination_wip ( busId, destName, destType, reliability, optArgs ):
	#    SIBus       - SIBus name
	#    destName    - destination name
	#    destType    - destination type
	#    reliability - reliability
	#    optArgs[0]  - cluster name or node name
	#    optArgs[1]  - server name

	if (len(optArgs) == 1):
		clusterName = optArgs[0]
	elif (len(optArgs) == 2) :
		nodeName = optArgs[0]
		serverName = optArgs[1]
	#endElse

	print " "
	print "Creating SIB Destination " + destName + "..."

	# Check if the SIB Destination already exists
	SIBus = getName(busId)
	parms = ["-bus", SIBus]
	destList = AdminTask.listSIBDestinations(parms )

	dest = ""
	if (len(destList) > 0):
		for item in destList.split("\n"):
			item = item.rstrip()
			ident = AdminConfig.showAttribute(item.rstrip(), "identifier" )
			if (ident == destName):
				dest = item.rstrip()
				break
			#endIf
		#endFor
	#endIf

	if (dest == ""):        
		print "  Destination Name:  " + destName
		print "  Destination Type:  " + destType
		print "  Reliability:       " + reliability
                
		parms = ["-bus", SIBus, "-name", destName, "-type", destType, "-reliability", reliability]

		if (destType == "Queue"):
			if (len(optArgs) == 1):
				print "  Cluster Name:      " + clusterName
				parms.append("-cluster")
				parms.append(clusterName)
			elif (len(optArgs) == 2):
				print "  Node Name:         " + nodeName
				print "  Server Name:       " + serverName
				parms.append("-node")
				parms.append(nodeName)
				parms.append("-server")
				parms.append(serverName)
			#endElse
		#endIf

		dest = AdminTask.createSIBDestination(parms )
                
		print destName + " created successfully!"
	else:
		print destName + " already exists!"
	#endElse

	return dest
#endDef


	#endElse
#endDef

#-----------------------------------------------------------------
# createOneOfNPolicy - Install the SIB JMS Resource Adapter
#            at the cell scope.
#-----------------------------------------------------------------




#-----------------------------------------------------------------
# createWMQConnectionFactory - Create a new WMQ Connection Factory
#            if one with the same name does not exist.
#            Otherwise, return the existing Connection Factory.
#-----------------------------------------------------------------
def createWMQConnectionFactory_wip (cfName, cfType, jndiName, mq_queue_manager_name, mq_host_name, mq_channel_port, mq_channel_name, scope ):
	# Create JMS Connection Factory
	#    cfName     - connection factory name
	#    cfType     - connection factory type
	#    jndiName   - connection factory jndi name
	#    mq_queue_manager_name - Queue Manager name
	#    mq_host_name - Hostname of MQ Q Manager
	#    mq_channel_port - port number of channel	
	#    mq_channel_name  - channel name
	#    scope      - scope

	print " "
	print "Creating WMQ " + cfType + " Connection Factory " + cfName + "..."

	# Check if the connection factory already exists

	parms = ["-type", cfType]
	cfList = AdminTask.listWMQConnectionFactories(scope, parms )
	connectionFactory = ""
	if (len(cfList) > 0):
		for item in cfList.split("\n"):
			item = item.rstrip()
			if (item.find(cfName) >= 0):
				connectionFactory = item
				break
			#endIf
		#endFor
	#enfIf

	if (connectionFactory == "" ):
		print "  Connection Factory Name:  " + cfName
		print "  Connection Factory Type:  " + cfType
		print "  JNDI Name:                " + jndiName
		print "  Queue Manager Name:       " + mq_queue_manager_name
		print "  Queue Manager Host Name:  " + mq_host_name
		print "  Queue Manager Port :      " + mq_channel_port
		print "  Channel Name :            " + mq_channel_name

		params = ["-name", cfName, "-jndiName", jndiName, "-qmgrName", mq_queue_manager_name, "-type", cfType, "-wmqTransportType", "CLIENT", "-qmgrHostname", mq_host_name, "-qmgrPortNumber", mq_channel_port, "-qmgrSvrconnChannel", mq_channel_name]
		connectionFactory = AdminTask.createWMQConnectionFactory(scope, params )
                
		print cfName + " created successfully!"
	else:
		print cfName + " already exists!"
	#endElse

	return connectionFactory
#endDef

#-----------------------------------------------------------------
# createWMQQueue - Create a new JMS Queue if one with the same
#            name does not exist at the specified scope. Otherwise,
#            return the existing JMS Queue.
#-----------------------------------------------------------------
def createWMQQueue2 ( qName, jndiName, mqQueueName,scope ):
	#    qName    - queue name
	#    jndiName - queue jndi name
	#    mqQueueName  - Name of Queue in MQ
	#    scope    - scope

	print " "
	print "Creating WMQ Queue " + qName + "..."

	# Check if the queue already exists

	qList = AdminTask.listWMQQueues(scope )
	queue = ""
	if (len(qList) > 0):
		for item in qList.split("\n"):
			item = item.rstrip()
			if (item.find(qName) >= 0):
				queue = item
				break
			#endIf
		#endFor
	#endIf

	if (queue == ""):
		print "  Queue Name:       " + qName
		print "  JNDI Name:        " + jndiName
		print "  Queue Destination:" + mqQueueName

		params = ["-name", qName, "-jndiName", jndiName, "-queueName", mqQueueName, "-qmgr","", "-descrption", ""]
		queue = AdminTask.createSIBJMSQueue(scope, params )
                
		print qName + " created successfully!"
	else:
		print qName + " already exists!"
	#endElse

	return queue
#endDef

#-----------------------------------------------------------------
# createJMSConnectionFactory - Create a new JMS Connection Factory
#            if one with the same name does not exist on the SIBus.
#            Otherwise, return the existing Connection Factory.
#-----------------------------------------------------------------
def createJMSConnectionFactory ( busId, cfName, cfType, jndiName, authAlias, scope ):
	# Create JMS Connection Factory
	#    SIBus      - SIBus name
	#    cfName     - connection factory name
	#    cfType     - connection factory type
	#    jndiName   - connection factory jndi name
	#    authAlias  - authentication alias name
	#    scope      - scope

	print " "
	print "Creating JMS " + cfType + " Connection Factory " + cfName + "..."

	# Check if the connection factory already exists

	parms = ["-type", cfType]
	cfList = AdminTask.listSIBJMSConnectionFactories(scope, parms )
	connectionFactory = ""
	if (len(cfList) > 0):
		for item in cfList.split("\n"):
			item = item.rstrip()
			if (item.find(cfName) >= 0):
				connectionFactory = item
				break
			#endIf
		#endFor
	#enfIf

	if (connectionFactory == "" ):
		print "  Connection Factory Name:  " + cfName
		print "  Connection Factory Type:  " + cfType
		print "  JNDI Name:                " + jndiName

		params = ["-name", cfName, "-jndiName", jndiName, "-busName", getName(busId), "-type", cfType, "-authDataAlias", authAlias]
		connectionFactory = AdminTask.createSIBJMSConnectionFactory(scope, params )
                
		print cfName + " created successfully!"
	else:
		print cfName + " already exists!"
	#endElse

	return connectionFactory
#endDef



#-----------------------------------------------------------------
# createJMSQueue - Create a new JMS Queue if one with the same
#            name does not exist at the specified scope. Otherwise,
#            return the existing JMS Queue.
#-----------------------------------------------------------------
def createJMSQueue_wip ( qName, jndiName, SIBDest, delMode, scope ):
	#    qName    - queue name
	#    jndiName - queue jndi name
	#    SIBDest  - SIB destination
	#    delMode  - delivery mode
	#    scope    - scope

	print " "
	print "Creating JMS Queue " + qName + "..."

	# Check if the queue already exists

	qList = AdminTask.listSIBJMSQueues(scope )
	queue = ""
	if (len(qList) > 0):
		for item in qList.split("\n"):
			item = item.rstrip()
			if (item.find(qName) >= 0):
				queue = item
				break
			#endIf
		#endFor
	#endIf

	if (queue == ""):
		print "  Queue Name:       " + qName
		print "  JNDI Name:        " + jndiName
		print "  SIB Destination:  " + SIBDest
		print "  Delivery Mode:    " + delMode

		params = ["-name", qName, "-jndiName", jndiName, "-queueName", SIBDest, "-deliveryMode", delMode]
		queue = AdminTask.createSIBJMSQueue(scope, params )
                
		print qName + " created successfully!"
	else:
		print qName + " already exists!"
	#endElse

	return queue
#endDef



#-----------------------------------------------------------------
# createJMSTopic - Create a new JMS Topic if one with the same
#            name does not exist at the specified scope. Otherwise,
#            return the existing JMS Topic.
#-----------------------------------------------------------------
def createJMSTopic ( tName, jndiName, tSpace, delMode, scope ):
	#    tName    - topic name
	#    jndiName - topic jndi name
	#    tSpace   - topic space
	#    delMode  - delivery mode
	#    scope    - scope

	print " "
	print "Creating JMS Topic " + tName + "..."

	# Check if the topic already exists

	tList = AdminTask.listSIBJMSTopics(scope )
	topic = ""
	if (len(tList) > 0):
		for item in tList.split("\n"):
			item = item.rstrip()
			if (item.find(tName) >= 0):
				topic = item
				break
			#endIf
		#endFor
	#endIf

	if (topic == ""):
		print "  Topic Name:     " + tName
		print "  JNDI Name:      " + jndiName
		print "  Topic Space:    " + tSpace
		print "  Delivery Mode:  " + delMode

		params = ["-name", tName, "-jndiName", jndiName, "-topicName", tName, "-topicSpace", tSpace, "-deliveryMode", delMode]
		topic = AdminTask.createSIBJMSTopic(scope, params )
                
		print tName + " created successfully!"
	else:
		print tName + " already exists!"
	#endElse

	return topic
#endDef



#-----------------------------------------------------------------
# createMDBActivationSpec - Create a new MDB Activation Spec if one
#            with the same name does not exist at the specified
#            scope. Otherwise, return the existing Activation Spec.
#-----------------------------------------------------------------
def createMDBActivationSpec ( mdbName, jndiName, busId, JMSDestJndi, destType, authAlias, scope, durability ):
	#    mdbName     - MDB name
	#    jndiName    - activation spec jndi name
	#    SIBus       - SIBus name
	#    JMSDestJndi - JMS destination JNDI name
	#    destType    - destination type
	#    authAlias   - authentication alias name
	#    scope       - scope
	#    durability  - subscriptionDurability

	print " "
	print "Creating MDB Activation Spec " + mdbName + "..."

	# Check if the activation spec already exists

	asList = AdminTask.listSIBJMSActivationSpecs(scope )
	mdb = ""
	if (len(asList) > 0):
		for item in asList.split("\n"):
			item = item.rstrip()
			if (item.find(mdbName) >= 0):
				mdb = item
				break
			#endIf
		#endFor
	#endIf

	if (mdb == ""):
		print "  MDB Activation Spec Name:   " + mdbName
		print "  JNDI Name:                  " + jndiName
		print "  JMS Destination JNDI Name:  " + JMSDestJndi
		print "  Destination Type:           " + destType

		SIBus = getName(busId)
		params = ["-name", mdbName, "-jndiName", jndiName, "-busName", SIBus, "-destinationJndiName", JMSDestJndi, "-destinationType", destType, "-authenticationAlias", authAlias, "-subscriptionDurability", durability, "-clientId", mdbName, "-subscriptionName", mdbName]
		mdb = AdminTask.createSIBJMSActivationSpec(scope, params )
                
		print mdbName + " created successfully!"
	else:
		print mdbName + " already exists!"
	#endElse

	return mdb
#endDef



#-----------------------------------------------------------------
# addHostAliasToDefaultHost - Add the specified port to the default
#            host mappings.
#-----------------------------------------------------------------
def addHostAliasToDefaultHost ( port ):
	#    port - port number

	print " "
	print "Creating HostAlias for " + port + "..."

	# Check if the port already exists

	hostList = AdminConfig.list("HostAlias" )
	hostAlias = ""
	if (len(hostList) > 0):
		for item in hostList.split("\n"):
			item = item.rstrip()
			tmp = AdminConfig.showAttribute(item, "port" )
			if (tmp == port):
				hostAlias = item
				break
			#endIf
		#endFor
	#endIf

	if (hostAlias == ""):
		print "  Host Name:  *"
		print "  Port:       " + port

		vhList = AdminConfig.list("VirtualHost" )
		defaultHost = ""
		for item in vhList.split("\n"):
			item = item.rstrip()
			if (getName(item) == "default_host"): 
				defaultHost = item
			#endIf
		#endFor

		attrs = [["hostname", "*" ], ["port", port]]
		hostAlias = AdminConfig.create("HostAlias", defaultHost, attrs )

		print port + " created successfully!"
	else:
		print port + " already exists!"
	#endElse

	return hostAlias
#endDef

#-----------------------------------------------------------------
# createServer - Create a new server if one with the same name
#            does not exist. Otherwise, return the existing server.
#-----------------------------------------------------------------
def createServer ( serverName, nodeName ):
	#    serverName - server name
	#    nodeName   - node name

	print " "
	print "Creating Server " + serverName + "..."

	# Check if the server already exists

	server = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
                
	if (server == ""):
		print "  Server Name:  " + serverName
		print "  Node Name:    " + nodeName

		node = AdminConfig.getid("/Node:"+nodeName+"/" )

		templateList = AdminConfig.listTemplates("Server","APPLICATION_SERVER")
		template = ""
		for item in templateList.split("\n"):
			item = item.rstrip()
			if (getName(item) == "default"):
				template = item
				break
			#endIf
		#endFor                

		attrs = [["name", serverName]]
		server = AdminConfig.createUsingTemplate("Server", node, attrs, template )
                
		print serverName + " created successfully!"
	else:
		print serverName + " already exists!"
	#endElse

	return server
#endDef

#-----------------------------------------------------------------
# createCluster - Create a new cluster if one with the same name
#            does not exist. Otherwise, return the existing cluster.
#-----------------------------------------------------------------
def createCluster ( clusterName, preferLocal, description, cell ):
	#    clusterName - cluster name
	#    preferLocal - prefer local value
	#    description - cluster description
	#    cell        - cell

	print " "
	print "Creating Cluster " + clusterName + "..."

	# Check if the cluster already exists
	cluster = ""
	clusterList = AdminConfig.list("ServerCluster" )
	if (len(clusterList) > 0):
		for item in clusterList.split("\n"):
			item = item.rstrip()
			if (item.find(clusterName) >= 0):
				cluster = item
				break
			#endIf
		#endFor
	#endIf

	if (cluster == ""):
		print "  Cluster Name:  " + clusterName
		print "  Prefer Local:  " + preferLocal
		print "  Description:   " + description

		attrs = [["name", clusterName], ["preferLocal", preferLocal], ["description", "$description"]]
		cluster = AdminConfig.create("ServerCluster", cell, attrs )
                
		print clusterName + " created successfully!"
	else:
		print clusterName + " already exists!"
	#endElse

	return cluster
#endDef

#-----------------------------------------------------------------
# createClusterMember - Create a new cluster member if one with the
#            same name does not exist. Otherwise, return the
#            existing cluster member.
#-----------------------------------------------------------------
def createClusterMember ( memberName, nodeId, weight, clusterId ):
	#    memberName - member name
	#    node       - node
	#    weight     - weight
	#    cluster    - cluster

	print " "
	print "Creating Cluster Member " + memberName + "..."

	# Check if the cluster member already exists
	member = ""
	memberList = AdminConfig.list("ClusterMember" )
	if (len(memberList) > 0):
		for item in memberList.split("\n"):
			item = item.rstrip()
			if (item.find(memberName) >= 0):
				member = item
				break
			#endIf
		#endFor
	#endIf

	if (member == ""):
		print "  Member Name:  " + memberName
		print "  Node:         " + getName(nodeId)
		print "  Weight:       " + weight
		print "  Cluster:      " + getName(clusterId)

		attrs = [["memberName", memberName], ["weight", weight]]
		member = AdminConfig.createClusterMember(cluster, node, attrs )
        
		print memberName + " created successfully!"
	else:
		print memberName + " already exists!"
	#endElse

	return member
#endDef

def mapModulesToServers(listCluster):
	webServers = AdminTask.listServers('[-serverType WEB_SERVER ]')
	webServers = webServers.split("\n")
	cellName = AdminControl.getCell()
	pos1='.*'
	parms =""

	for webServer in webServers:
		serverList=re.split('[(/|]',webServer)
		parms += "WebSphere:cell=%s,node=%s,server=%s" %(serverList[2], serverList[4], serverList[6]) + '+'
	parms += 'WebSphere:cell=%s,cluster=%s' %(cellName, listCluster)
	return parms

def mapModulesToServersEx(listCluster):
	webServers = AdminTask.listServers('[-serverType WEB_SERVER ]')
	webServers = webServers.split("\n")
	cellName = AdminControl.getCell()
	pos1='.*'
	parms =""

	for webServer in webServers:
		serverList=re.split('[(/|]',webServer)
		parms += "WebSphere:cell=%s,node=%s,server=%s" %(serverList[2], serverList[4], serverList[6]) + '+'
	parms += 'WebSphere:cell=%s,cluster=%s' %(cellName, listCluster)
	return pos1 + ' ' + pos1 + ' ' + parms

	
#-----------------------------------------------------------------
# installApp - Install the specified application ear file if an
#            application with the same name does not exist.
#-----------------------------------------------------------------
def installApp ( appName, ear_file_name, deployejb, deployws, defaultBindings, earMetaData, dbType, target, virtualHostName):
#http://pic.dhe.ibm.com/infocenter/wasinfo/v8r0/index.jsp?topic=%2Fcom.ibm.websphere.express.doc%2Finfo%2Fexp%2Fae%2Frxml_taskoptions.html
	#    appName         - application name
	#    ear_file_name   - ear_file_name
	#    deployejb       - deploy ejb (true|false)
	#    deployws        - deploy webservices (true|false)
	#    defaultBindings - use default binding (true|false)
	#    earMetaData     - use MetaData from ear (true|false)
	#    dbType          - ejb deploy db type
	#    target[0]       - node name or cluster name
	#    target[1]       - server name
	#    virtualHostName - virtual host name

	print ""
	pos1='.*'
	print "Installing application " + appName + "..."
	
	deployejb = deployejb.lower()
	deployws = deployws.lower()
	defaultBindings = defaultBindings.lower()
	earMetaData = earMetaData.lower()

	# Check if the application already exists
	app = ""
	appList = AdminApp.list( )
	if (len(appList) > 0):
		for item in appList.split("\n"):
			item = item.rstrip()
			if (item.find(appName) == 0):
				app = item
				break
			#endIf
		#endFor
	#endIf

	if (app == ""):
		print "  Application Name:      " + appName
		print "  Ear file:              " + ear_file_name
		if (len(target) == 1):
			cluster = target[0]
			print "  Target Cluster:        " + cluster
		else:
			node = target[0]
			server = target[1]
			print "  Target Node:           " + node
			print "  Target Server:         " + server
		#endElse
		print "  Deploy EJB:            " + deployejb
		print "  Deploy WebServices:    " + deployws
		print "  Use default bindings:  " + defaultBindings
		print "  Use Ear MetaData:      " + earMetaData
		print "  Deployed DB Type:      " + dbType

		'''options = [
			"["
			"-nopreCompileJSPs",
			"-distributeApp ",
			"-nouseMetaDataFromBinary ",
			"-nodeployejb ",
			"-appname " + appName,
			"-createMBeansForResources ",
			"-noreloadEnabled ",
			"-nodeployws ",
			"-validateinstall warn ",
			"-noprocessEmbeddedConfig ",
			"-filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 ",
			"-noallowDispatchRemoteInclude ",
			"-noallowServiceRemoteInclude ",
			"-MapModulesToServers [[.* .*,.* " + serverString + " ]]"
			"]"
		]'''
		parms = "-appname " + appName
		#parms += " -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 "
		
		if (deployejb == "true"):
			parms += " -deployejb"
			parms += " -deployejb.dbtype " + dbType
		else:
			parms += " -nodeployejb"
		#endElse
		if (deployws == "true"):
			parms += " -deployws"
		else:
			parms += " -nodeployws"
		#endElse
		if (defaultBindings == "true"):
			parms += " -usedefaultbindings"
		#endIf
		if (earMetaData == "true"):
			parms += " -useMetaDataFromBinary"
		else:
			parms += " -nouseMetaDataFromBinary"
		#endElse

		if (cluster not in ('', 'na')):
			parms += " -MapModulesToServers " + '[['+ mapModulesToServersEx(target[0]) + ']]'
		
		if (virtualHostName not in ('', 'na')):
			parms += " -MapWebModToVH " +'[[ %s %s %s ]]' %(pos1, pos1, virtualHostName)
			
		parms1 = [parms]

		print "Starting application install..."
		app = AdminApp.install(ear_file_name, parms1 )

		print "Install completed successfully!"
	else:
		print appName + " already exists!"
	#endElse

	return app
#endDef

#-----------------------------------------------------------------
# uninstallApp - Uninstall the specified application if it exists.
#-----------------------------------------------------------------



# <ND IWD>
#-----------------------------------------------------------------
# syncAllNodes - Force synchronize all nodes
#-----------------------------------------------------------------


#-----------------------------------------------------------------
# startApp - Start application on all nodes
#-----------------------------------------------------------------
def startApp (applicationName, clusterName ):
	print "Starting application " + applicationName + " on cluster " + clusterName
	# loop until status is started
	while (not AdminApp.isAppReady(applicationName) ):
		sleep(1)
	# endWhile

	# get list of cluster members
	clusterMembers = AdminConfig.getid('/ServerCluster:%s/ClusterMember:/' % clusterName).splitlines()

	# start application in each cluster member
	for clusterMember in clusterMembers:

  		# cluster member server name and node name
  		serverName = AdminConfig.showAttribute(clusterMember, "memberName")
  		nodeName = AdminConfig.showAttribute(clusterMember, "nodeName")
		#print serverName
		#print nodeName

  		# get ApplicationManager MBean for the cluster member
  		applicationManager = AdminControl.queryNames('type=ApplicationManager,node=%s,process=%s,*' % (nodeName, serverName))
		#print applicationManager

  		# if the ApplicationManager MBean was found (for example, cluster member is running), stop the application
		if(len(applicationManager) > 0):
			AdminControl.invoke(applicationManager, 'startApplication', '[%s]' % applicationName, '[java.lang.String]')
			#AdminControl.invoke('WebSphere:name=ApplicationManager,process=DayTrader_0_WVE_TradeNode_3,platform=proxy,node=WVE_TradeNode_3,version=8.0.0.1,type=ApplicationManager,mbeanIdentifier=ApplicationManager,cell=WVE_TradeCell_1,spec=1.0',  'startApplication', '[DayTrader2-EE5]', '[java.lang.String]') 
		# endIf
	# endFor
#endDef

def getVirtualHostByName( virtualhostname ):
    """Return the id of the named VirtualHost"""
    hosts = AdminConfig.list( 'VirtualHost' )
    hostlist = _splitlines(hosts)
    for host_id in hostlist:
        name = AdminConfig.showAttribute( host_id, "name" )
        if name == virtualhostname:
            return host_id
    return None

def _splitlines(s):
  rv = [s]
  if '\r' in s:
    rv = s.split('\r\n')
  elif '\n' in s:
    rv = s.split('\n')
  if rv[-1] == '':
    rv = rv[:-1]
  return rv

def readArgs(argList):
    args = {}
    for arg in argList:
        argument = arg.strip()
        if argument[0] == '-':
            # arg starts with '-' so its a property and next arg should be a value
            property = arg[1:]
            getValue = 1
            args[property] = property
        else:
            args[property] = argument

    return args
#endDef

def nppFirewall (port):
	#sys.path.append('/0config/nodepkgs/common/python')
	#os.environ['KERNELSERVICE_URL']=''

	import maestro
	maestro.firewall
	maestro.firewall.open_tcpin(dport=port)
	maestro.firewall.open_tcpout(dport=port)
	maestro.firewall.open_in(protocol="udp", dport=port)
	maestro.firewall.open_out(protocol="udp", dport=port)
	print "Finished opening firewall ports! - ", port

def createCluster (clusterName, serverName):
	managedNodes = AdminTask.listManagedNodes().splitlines()
	AdminTask.createCluster('[-clusterConfig [-clusterName ' + clusterName + ' -preferLocal true]]')

	i = 1
	for managedNode in managedNodes:
		cluster = AdminConfig.getid('/ServerCluster:' + clusterName + '/')
		memberName = serverName + str(i)
		node = AdminConfig.getid('/Node:' + managedNode + '/')
		AdminConfig.createClusterMember(cluster, node, [['memberName', memberName ]])
		i = i + 1
	#startCluster(clusterName)
	AdminConfig.save()

# WIP
# http://www-01.ibm.com/support/knowledgecenter/SSAW57_8.5.5/com.ibm.websphere.nd.doc/ae/rxml_atwimmgt.html?lang=en
def createUser_wip (userName, password):
	AdminTask.createUser ('[-uid %s -password %s -confirmPassword %s -cn ernese -sn ENorelus]' %(userName,password,password))
	AdminTask.addMemberToGroup ('[-memberUniqueName uid=ernese,cn=users,dc=IBM,dc=com –groupUniqueName cn=admins,cn=groups,dc=IBM,dc=com]')
	AdminTask.addMemberToGroup ('[-memberUniqueName uid=ernese,o=defaultWIMFileBasedRealm -groupUniqueName cn=ernese,o=defaultWIMFileBasedRealm]')
	AdminTask.getMembersOfGroup('[-uniqueName cn=ernese,o=defaultWIMFileBasedRealm]')
	AdminConfig.save()
	
def createCoreGroup_wip(coreGroupName):
	AdminTask.createCoreGroup('[-coreGroupName %s]' %(coreGroupName))
	cellName = AdminControl.getCell()
	core = AdminConfig.getid('/Cell:%s/CoreGroup:%s/'%(cellName,coreGroupName ))
	AdminConfig.modify(core, [['description', "This is my new description"]]) 
	AdminConfig.save()  
	#AdminConfig.list('CoreGroup', AdminConfig.getid( '/Cell:%s/' %(cellName)))

def createDynamicCluster_wip(DC_Name, Group_Name):
	
	#Create Node Group
	AdminTask.createNodeGroup(Group_Name)

	managedNodes = AdminTask.listManagedNodes().splitlines()
	i = 1
	for managedNode in managedNodes:
		nodeNameAttr = ["-nodeName", managedNode]
		#Create Node Group Members
		AdminTask.addNodeGroupMember( Group_Name, nodeNameAttr)
		#Create DC
		mb=AdminControl.queryNames('type=DynamicClusterConfigManager,process=dmgr,*')
		AdminControl.invoke(mb, "createDynamicCluster", Group_Name + " " +DC_Name+ " \"\"  \"\" ")
		i = i + 1
	#Save configuration Changes
	AdminConfig.save()

####### ########### Start Adding for CPALL v2.0


def createNodeGroup():

	print 'createNodeGroup...'
	f = open(r'/tmp/DCA_CFG/createNodeGroup.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")
			groupName = strTok.nextToken().strip()
			print groupName
			AdminTask.createNodeGroup(groupName)			
		skiphead = skiphead + 1	
	AdminConfig.save()
	f.close()

def addNodeGroupMember():

	print 'addNodeGroupMember...'
	
	f = open(r'/tmp/DCA_CFG/addNodeGroupMember.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")
			groupName = strTok.nextToken().strip()
			nodeName = strTok.nextToken().strip()
			print groupName, nodeName
			nodeNameAttr = ["-nodeName", nodeName]	
			AdminTask.addNodeGroupMember( groupName, nodeNameAttr)
		skiphead = skiphead + 1	
	AdminConfig.save()
	f.close()

	
def createCoreGroup():

	print 'createCoreGroup...'

	f = open(r'/tmp/DCA_CFG/createCoreGroup.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")
			coreGroupName = strTok.nextToken().strip()
			print coreGroupName
			AdminTask.createCoreGroup('[-coreGroupName %s]' %(coreGroupName))
			cellName = AdminControl.getCell()
			core = AdminConfig.getid('/Cell:%s/CoreGroup:%s/'%(cellName,coreGroupName ))
			AdminConfig.modify(core, [['description', coreGroupName]])
		skiphead = skiphead + 1	
	AdminConfig.save()
	f.close()

def createTemplateCluster():
	
	print 'createTemplateCluster...'
	f = open(r'/tmp/DCA_CFG/createTemplateCluster.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")
			clusterName = strTok.nextToken().strip()
			groupName = strTok.nextToken().strip()
			print clusterName, groupName
			
			mb=AdminControl.queryNames('type=DynamicClusterConfigManager,process=dmgr,*')
			AdminControl.invoke(mb, "createDynamicCluster", groupName + " " +clusterName+ " \"\"  \"\" ")
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

def modifyServerPort():

	print 'modifyServerPort...'
	f = open(r'/tmp/DCA_CFG/modifyServerPort.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			serverName = strTok.nextToken().strip()
			nodeName = strTok.nextToken().strip()
			endPointName = strTok.nextToken().strip()
			port = strTok.nextToken().strip()
			print serverName, nodeName, endPointName, port		
			AdminTask.modifyServerPort(serverName, '[-nodeName ' + nodeName + ' -endPointName '+endPointName+' -host * -port '+ port +' -modifyShared true]')		
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def setJVMPropertiesCluster():

	print 'setJVMPropertiesCluster...'
	f = open(r'/tmp/DCA_CFG/setJVMProperties.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			initialHeapSize = strTok.nextToken().strip()
			maximumHeapSize = strTok.nextToken().strip()
			jvmClassPath = strTok.nextToken().strip()
			print clusterName, initialHeapSize, maximumHeapSize, jvmClassPath
			nodeName = AdminControl.getNode()			
			if (clusterName == 'Dmgr' or clusterName == 'dmgr'):
				AdminTask.setJVMProperties('[-nodeName '+nodeName+' -serverName dmgr -verboseModeClass false -verboseModeGarbageCollection false -verboseModeJNI false -initialHeapSize '+initialHeapSize+' -maximumHeapSize '+maximumHeapSize+' -runHProf false -hprofArguments -debugMode false -debugArgs "-Djava.compiler=NONE -Xdebug -Xnoagent -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7792" -executableJarFileName -genericJvmArguments -disableJIT false]') 
				
			else :
				if (clusterName == 'NodeAgent' or clusterName == 'nodeagent' or clusterName == 'Nodeagent'):
					CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')	
					nodes=AdminConfig.list('Node', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
					for sid in nodes :
						nodeName = AdminConfig.showAttribute(sid, "name")	
						if (nodeName.find('Dmgr') ==-1) and (nodeName.find('wi') ==-1) and (nodeName.find('wb')==-1):	
							print nodeName
							AdminTask.setJVMProperties('[-nodeName '+nodeName+' -serverName nodeagent -classpath "" -bootClasspath "" -verboseModeClass false -verboseModeGarbageCollection false -verboseModeJNI false -initialHeapSize '+initialHeapSize+' -maximumHeapSize '+maximumHeapSize+' -runHProf false -hprofArguments -debugMode false -debugArgs "-Djava.compiler=NONE -Xdebug -Xnoagent -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7777" -executableJarFileName -genericJvmArguments "-Djava.awt.headless=true" -disableJIT false]') 	
				else :
					cellName = AdminControl.getCell()	
					AdminTask.setJVMProperties(clusterName+'(cells/'+cellName+'/dynamicclusters/'+clusterName+'/servers/'+clusterName+'|server.xml)', '[-classpath ['+jvmClassPath+' ] -verboseModeClass false -verboseModeGarbageCollection true -verboseModeJNI false -initialHeapSize ' + initialHeapSize + ' -maximumHeapSize ' +  maximumHeapSize + ' -runHProf false -hprofArguments -debugMode false -debugArgs "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=7777" -executableJarFileName -genericJvmArguments -disableJIT false]') 	
		
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

def setJVMPropertiesNode():
	print 'setJVMPropertiesNode...'
	
	nodeName = AdminControl.getNode()
	
	AdminTask.setJVMProperties('[-nodeName '+nodeName+' -serverName dmgr -verboseModeClass false -verboseModeGarbageCollection false -verboseModeJNI false -initialHeapSize 512 -maximumHeapSize 3072 -runHProf false -hprofArguments -debugMode false -debugArgs "-Djava.compiler=NONE -Xdebug -Xnoagent -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7792" -executableJarFileName -genericJvmArguments -disableJIT false]') 
	
	CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')	
	nodes=AdminConfig.list('Node', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
	for sid in nodes :
		nodeName = AdminConfig.showAttribute(sid, "name")	
		if (nodeName.find('Dmgr') ==-1) and (nodeName.find('wi') ==-1) and (nodeName.find('wb')==-1):	
			print nodeName
			AdminTask.setJVMProperties('[-nodeName '+nodeName+' -serverName nodeagent -classpath "" -bootClasspath "" -verboseModeClass false -verboseModeGarbageCollection false -verboseModeJNI false -initialHeapSize 256 -maximumHeapSize 1024 -runHProf false -hprofArguments -debugMode false -debugArgs "-Djava.compiler=NONE -Xdebug -Xnoagent -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7777" -executableJarFileName -genericJvmArguments "-Djava.awt.headless=true" -disableJIT false]') 	
	
	AdminConfig.save() 

def modifyThreadPool():

	print 'modifyThreadPool...'
	f = open(r'/tmp/DCA_CFG/modifyThreadPool.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			propName = strTok.nextToken().strip()
			Min = strTok.nextToken().strip()
			Max = strTok.nextToken().strip()
			inactivityTimeout = strTok.nextToken().strip()
			print clusterName,propName,Min,Max,inactivityTimeout
			
			cellName = AdminControl.getCell()
			serverId = AdminConfig.getid('/Server:'+clusterName)
			threadPoolIds = AdminConfig.list('ThreadPool', serverId).splitlines()
	
			for threadPoolId in threadPoolIds:	
				if (threadPoolId.find(propName) >=0):	
					print 'Jython threadPool@' + threadPoolId
					AdminConfig.modify(threadPoolId, '[[maximumSize "'+Max+'"] [name "'+propName+'"] [minimumSize "'+Min+'"] [inactivityTimeout "'+inactivityTimeout+'"] [description ""] [isGrowable "false"]]') 

		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
		
def createDynamicCluster():

	print 'createDynamicCluster...'
	f = open(r'/tmp/DCA_CFG/createDynamicCluster.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			nodeGroup = strTok.nextToken().strip()
			coreGroup = strTok.nextToken().strip()
			nodeTemplate = strTok.nextToken().strip()
			serverTemplate = strTok.nextToken().strip()
			enableHA = strTok.nextToken().strip()
			numVerticalInstances = strTok.nextToken().strip()
			
			print clusterName, nodeGroup, coreGroup, nodeTemplate, serverTemplate, enableHA, numVerticalInstances	
			
			if (serverTemplate == 'n/a' or serverTemplate == '' or nodeTemplate == 'n/a' or nodeTemplate == ''):
				print "Don't use Template Cluster"
				cellName = AdminControl.getCell()
				templateName = cellName + "/" + nodeTemplate + "/" + serverTemplate
				AdminTask.createDynamicCluster(clusterName,"[-membershipPolicy \"node_nodegroup = \'"+nodeGroup+"\'\" -dynamicClusterProperties \"[[operationalMode manual][-enableHA true][minInstances 1][maxInstances -1][numVerticalInstances "+numVerticalInstances+"][serverInactivityTime 60]]\" -clusterProperties \"[[preferLocal false][createDomain false][coreGroup "+coreGroup+"]]\"]")
				modifyEnableHA(clusterName, enableHA)
		
			else:	
				print "Use Template Cluster"
				cellName = AdminControl.getCell()
				templateName = cellName + "/" + nodeTemplate + "/" + serverTemplate
				AdminTask.createDynamicCluster(clusterName,"[-membershipPolicy \"node_nodegroup = \'"+nodeGroup+"\'\" -dynamicClusterProperties \"[[operationalMode manual][-enableHA true][minInstances 1][maxInstances -1][numVerticalInstances "+numVerticalInstances+"][serverInactivityTime 60]]\" -clusterProperties \"[[preferLocal false][createDomain false][templateName "+templateName+"][coreGroup "+coreGroup+"]]\"]")
				modifyEnableHA(clusterName, enableHA)
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

def modifyEnableHA(clusterName, enableHA):
    cid = AdminConfig.getid("/ServerCluster:"+clusterName)
    AdminConfig.modify(cid,[["enableHA",enableHA]])
	
def createJAASAuthData (  ):

	print 'createJAASAuthData...'
	f = open(r'/tmp/DCA_CFG/createJAASAuthData.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			aliasName = strTok.nextToken().strip()
			user = strTok.nextToken().strip()
			passwd = strTok.nextToken().strip()
			print aliasName, user, passwd
			
			authDataAlias = ""
			authList = AdminConfig.list("JAASAuthData" )
			if (len(authList) > 0):
				for item in authList.split("\n"):
					item = item.rstrip()
					alias = AdminConfig.showAttribute(item, "alias" )
					if (alias == aliasName):
						authDataAlias = item
						break
						
			if (authDataAlias == ""):
				attrs = AdminConfig.list("Security")
				attrs0 = [["alias", aliasName], ["userId", user], ["password", passwd]]
						
				authDataAlias = AdminConfig.create("JAASAuthData", attrs, attrs0)
						
				print aliasName + " created successfully!"
			else:
				print aliasName + " already exists!"
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createXADataSource():

	print 'createXADataSource...'
	f = open(r'/tmp/DCA_CFG/createXADataSource.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			jdbcName = strTok.nextToken().strip()
			dataSourceName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			authenAlias = strTok.nextToken().strip()
			databaseName = strTok.nextToken().strip()
			serverName = strTok.nextToken().strip()
			portNumber = strTok.nextToken().strip()
			scope = strTok.nextToken().strip()
			print clusterName, jdbcName, dataSourceName, jndiName, authenAlias, databaseName, serverName, portNumber, scope
			
			if (scope == 'Cell' or scope == 'cell'):	
				jdbcId = AdminConfig.getid('/Cell:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/Cell:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				rraId = AdminConfig.getid( '/Cell:'+ clusterName +'/J2CResourceAdapter:WebSphere Relational Resource Adapter/')
				
				print 'Jython jdbcId@' + jdbcId
				print 'Jython dataSourceId@' + dataSourceId
				print 'Jython rraId@' + rraId
				
				#"/J2CResourceAdapter:WebSphere Relational Resource Adapter/"
				print "rraId@" + rraId	

				if (len(jdbcId) == 0):
					print "Creating JDBCProvider:" + jdbcName

					AdminTask.createJDBCProvider('[-scope Cell='+clusterName+' -databaseType DB2 -providerType "DB2 Universal JDBC Driver Provider" -implementationType "XA data source" -name "'+jdbcName+'" -description "Two-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support the use of XA to perform 2-phase commit processing. Use of driver type 2 on the application server for z/OS is not supported for data sources created under this provider." -classpath [${DB2UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc.jar ${UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cu.jar ${DB2UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cisuz.jar ] -nativePath [${DB2UNIVERSAL_JDBC_DRIVER_NATIVEPATH} ] ]')
					jdbcId = AdminConfig.getid('/Cell:'+clusterName+'/JDBCProvider:' + jdbcName)
					print "jdbcId@" + jdbcId
				else:
					print "JDBCProvider: " + jdbcName + " already exists, not creating JDBCProvider"
				
				if (len(dataSourceId) == 0):
					print "Creating DataSource:" + dataSourceName
					
					AdminTask.createDatasource('"'+jdbcId+'"', '[-name '+dataSourceName+' -jndiName '+jndiName+' -dataStoreHelperClassName com.ibm.websphere.rsadapter.DB2UniversalDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias '+authenAlias+' -xaRecoveryAuthAlias '+authenAlias+' -configureResourceProperties [[databaseName java.lang.String '+databaseName+'] [driverType java.lang.Integer 4] [serverName java.lang.String '+serverName+'] [portNumber java.lang.Integer '+portNumber+']]]') 
					dataSourceId = AdminConfig.getid('/Cell:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
					print "dataSourceId@" + dataSourceId

					AdminConfig.create('MappingModule', dataSourceId, '[[authDataAlias '+authenAlias+'] [mappingConfigAlias DefaultPrincipalMapping]]')	
					cfId = AdminConfig.getid("/CMPConnectorFactory:"+dataSourceName+'_CF'+"/")
					print "cfId@" + cfId
							
				else:
					print "Datasource:"+dataSourceName+" already exists, not creating Datasource"
			
			if (scope == 'Cluster' or scope == 'cluster'):
				jdbcId = AdminConfig.getid('/ServerCluster:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/ServerCluster:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				rraId = AdminConfig.getid( '/ServerCluster:'+ clusterName +'/J2CResourceAdapter:WebSphere Relational Resource Adapter/')
				
				#"/J2CResourceAdapter:WebSphere Relational Resource Adapter/"
				print "rraId@" + rraId	

				if (len(jdbcId) == 0):
					print "Creating JDBCProvider:" + jdbcName

					AdminTask.createJDBCProvider('[-scope Cluster='+clusterName+' -databaseType DB2 -providerType "DB2 Universal JDBC Driver Provider" -implementationType "XA data source" -name "'+jdbcName+'" -description "Two-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support the use of XA to perform 2-phase commit processing. Use of driver type 2 on the application server for z/OS is not supported for data sources created under this provider." -classpath [${DB2UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc.jar ${UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cu.jar ${DB2UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cisuz.jar ] -nativePath [${DB2UNIVERSAL_JDBC_DRIVER_NATIVEPATH} ] ]')
					jdbcId = AdminConfig.getid('/ServerCluster:'+clusterName+'/JDBCProvider:' + jdbcName)
					print "jdbcId@" + jdbcId
				else:
					print "JDBCProvider: " + jdbcName + " already exists, not creating JDBCProvider"
				
				if (len(dataSourceId) == 0):
					print "Creating DataSource:" + dataSourceName
					
					AdminTask.createDatasource('"'+jdbcId+'"', '[-name '+dataSourceName+' -jndiName '+jndiName+' -dataStoreHelperClassName com.ibm.websphere.rsadapter.DB2UniversalDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias '+authenAlias+' -xaRecoveryAuthAlias '+authenAlias+' -configureResourceProperties [[databaseName java.lang.String '+databaseName+'] [driverType java.lang.Integer 4] [serverName java.lang.String '+serverName+'] [portNumber java.lang.Integer '+portNumber+']]]') 
					dataSourceId = AdminConfig.getid('/ServerCluster:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
					print "dataSourceId@" + dataSourceId

					AdminConfig.create('MappingModule', dataSourceId, '[[authDataAlias '+authenAlias+'] [mappingConfigAlias DefaultPrincipalMapping]]')	
					cfId = AdminConfig.getid("/CMPConnectorFactory:"+dataSourceName+'_CF'+"/")
					print "cfId@" + cfId
							
				else:
					print "Datasource:"+dataSourceName+" already exists, not creating Datasource"
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
	
def getConfigItemId (scope, scopeName, nodeName, objectType, item):
	global AdminConfig

	scope = scope.title()
	if (scope == "Cell"):
		confItemId = AdminConfig.getid("/Cell:"+scopeName+"/"+objectType+":"+item)
	elif (scope == "Node"):
		confItemId = AdminConfig.getid("/Node:"+scopeName+"/"+objectType+":"+item)
	elif (scope == "Cluster"):
		confItemId = AdminConfig.getid("/ServerCluster:"+scopeName+"/"+objectType+":"+item)
	elif (scope == "Server"):
		confItemId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+scopeName+"/"+objectType+":"+item)
	#endIf
	return confItemId
#endDef
	
def createXADataSourceOracle():

	print 'createXADataSourceOracle...'
	f = open(r'/tmp/DCA_CFG/createXADataSourceOracle.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			jdbcName = strTok.nextToken().strip()
			dataSourceName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			authenAlias = strTok.nextToken().strip()
			databaseURL = strTok.nextToken().strip()
			scope = strTok.nextToken().strip()
			print clusterName, jdbcName, dataSourceName, jndiName, authenAlias, databaseURL, scope
			
			if (scope == 'Cell' or scope == 'cell'):	
				jdbcId = AdminConfig.getid('/Cell:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/Cell:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				rraId = AdminConfig.getid( '/Cell:'+ clusterName +'/J2CResourceAdapter:WebSphere Relational Resource Adapter/')
				
				#"/J2CResourceAdapter:WebSphere Relational Resource Adapter/"
				print "rraId@" + rraId	

				if (len(jdbcId) == 0):
					print "Creating JDBCProvider:" + jdbcName

					AdminTask.createJDBCProvider('[-scope Cell='+clusterName+' -databaseType Oracle -providerType "Oracle JDBC Driver" -implementationType "XA data source" -name "'+jdbcName+'" -description "Two-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support the use of XA to perform 2-phase commit processing. Use of driver type 2 on the application server for z/OS is not supported for data sources created under this provider." -classpath [${ORACLE_JDBC_DRIVER_PATH}/ojdbc6.jar ]  -nativePath "" ]')
					jdbcId = AdminConfig.getid('/Cell:'+clusterName+'/JDBCProvider:' + jdbcName)
					print "jdbcId@" + jdbcId
				else:
					print "JDBCProvider: " + jdbcName + " already exists, not creating JDBCProvider"
				
				if (len(dataSourceId) == 0):
					print "Creating DataSource:" + dataSourceName
					
					AdminTask.createDatasource('"'+jdbcId+'"', '[-name '+dataSourceName+' -jndiName '+jndiName+' -dataStoreHelperClassName com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias '+authenAlias+' -xaRecoveryAuthAlias '+authenAlias+' -configureResourceProperties [[URL java.lang.String '+databaseURL+'] ]]') 
					dataSourceId = AdminConfig.getid('/Cell:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
					print "dataSourceId@" + dataSourceId

					AdminConfig.create('MappingModule', dataSourceId, '[[authDataAlias '+authenAlias+'] [mappingConfigAlias DefaultPrincipalMapping]]')	
					cfId = AdminConfig.getid("/CMPConnectorFactory:"+dataSourceName+'_CF'+"/")
					print "cfId@" + cfId
							
				else:
					print "Datasource:"+dataSourceName+" already exists, not creating Datasource"

			if (scope == 'Cluster' or scope == 'cluster'):	

				jdbcId = AdminConfig.getid('/ServerCluster:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/ServerCluster:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				rraId = AdminConfig.getid( '/ServerCluster:'+ clusterName +'/J2CResourceAdapter:WebSphere Relational Resource Adapter/')
				
				#"/J2CResourceAdapter:WebSphere Relational Resource Adapter/"
				print "rraId@" + rraId	

				if (len(jdbcId) == 0):
					print "Creating JDBCProvider:" + jdbcName

					AdminTask.createJDBCProvider('[-scope Cluster='+clusterName+' -databaseType Oracle -providerType "Oracle JDBC Driver" -implementationType "XA data source" -name "'+jdbcName+'" -description "Two-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support the use of XA to perform 2-phase commit processing. Use of driver type 2 on the application server for z/OS is not supported for data sources created under this provider." -classpath [${ORACLE_JDBC_DRIVER_PATH}/ojdbc6.jar ]  -nativePath "" ]')
					jdbcId = AdminConfig.getid('/ServerCluster:'+clusterName+'/JDBCProvider:' + jdbcName)
					print "jdbcId@" + jdbcId
				else:
					print "JDBCProvider: " + jdbcName + " already exists, not creating JDBCProvider"
				
				if (len(dataSourceId) == 0):
					print "Creating DataSource:" + dataSourceName
					
					AdminTask.createDatasource('"'+jdbcId+'"', '[-name '+dataSourceName+' -jndiName '+jndiName+' -dataStoreHelperClassName com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias '+authenAlias+' -xaRecoveryAuthAlias '+authenAlias+' -configureResourceProperties [[URL java.lang.String '+databaseURL+'] ]]') 
					dataSourceId = AdminConfig.getid('/ServerCluster:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
					print "dataSourceId@" + dataSourceId

					AdminConfig.create('MappingModule', dataSourceId, '[[authDataAlias '+authenAlias+'] [mappingConfigAlias DefaultPrincipalMapping]]')	
					cfId = AdminConfig.getid("/CMPConnectorFactory:"+dataSourceName+'_CF'+"/")
					print "cfId@" + cfId
							
				else:
					print "Datasource:"+dataSourceName+" already exists, not creating Datasource"
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
 	
	
def setJVMLogCluster():

	print 'setJVMLogCluster...'
	f = open(r'/tmp/DCA_CFG/setJVMLog.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			streamType = strTok.nextToken().strip()
			streamProperty = strTok.nextToken().strip()
			StreamValue = strTok.nextToken().strip()
			print clusterName, streamType, streamProperty, StreamValue		
			
			if (clusterName == 'Dmgr' or clusterName == 'dmgr'):
				CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')	
				Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
				for sid in Servers :
					serverName = AdminConfig.showAttribute(sid, "name")
					if serverName == 'dmgr' :		
						jvmLog = AdminConfig.showAttribute(sid, streamType)
						AdminConfig.modify(jvmLog, [[streamProperty, StreamValue]])
			else :
				if (clusterName == 'NodeAgent' or clusterName == 'nodeagent' or clusterName == 'Nodeagent'):
					CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')	
					Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
					for sid in Servers :
						serverName = AdminConfig.showAttribute(sid, "name")
						if serverName == 'nodeagent' :
							jvmLog = AdminConfig.showAttribute(sid, streamType)
							AdminConfig.modify(jvmLog, [[streamProperty, StreamValue]])
				else:									
					serverId = AdminConfig.getid('/Server:'+clusterName)
					jvmLog = AdminConfig.showAttribute(serverId, streamType)
					AdminConfig.modify(jvmLog, [[streamProperty, StreamValue]])
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def setJVMLogNode():
	
	print 'setJVMLogNode...'
	CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')	
	Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
	for sid in Servers :
		serverName = AdminConfig.showAttribute(sid, "name")
		if serverName == 'nodeagent' :
		
			jvmLog = AdminConfig.showAttribute(sid, 'outputStreamRedirect')
			AdminConfig.modify(jvmLog, [['rolloverSize', '5']])
			
			jvmLog = AdminConfig.showAttribute(sid, 'outputStreamRedirect')
			AdminConfig.modify(jvmLog, [['maxNumberOfBackupFiles', '5']])
			
			jvmLog = AdminConfig.showAttribute(sid, 'errorStreamRedirect')
			AdminConfig.modify(jvmLog, [['rolloverSize', '5']])
			
			jvmLog = AdminConfig.showAttribute(sid, 'errorStreamRedirect')
			AdminConfig.modify(jvmLog, [['maxNumberOfBackupFiles', '5']])
			
		if serverName == 'dmgr' :
		
			jvmLog = AdminConfig.showAttribute(sid, 'outputStreamRedirect')
			AdminConfig.modify(jvmLog, [['rolloverSize', '5']])
			
			jvmLog = AdminConfig.showAttribute(sid, 'outputStreamRedirect')
			AdminConfig.modify(jvmLog, [['maxNumberOfBackupFiles', '5']])
			
			jvmLog = AdminConfig.showAttribute(sid, 'errorStreamRedirect')
			AdminConfig.modify(jvmLog, [['rolloverSize', '5']])
			
			jvmLog = AdminConfig.showAttribute(sid, 'errorStreamRedirect')
			AdminConfig.modify(jvmLog, [['maxNumberOfBackupFiles', '5']])

	AdminConfig.save()

def modifyTransactionLog():

	print 'modifyTransactionLog...'
	f = open(r'/tmp/DCA_CFG/modifyTransactionLog.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			serverName = strTok.nextToken().strip()
			logDirectory = strTok.nextToken().strip()
			print serverName, logDirectory			
			serverEntryId = AdminConfig.getid("/ServerEntry:"+serverName)
			print "Jython serverEntryId@ " + serverEntryId			
			trid = AdminConfig.list('TransactionService',serverEntryId)
			AdminConfig.create('RecoveryLog', serverEntryId, '[[transactionLogDirectory '+logDirectory+']]')		
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createEnvironmentEntries():
	
	print 'createEnvironmentEntries...'
	f = open(r'/tmp/DCA_CFG/createEnvironmentEntries.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			propertyName = strTok.nextToken().strip()
			propertyValue = strTok.nextToken().strip()
			print clusterName, propertyName, propertyValue

				
			if (clusterName == 'Dmgr' or clusterName == 'dmgr'):				
				cellName = AdminControl.getCell()
				serverId = AdminConfig.getid('/Server:'+clusterName)
				processDef = AdminConfig.list('JavaProcessDef', serverId)
				print "processDef@ " + processDef
				AdminConfig.create('Property', processDef, '[[validationExpression ""] [name '+'"'+propertyName+'"'+'] [description ""] [value '+'"'+propertyValue+'"'+'] [required "false"]]') 				
			
			
			else :
				if (clusterName == 'NodeAgent' or clusterName == 'nodeagent' or clusterName == 'Nodeagent'):
					print 'nodeagent'
					CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')
					Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
					for sid in Servers :
						serverName = AdminConfig.showAttribute(sid, "name")
						if serverName == 'nodeagent' :
							exe=AdminConfig.list('JavaProcessDef', sid)
							print 'Jython JavaProcessDef@ ' + exe
							AdminConfig.create('Property', exe, '[[validationExpression ""] [name '+'"'+propertyName+'"'+'] [description ""] [value '+'"'+propertyValue+'"'+'] [required "false"]]') 				

				else:
					cellName = AdminControl.getCell()
					serverId = AdminConfig.getid('/Server:'+clusterName)
					processDef = AdminConfig.list('JavaProcessDef', serverId)
					print "processDef@ " + processDef
					AdminConfig.create('Property', processDef, '[[validationExpression ""] [name '+'"'+propertyName+'"'+'] [description ""] [value '+'"'+propertyValue+'"'+'] [required "false"]]') 				
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def modifyProcessExecutionCluster():

	print 'modifyProcessExecution...'
	f = open(r'/tmp/DCA_CFG/modifyProcessExecution.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			runAsUser = strTok.nextToken().strip()
			runAsGroup = strTok.nextToken().strip()
			umask = strTok.nextToken().strip()
			print clusterName, runAsUser, runAsGroup, umask		

			if (clusterName == 'Dmgr' or clusterName == 'dmgr'):				
				CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')
				Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
				for sid in Servers :
					serverName = AdminConfig.showAttribute(sid, "name")
					if serverName == 'dmgr' :
						exe=AdminConfig.list('ProcessExecution', sid)
						print exe
						print AdminConfig.modify(exe, '[[runAsUser '+runAsUser+'] [runAsGroup '+runAsGroup+'] [runInProcessGroup "0"] [processPriority "20"] [umask '+umask+']]') 
			else:
				if (clusterName == 'NodeAgent' or clusterName == 'nodeagent' or clusterName == 'Nodeagent'):
					CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')
					Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
					for sid in Servers :
						serverName = AdminConfig.showAttribute(sid, "name")
						if serverName == 'nodeagent' :
							exe=AdminConfig.list('ProcessExecution', sid)
							print exe
							print AdminConfig.modify(exe, '[[runAsUser '+runAsUser+'] [runAsGroup '+runAsGroup+'] [runInProcessGroup "0"] [processPriority "20"] [umask '+umask+']]') 

				else:				
					serverId = AdminConfig.getid('/Server:'+clusterName)
					processDef = AdminConfig.list('ProcessExecution', serverId)
					print "processDef@ " + processDef
					AdminConfig.modify(processDef, '[[runAsUser "'+runAsUser+'"] [runAsGroup "'+runAsGroup+'"] [runInProcessGroup "0"] [processPriority "20"] [umask "'+umask+'"]]') 			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

#From GoSoft	
def modifyProcessExecutionNode():

	print 'modifyProcessExecutionNode...'
	CellName=AdminConfig.showAttribute(AdminConfig.list("Cell"), 'name')
	Servers=AdminConfig.list('Server', AdminConfig.getid( '/Cell:'+CellName+'/')).splitlines()
	for sid in Servers :
		serverName = AdminConfig.showAttribute(sid, "name")
		if serverName == 'nodeagent' :
			exe=AdminConfig.list('ProcessExecution', sid)
			print AdminConfig.modify(exe, '[[runAsUser "virtuser"] [runAsGroup "wasgroup"] [runInProcessGroup "0"] [processPriority "20"] [umask "002"]]') 
		
		if serverName == 'dmgr' :
			exe=AdminConfig.list('ProcessExecution', sid)
			print AdminConfig.modify(exe, '[[runAsUser "virtuser"] [runAsGroup "wasgroup"] [runInProcessGroup "0"] [processPriority "20"] [umask "002"]]') 
			
	AdminConfig.save() 

def modifyCPCustomProperties():
	
	print 'modifyCPCustomProperties...'
	f = open(r'/tmp/DCA_CFG/modifyCPCustomProperties.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			scope = strTok.nextToken().strip()
			clusterName = strTok.nextToken().strip()
			jdbcName = strTok.nextToken().strip()
			dataSourceName = strTok.nextToken().strip()
			propertyName = strTok.nextToken().strip()
			propertyType = strTok.nextToken().strip()
			propertyValue = strTok.nextToken().strip()
			propertyDescription = strTok.nextToken().strip()
			print scope, clusterName, jdbcName, dataSourceName, propertyName, propertyType ,propertyValue, propertyDescription			
			if (scope == 'Cell' or scope == 'cell'):
				clusterId = AdminConfig.getid('/Cell:'+clusterName+'/' )
				jdbcId = AdminConfig.getid('/Cell:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/Cell:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				j2eePropertyIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+propertyName).splitlines()
				for j2eePropertyId in j2eePropertyIds:
					print "j2eePropertyId@ " + j2eePropertyId
					AdminConfig.modify(j2eePropertyId, '[[name "'+propertyName+'"] [type "'+propertyType+'"] [description "'+propertyDescription+'"] [value "'+propertyValue+'"] [required "false"]]') 	
						
			if (scope == 'Cluster' or scope == 'cluster'):
				clusterId = AdminConfig.getid('/ServerCluster:'+clusterName+'/' )
				jdbcId = AdminConfig.getid('/ServerCluster:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/ServerCluster:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				j2eePropertyIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+propertyName).splitlines()
				for j2eePropertyId in j2eePropertyIds:
					print "j2eePropertyId@ " + j2eePropertyId
					AdminConfig.modify(j2eePropertyId, '[[name "'+propertyName+'"] [type "'+propertyType+'"] [description "'+propertyDescription+'"] [value "'+propertyValue+'"] [required "false"]]') 	
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()


def modifyDataSourceProperty():
		
	print 'modifyDataSourceProperty...'
	f = open(r'/tmp/DCA_CFG/modifyDataSourceProperty.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")		
			scope = strTok.nextToken().strip()
			clusterName = strTok.nextToken().strip()
			jdbcName = strTok.nextToken().strip()
			dataSourceName = strTok.nextToken().strip()
			minConnections = strTok.nextToken().strip()
			maxConnections = strTok.nextToken().strip()
			connectionTimeout = strTok.nextToken().strip()
			reapTime = strTok.nextToken().strip()
			unusedTimeout = strTok.nextToken().strip()
			agedTimeout = strTok.nextToken().strip()
			purgePolicy = strTok.nextToken().strip()
			retryInterval = strTok.nextToken().strip()
			maxRetries = strTok.nextToken().strip()
			rerouteServer = strTok.nextToken().strip()
			reroutePort = strTok.nextToken().strip()
			rerouteJNDI = strTok.nextToken().strip()
			print scope, clusterName, jdbcName, dataSourceName, minConnections, maxConnections,connectionTimeout,reapTime,unusedTimeout,agedTimeout,purgePolicy,retryInterval,maxRetries,rerouteServer,reroutePort,rerouteJNDI
			
			print 'Jython scope@' + scope	
			if (scope == 'Cell' or scope == 'cell'):
				print 'The scope is Cell'
				clusterId = AdminConfig.getid('/Cell:'+clusterName+'/' )
				jdbcId = AdminConfig.getid('/Cell:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/Cell:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				print "dataSourceId@ " + dataSourceId
				validateNewConnectionName='validateNewConnection'
				validateNewConnectionRetryCountName='validateNewConnectionRetryCount'
				validateNewConnectionRetryIntervalName='validateNewConnectionRetryInterval'
				errorDetectionModelName='errorDetectionModel'
				nonTransactionalDataSourceName = 'nonTransactionalDataSource'
				
				retryIntervalForClientRerouteName = 'retryIntervalForClientReroute'
				maxRetriesForClientRerouteName = 'maxRetriesForClientReroute'
				clientRerouteAlternatePortNumberName = 'clientRerouteAlternatePortNumber'
				clientRerouteServerListJNDIName = 'clientRerouteServerListJNDIName'
				clientRerouteAlternateServerName = 'clientRerouteAlternateServerName'	
				
				validateNewConnectionIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+validateNewConnectionName).splitlines()
				retryIntervalForClientRerouteIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+retryIntervalForClientRerouteName).splitlines()	
				maxRetriesForClientRerouteIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+maxRetriesForClientRerouteName).splitlines()	
				clientRerouteAlternateServerIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+clientRerouteAlternateServerName).splitlines()	
				clientRerouteAlternatePortNumberIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+clientRerouteAlternatePortNumberName).splitlines()	
				clientRerouteServerListJNDINameIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+clientRerouteServerListJNDIName).splitlines()	
				
				for validateNewConnectionId in validateNewConnectionIds:	
					if (validateNewConnectionId.find("/clusters/") ==-1):				
						print "validateNewConnectionId@ " + validateNewConnectionId
						AdminConfig.modify(validateNewConnectionId, '[[name "validateNewConnection"] [type "java.lang.Boolean"] [description "Setting this flag to true will cause to WebSphere Application Server to validate connections when they first get created and to keep trying to get a good connection from the database if the validation fails. Setting this flag to false prevents any additional validation from being performed - newly created connections are assumed to be valid and usable. "] [value "true"] [required "false"]]')
						AdminConfig.modify(dataSourceId, [["connectionPool", [["testConnectionInterval", "0"]]]])
						AdminConfig.modify(dataSourceId, [["connectionPool", [["testConnection", "true"]]]])
						
				for retryIntervalForClientRerouteId in retryIntervalForClientRerouteIds:	
					if (retryIntervalForClientRerouteId.find("/clusters/") ==-1):				
						print "retryIntervalForClientRerouteId@ " + retryIntervalForClientRerouteId
						AdminConfig.modify(retryIntervalForClientRerouteId, '[[name "retryIntervalForClientReroute"] [type "java.lang.Integer"] [description "The amount of time (in seconds) between automatic client reroute retries. This property is only used if the maxRetriesForClientReroute property is also set."] [value "'+maxRetries+'"] [required "false"]]') 
									
				for maxRetriesForClientRerouteId in maxRetriesForClientRerouteIds:	
					if (maxRetriesForClientRerouteId.find("/clusters/") ==-1):				
						print "maxRetriesForClientRerouteId@ " + maxRetriesForClientRerouteId
						AdminConfig.modify(maxRetriesForClientRerouteId, '[[name "maxRetriesForClientReroute"] [type "java.lang.Integer"] [description "The maximum number of connection retries attempted by automatic client reroute if the primary connection to the server fails. This property is only used if the retryIntervalClientReroute property is also set."] [value "'+retryInterval+'"] [required "false"]]') 
				
				for clientRerouteAlternateServerId in clientRerouteAlternateServerIds:	
					if (clientRerouteAlternateServerId.find("/clusters/") ==-1):				
						print "clientRerouteAlternateServerId@ " + clientRerouteAlternateServerId
						AdminConfig.modify(clientRerouteAlternateServerId, '[[name "clientRerouteAlternateServerName"] [type "java.lang.String"] [description "The list of alternate server name(s) for the DB2 server. If more than one alternate server name is specified, then the names must be separated by a comma. For example, host1,host2."] [value "'+rerouteServer+'"] [required "false"]]')
				
				for clientRerouteAlternatePortNumberId in clientRerouteAlternatePortNumberIds:	
					if (clientRerouteAlternatePortNumberId.find("/clusters/") ==-1):				
						print "clientRerouteAlternatePortNumberId@ " + clientRerouteAlternatePortNumberId
						AdminConfig.modify(clientRerouteAlternatePortNumberId, '[[name "clientRerouteAlternatePortNumber"] [type "java.lang.String"] [description "The list of alternate server port(s) for the DB2 server. If more than one alternate server port is specified, then the ports must be separated by a comma. For example, 5000,50001."] [value "'+reroutePort+'"] [required "false"]]') 

				for clientRerouteServerListJNDINameId in clientRerouteServerListJNDINameIds:	
					if (clientRerouteServerListJNDINameId.find("/clusters/") ==-1):				
						print "clientRerouteServerListJNDINameId@ " + clientRerouteServerListJNDINameId
						AdminConfig.modify(clientRerouteServerListJNDINameId, '[[name "clientRerouteServerListJNDIName"] [type "java.lang.String"] [description "The name used to bind the DB2 client reroute server list to JNDI name space."] [value "'+rerouteJNDI+'"] [required "false"]]') 
			
				#Update connection pool sizings
				pool = AdminConfig.showAttribute(dataSourceId, "connectionPool")
				AdminConfig.modify(pool, [["maxConnections", maxConnections], ["minConnections", minConnections], ["connectionTimeout",connectionTimeout], ["reapTime", reapTime], ["unusedTimeout",unusedTimeout], ["agedTimeout",agedTimeout], ["purgePolicy", purgePolicy]])
					
			if (scope == 'Cluster' or scope == 'cluster'):
				print 'The scope is Cluster'
				clusterId = AdminConfig.getid('/ServerCluster:'+clusterName+'/' )
				jdbcId = AdminConfig.getid('/ServerCluster:'+clusterName+'/JDBCProvider:' + jdbcName)
				dataSourceId = AdminConfig.getid('/ServerCluster:'+ clusterName +'/JDBCProvider:'+ jdbcName +'/DataSource:'+ dataSourceName +'/')
				print "dataSourceId@ " + dataSourceId
				validateNewConnectionName='validateNewConnection'
				validateNewConnectionRetryCountName='validateNewConnectionRetryCount'
				validateNewConnectionRetryIntervalName='validateNewConnectionRetryInterval'
				errorDetectionModelName='errorDetectionModel'
				nonTransactionalDataSourceName = 'nonTransactionalDataSource'

				retryIntervalForClientRerouteName = 'retryIntervalForClientReroute'
				maxRetriesForClientRerouteName = 'maxRetriesForClientReroute'
				clientRerouteAlternatePortNumberName = 'clientRerouteAlternatePortNumber'
				clientRerouteServerListJNDIName = 'clientRerouteServerListJNDIName'
				clientRerouteAlternateServerName = 'clientRerouteAlternateServerName'	
				
				validateNewConnectionIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+validateNewConnectionName).splitlines()
				retryIntervalForClientRerouteIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+retryIntervalForClientRerouteName).splitlines()	
				maxRetriesForClientRerouteIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+maxRetriesForClientRerouteName).splitlines()	
				clientRerouteAlternateServerIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+clientRerouteAlternateServerName).splitlines()	
				clientRerouteAlternatePortNumberIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+clientRerouteAlternatePortNumberName).splitlines()	
				clientRerouteServerListJNDINameIds = AdminConfig.getid('/JDBCProvider:'+jdbcName+'/DataSource:'+dataSourceName+'/J2EEResourcePropertySet:/J2EEResourceProperty:'+clientRerouteServerListJNDIName).splitlines()	
				
				for validateNewConnectionId in validateNewConnectionIds:	
					if (validateNewConnectionId.find("/clusters/") >=0):				
						print "validateNewConnectionId@ " + validateNewConnectionId
						AdminConfig.modify(validateNewConnectionId, '[[name "validateNewConnection"] [type "java.lang.Boolean"] [description "Setting this flag to true will cause to WebSphere Application Server to validate connections when they first get created and to keep trying to get a good connection from the database if the validation fails. Setting this flag to false prevents any additional validation from being performed - newly created connections are assumed to be valid and usable. "] [value "true"] [required "false"]]')
						AdminConfig.modify(dataSourceId, [["connectionPool", [["testConnectionInterval", "0"]]]])
						AdminConfig.modify(dataSourceId, [["connectionPool", [["testConnection", "true"]]]])
						
				for retryIntervalForClientRerouteId in retryIntervalForClientRerouteIds:	
					if (retryIntervalForClientRerouteId.find("/clusters/") >=0):				
						print "retryIntervalForClientRerouteId@ " + retryIntervalForClientRerouteId
						AdminConfig.modify(retryIntervalForClientRerouteId, '[[name "retryIntervalForClientReroute"] [type "java.lang.Integer"] [description "The amount of time (in seconds) between automatic client reroute retries. This property is only used if the maxRetriesForClientReroute property is also set."] [value "'+maxRetries+'"] [required "false"]]') 
									
				for maxRetriesForClientRerouteId in maxRetriesForClientRerouteIds:	
					if (maxRetriesForClientRerouteId.find("/clusters/") >=0):				
						print "maxRetriesForClientRerouteId@ " + maxRetriesForClientRerouteId
						AdminConfig.modify(maxRetriesForClientRerouteId, '[[name "maxRetriesForClientReroute"] [type "java.lang.Integer"] [description "The maximum number of connection retries attempted by automatic client reroute if the primary connection to the server fails. This property is only used if the retryIntervalClientReroute property is also set."] [value "'+retryInterval+'"] [required "false"]]') 
				
				for clientRerouteAlternateServerId in clientRerouteAlternateServerIds:	
					if (clientRerouteAlternateServerId.find("/clusters/") >=0):				
						print "clientRerouteAlternateServerId@ " + clientRerouteAlternateServerId
						AdminConfig.modify(clientRerouteAlternateServerId, '[[name "clientRerouteAlternateServerName"] [type "java.lang.String"] [description "The list of alternate server name(s) for the DB2 server. If more than one alternate server name is specified, then the names must be separated by a comma. For example, host1,host2."] [value "'+rerouteServer+'"] [required "false"]]')
				
				for clientRerouteAlternatePortNumberId in clientRerouteAlternatePortNumberIds:	
					if (clientRerouteAlternatePortNumberId.find("/clusters/") >=0):				
						print "clientRerouteAlternatePortNumberId@ " + clientRerouteAlternatePortNumberId
						AdminConfig.modify(clientRerouteAlternatePortNumberId, '[[name "clientRerouteAlternatePortNumber"] [type "java.lang.String"] [description "The list of alternate server port(s) for the DB2 server. If more than one alternate server port is specified, then the ports must be separated by a comma. For example, 5000,50001."] [value "'+reroutePort+'"] [required "false"]]') 

				for clientRerouteServerListJNDINameId in clientRerouteServerListJNDINameIds:	
					if (clientRerouteServerListJNDINameId.find("/clusters/") >=0):				
						print "clientRerouteServerListJNDINameId@ " + clientRerouteServerListJNDINameId
						AdminConfig.modify(clientRerouteServerListJNDINameId, '[[name "clientRerouteServerListJNDIName"] [type "java.lang.String"] [description "The name used to bind the DB2 client reroute server list to JNDI name space."] [value "'+rerouteJNDI+'"] [required "false"]]') 
			
						
				#Update connection pool sizings
				pool = AdminConfig.showAttribute(dataSourceId, "connectionPool")
				AdminConfig.modify(pool, [["maxConnections", maxConnections], ["minConnections", minConnections], ["connectionTimeout",connectionTimeout], ["reapTime", reapTime], ["unusedTimeout",unusedTimeout], ["agedTimeout",agedTimeout], ["purgePolicy", purgePolicy]])

			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def addHostAlias ():

	print 'addHostAlias...'
	f = open(r'/tmp/DCA_CFG/addHostAlias.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			hostName = strTok.nextToken().strip()
			dnsHost = strTok.nextToken().strip()
			port = strTok.nextToken().strip()
			print hostName, dnsHost, port	
			global AdminConfig, AdminControl
			#port.replace('\n', '')
			dnsHost=dnsHost.replace('all', '*')
			hostTarget = findConfigTarget(hostName, "VirtualHost")
			if (hostTarget == 0):
				print "Can not find "+hostName
				return
			  #endIf

			# determine whether alias exists
			oNeedToDefine = 1
			aliasList = AdminConfig.list("HostAlias", hostTarget).splitlines()
			if (aliasList != ['']):
				for HAEntry in aliasList:
					oHostName = AdminConfig.showAttribute(HAEntry, "hostname")
					oPort = AdminConfig.showAttribute(HAEntry, "port")
					if oHostName == dnsHost:
						if oPort == port:
							print "The hostname "+hostName+ " has already defined host alias: "+HAEntry
							print "New entry will not be added."
							oNeedToDefine = 0
							break 
						#endIf 
					#endIf 
				#endFor 
			#endIf

			if (oNeedToDefine == 1):
				attrHA = [["hostname", dnsHost], ["port", port]]
				print "Adding Host Alias to "+hostName
				try:
					_excp_ = 0
					hAlias = AdminConfig.create( "HostAlias", hostTarget, attrHA )
				except:
					_type_, _value_, _tbck_ = sys.exc_info()
					hAlias = `_value_`
					_excp_ = 1
				#endTry 
				if (_excp_ ):
					print "Caught Exception creating host alias"
					print hAlias
					return
				#endIf 
	
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

def createSIBus ():
	
	print 'createSIBus...'
	f = open(r'/tmp/DCA_CFG/createSIBus.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			busName = strTok.nextToken().strip()
			print busName		
			SIBus = AdminConfig.getid("/SIBus:"+busName+"/" )
			if (SIBus == ""):
				parms = ["-bus", busName, "-busSecurity false"]
				SIBus = AdminTask.createSIBus(parms )
						
				print busName + " created successfully!"
			else:
				print busName + " already exists!"
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def addSIBusMember():

	print 'addSIBusMember...'
	f = open(r'/tmp/DCA_CFG/addSIBusMember.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			busName = strTok.nextToken().strip()
			targetArgs = strTok.nextToken().strip()
			JNDIName = strTok.nextToken().strip()
			authAlias = strTok.nextToken().strip()
			schemaName = strTok.nextToken().strip()
			print busName, targetArgs, JNDIName,authAlias,schemaName			
			AdminTask.addSIBusMember("[-bus "+busName+" -cluster "+targetArgs+" -enableAssistance true -policyName HA -dataStore -createDefaultDatasource false -datasourceJndiName "+JNDIName+" -authAlias "+authAlias+" -createTables true -restrictLongDBLock false -schemaName "+schemaName+" ]")			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
	
def createSIBForeignBus():

	print 'createSIBForeignBus...'
	f = open(r'/tmp/DCA_CFG/createSIBForeignBus.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			busName = strTok.nextToken().strip()
			fBusName = strTok.nextToken().strip()
			messagingEngine = strTok.nextToken().strip()
			MQLinkName = strTok.nextToken().strip()
			senderChannel = strTok.nextToken().strip()
			hostName = strTok.nextToken().strip()
			port = strTok.nextToken().strip()
			receiverChannel = strTok.nextToken().strip()
			print busName, fBusName ,messagingEngine ,MQLinkName ,senderChannel ,hostName ,port ,receiverChannel			
			hostName=hostName.replace("|", ",")		
			AdminTask.createSIBForeignBus('[-bus '+busName+' -name '+fBusName+' -routingType Direct -type MQ ]')
			AdminTask.createSIBMQLink('[-bus '+busName+' -messagingEngine '+messagingEngine+' -name '+MQLinkName+' -foreignBusName '+fBusName+' -queueManagerName '+busName+' -adoptable true -preferLocal true -senderChannelTransportChain OutboundBasicMQLink -senderChannelName '+senderChannel+' -connameList '+hostName+' -receiverChannelName '+receiverChannel+']') 		 
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createSIBDestination():

	print 'createSIBDestination...'
	f = open(r'/tmp/DCA_CFG/createSIBDestination.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			busName = strTok.nextToken().strip()
			desName = strTok.nextToken().strip()
			fBusName = strTok.nextToken().strip()
			qType = strTok.nextToken().strip()
			cluster = strTok.nextToken().strip()
			print busName, desName, fBusName, qType, cluster			
			if (qType == "Foreign"):
				AdminTask.createSIBDestination('[-name '+desName+' -foreignBus '+fBusName+' -type '+qType+' -reliability ASSURED_PERSISTENT -maxReliability ASSURED_PERSISTENT -overrideOfQOSByProducerAllowed true -sendAllowed true -description -bus '+busName+' ]') 
			else :
				AdminTask.createSIBDestination("[-bus "+busName+" -name "+desName+" -type "+qType+" -reliability ASSURED_PERSISTENT -description -cluster "+cluster+" ]")	
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createJMSQueue():

	print 'createJMSQueue...'
	f = open(r'/tmp/DCA_CFG/createJMSQueue.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			deliveryMode = strTok.nextToken().strip()
			busName = strTok.nextToken().strip()
			queueName = strTok.nextToken().strip()
			connectQueueName = strTok.nextToken().strip()
			print clusterName, jndiName, deliveryMode, busName, queueName, connectQueueName
			
			clusterId = AdminConfig.getid('/ServerCluster:'+clusterName+'/' )
			AdminTask.createSIBJMSQueue(clusterId, '[-name '+queueName+' -jndiName '+jndiName+' -description -deliveryMode '+deliveryMode+' -readAhead AsConnection -busName '+busName+' -queueName '+connectQueueName+' -scopeToLocalQP false -producerBind false -producerPreferLocal true -gatherMessages false]') 
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
	
def createWMQQueue():

	print 'createWMQQueue...'
	f = open(r'/tmp/DCA_CFG/createWMQQueue.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			wmqqName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			queueName = strTok.nextToken().strip()
			ccsid = strTok.nextToken().strip()
			useNativeEncoding = strTok.nextToken().strip()
			print clusterName, wmqqName, jndiName, queueName, ccsid, useNativeEncoding			
			clusterId = AdminConfig.getid('/ServerCluster:'+clusterName+'/' )	
			cellName = AdminControl.getCell()	
			AdminTask.createWMQQueue(clusterId, '[-name '+wmqqName+' -jndiName '+jndiName+' -queueName '+queueName+' -qmgr  -description -ccsid '+ccsid+' -useNativeEncoding '+useNativeEncoding+']') #-ccsid '+ccsid+' -useNativeEncoding '+useNativeEncoding+'
				
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
		
	
def createSIBJMSConnectionFactory():

	print 'createSIBJMSConnectionFactory...'
	f = open(r'/tmp/DCA_CFG/createSIBJMSConnectionFactory.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			queueName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			busName = strTok.nextToken().strip()
			print clusterName, queueName, jndiName, busName			
			clusterId = AdminConfig.getid('/ServerCluster:'+clusterName+'/' )
			AdminTask.createSIBJMSConnectionFactory(clusterId, '[-type queue -name '+queueName+' -jndiName '+jndiName+' -description -category -busName '+busName+' -nonPersistentMapping ExpressNonPersistent -readAhead Default -tempQueueNamePrefix -target -targetType BusMember -targetSignificance Preferred -targetTransportChain -providerEndPoints -connectionProximity Bus -authDataAlias -containerAuthAlias -mappingAlias -shareDataSourceWithCMP false -logMissingTransactionContext false -manageCachedHandles false -xaRecoveryAuthAlias -persistentMapping ReliablePersistent -consumerDoesNotModifyPayloadAfterGet false -producerDoesNotModifyPayloadAfterSet false]') 					
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createWMQConnectionFactory():
	
	print 'createWMQConnectionFactory...'
	f = open(r'/tmp/DCA_CFG/createWMQConnectionFactory.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			queueName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			qmgrName = strTok.nextToken().strip()
			qmgrSvrconnChannel = strTok.nextToken().strip()
			connectionNameList = strTok.nextToken().strip()
			print clusterName, queueName, jndiName, qmgrName, qmgrSvrconnChannel, connectionNameList			
			connectionNameList=connectionNameList.replace("|", ",")	
			cellName = AdminControl.getCell()			
			AdminTask.createWMQConnectionFactory('"WebSphere MQ JMS Provider(cells/'+cellName+'/clusters/'+clusterName+'|resources.xml#builtin_mqprovider)"', '[-type QCF -name '+queueName+' -jndiName '+jndiName+' -description -qmgrName '+qmgrName+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+qmgrSvrconnChannel+' -connectionNameList '+connectionNameList+' ]') 
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def modifyWMQConnectionFactory():
	
	print 'modifyWMQConnectionFactory...'
	f = open(r'/tmp/DCA_CFG/modifyWMQConnectionFactory.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			queueName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			qmgrName = strTok.nextToken().strip()
			qmgrSvrconnChannel = strTok.nextToken().strip()
			connectionNameList = strTok.nextToken().strip()
			containerAuthAlias = strTok.nextToken().strip()
			maxConnections = strTok.nextToken().strip()
			minConnections = strTok.nextToken().strip()
			print clusterName, queueName, jndiName, qmgrName, qmgrSvrconnChannel, connectionNameList, containerAuthAlias, maxConnections, minConnections			
			connectionNameList=connectionNameList.replace("|", ",")	
			cellName = AdminControl.getCell()
			MS=AdminConfig.getid('/ServerCluster:'+ clusterName +'/JMSProvider:WebSphere MQ JMS Provider/')
			qfid=AdminConfig.getid('/ServerCluster:'+ clusterName +'/JMSProvider:WebSphere MQ JMS Provider/MQQueueConnectionFactory:'+ queueName +'/')			
			print "Jython qfid@ " + qfid			
			AdminTask.modifyWMQConnectionFactory(qfid, '[-name '+queueName+' -jndiName '+jndiName+' -description -qmgrName '+qmgrName+' -wmqTransportType CLIENT -connectionNameList '+connectionNameList+' -qmgrSvrconnChannel '+qmgrSvrconnChannel+' -sslType NONE -clientId -providerVersion -mappingAlias DefaultPrincipalMapping -containerAuthAlias '+containerAuthAlias+' -componentAuthAlias -xaRecoveryAuthAlias '+containerAuthAlias+' -support2PCProtocol true ]') 																																												  #[-name Queue Connection Factory for BatchProcess -jndiName jms/eaiqm_qcf -description -qmgrName RMS_QM -wmqTransportType CLIENT -connectionNameList sermsmq01.cpall.co.th(1414),sermsmq02.cpall.co.th(1414) -qmgrSvrconnChannel MMMOP.SVRCONN -sslType NONE -clientId -providerVersion -mappingAlias DefaultPrincipalMapping -containerAuthAlias sewtsmn01DmgrNode01/wascdc -componentAuthAlias -xaRecoveryAuthAlias sewtsmn01DmgrNode01/wascdc -support2PCProtocol true ]
			#Update connection pool sizings
			pool = AdminConfig.showAttribute(qfid, "connectionPool")
			AdminConfig.modify(pool, [["maxConnections", maxConnections], ["minConnections", minConnections]])
		
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def createSIBJMSActivationSpec():
	
	print 'createSIBJMSActivationSpec...'
	f = open(r'/tmp/DCA_CFG/createSIBJMSActivationSpec.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			specName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			desJndiName = strTok.nextToken().strip()
			messageSelector = strTok.nextToken().strip()
			busName = strTok.nextToken().strip()
			subHome = strTok.nextToken().strip()
			maxBatchSize = strTok.nextToken().strip()
			maxConcurrency = strTok.nextToken().strip()
			print clusterName, specName, jndiName, desJndiName, messageSelector, busName, subHome, maxBatchSize, maxConcurrency
			cellName = AdminControl.getCell()
			messageSelector=messageSelector.replace("|", "\'")	
			cellName = AdminControl.getCell()		
			AdminTask.createSIBJMSActivationSpec(clusterName+'(cells/'+cellName+'/clusters/'+clusterName+'|cluster.xml)', '[ -name '+specName+' -jndiName '+jndiName+'  -destinationJndiName '+desJndiName+' -description -busName '+busName+' -clientId -durableSubscriptionHome '+subHome+' -destinationType javax.jms.Queue -messageSelector [_progId_='+messageSelector+'] -acknowledgeMode Auto-acknowledge -subscriptionName -maxBatchSize '+maxBatchSize+' -maxConcurrency '+maxConcurrency+'  -subscriptionDurability NonDurable -shareDurableSubscriptions InCluster -authenticationAlias -readAhead Default -target -targetType BusMember -targetSignificance Preferred -targetTransportChain -providerEndPoints -shareDataSourceWithCMP false -consumerDoesNotModifyPayloadAfterGet false -forwarderDoesNotModifyPayloadAfterSet false -alwaysActivateAllMDBs false -retryInterval 30 -autoStopSequentialMessageFailure 0 -failingMessageDelay 0]')	
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
		
def createWMQActivationSpec():
	
	print 'createWMQActivationSpec...'
	f = open(r'/tmp/DCA_CFG/createWMQActivationSpec.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			specName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			desJndiName = strTok.nextToken().strip()
			qmgrName = strTok.nextToken().strip()
			qmgrSvrconnChannel = strTok.nextToken().strip()
			connectionNameList = strTok.nextToken().strip()
			rescanInterval = strTok.nextToken().strip()
			ccsid = strTok.nextToken().strip()
			failIfQuiescing = strTok.nextToken().strip()
			maxPoolSize = strTok.nextToken().strip()
			poolTimeout = strTok.nextToken().strip()
			stopEndpointIfDeliveryFails = strTok.nextToken().strip()
			messageRetention = strTok.nextToken().strip()
			print clusterName, specName, jndiName, desJndiName, qmgrName, qmgrSvrconnChannel, connectionNameList, rescanInterval, ccsid, failIfQuiescing, maxPoolSize, poolTimeout, stopEndpointIfDeliveryFails, messageRetention				  
			connectionNameList=connectionNameList.replace("|", ",")	
			cellName = AdminControl.getCell()
			AdminTask.createWMQActivationSpec('"WebSphere MQ JMS Provider(cells/'+cellName+'/clusters/'+clusterName+'|resources.xml#builtin_mqprovider)"', '[-name '+specName+' -jndiName '+jndiName+' -description -destinationJndiName '+desJndiName+' -destinationType javax.jms.Queue -messageSelector -qmgrName '+qmgrName+' -wmqTransportType BINDINGS_THEN_CLIENT -qmgrSvrconnChannel '+qmgrSvrconnChannel+' -connectionNameList '+connectionNameList+' -rescanInterval '+rescanInterval+' -ccsid '+ccsid+' -failIfQuiescing '+failIfQuiescing+' -maxPoolSize '+maxPoolSize+' -poolTimeout '+poolTimeout+' -stopEndpointIfDeliveryFails '+stopEndpointIfDeliveryFails+' -msgRetention '+messageRetention+' ]') 			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def modifyWMQActivationSpec():
	
	print 'modifyWMQActivationSpec...'
	f = open(r'/tmp/DCA_CFG/modifyWMQActivationSpec.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			specName = strTok.nextToken().strip()
			authAlias = strTok.nextToken().strip()
			propName = strTok.nextToken().strip()
			propType = strTok.nextToken().strip()
			propDesc = strTok.nextToken().strip()
			propValue = strTok.nextToken().strip()
			required = strTok.nextToken().strip()
			print clusterName, specName, authAlias, propName, propType ,propDesc, propValue, required
			
			specIds = AdminConfig.getid("/J2CActivationSpec:" + specName + "/").splitlines()
			for specId in specIds:		
				if (specId.find("/clusters/"+clusterName) >=0):
					print "Jython clusterName@ " + clusterName
					print "Jython specId@ " + specId
					
					AdminTask.modifyWMQActivationSpec(specId, '[ -authAlias '+authAlias+' ]') 
					resourceProps = AdminConfig.list("J2EEResourceProperty", specId).splitlines()
					for resourceProp in resourceProps:
						if (resourceProp.find(propName) >=0):
							print "Jython J2EEResourceProperty@ " + resourceProp
							AdminConfig.modify(resourceProp, '[[name '+propName+'] [type '+propType+'] [description '+propDesc+'] [value '+propValue+'] [required '+required+']]')
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
				
def createWebsphereVariable():

	print 'createWebsphereVariable...'
	f = open(r'/tmp/DCA_CFG/createWebsphereVariable.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			scope = strTok.nextToken().strip()
			scopeName = strTok.nextToken().strip()
			symbolicName = strTok.nextToken().strip()
			value = strTok.nextToken().strip()
			print scope, scopeName, symbolicName, value		
			cellName = AdminControl.getCell()
			variableMaps = AdminConfig.list("VariableMap").split();
			VariableSubstitutionEntry = AdminConfig.list("VariableSubstitutionEntry").split();			
			created=0
			modified=0				
			if (scope == 'Cell' or scope == 'cell'):
				print 'Cell Scope'
				for variableMap in variableMaps:
					for vEntry in VariableSubstitutionEntry:
						if (variableMap.find('cells/'+scopeName+'|variables.xml#VariableMap_1') >=0):						
							name = AdminConfig.showAttribute(vEntry, "symbolicName")

							if (modified==0 and created==0):	
								print 'Create'
								print 'name@ ' + name
								print 'symbolicName@ ' + symbolicName
								params = [];
								params.append(["symbolicName", symbolicName]);
								params.append(["value", value]);
								AdminConfig.create('VariableSubstitutionEntry', variableMap, params)
								created=1				
				
			if (scope == 'Node' or scope == 'node'):
				for vEntry in VariableSubstitutionEntry:
					if (vEntry.find("/nodes/") >=0 and vEntry.find("/nodeagent|") ==-1 and vEntry.find("/servers/") ==-1):
						name = AdminConfig.showAttribute(vEntry, "symbolicName")			
						if (name.find(symbolicName) >=0 and vEntry.find(scopeName) >=0):
							params = [];
							params.append(["symbolicName", symbolicName]);
							params.append(["value", value]);
							if modified==0:
								AdminConfig.modify(vEntry, params);
								modified=1
						else:
							for variableMap in variableMaps:
								if (variableMap.find("/nodes/") >=0 and variableMap.find("/nodeagent|") ==-1 and variableMap.find("Dmgr") ==-1 and variableMap.find("/servers/") ==-1):
									if (variableMap.find(scopeName) >=0):
										params = [];
										params.append(["symbolicName", symbolicName]);
										params.append(["value", value]);
										if created==0:
											AdminConfig.create('VariableSubstitutionEntry', variableMap, params) 
											created=1
										#AdminConfig.create('VariableSubstitutionEntry', '(cells/STA_Cell/nodes/sepa2tt01Node01|variables.xml#VariableMap_1)', '[[symbolicName "ORACLE_JDBC_DRIVER_PATH"] [description ""] [value "/opt/IBM/WebSphere/AppServer/lib/ext/oracle"]]') 
											
			if (scope == 'Cluster' or scope == 'cluster'):
				for variableMap in variableMaps:
					if (variableMap.find(scopeName) >=0):
						for vEntry in VariableSubstitutionEntry:
							name = AdminConfig.showAttribute(vEntry, "symbolicName")
							if (name == symbolicName):		
								print 'Jython vEntry@' + vEntry
								params = [];
								params.append(["symbolicName", symbolicName]);
								params.append(["value", value]);
								if (created==0 and modified==0):
									print 'Modify'
									print 'name@ ' + name
									print 'symbolicName@ ' + symbolicName
									AdminConfig.modify(vEntry, params) 
									modified=1						
							else:
								if (created==0 and modified==0):
									print 'Jython vEntry@' + vEntry
									print 'Create'
									print 'name@ ' + name
									print 'symbolicName@ ' + symbolicName
									params = [];
									params.append(["symbolicName", symbolicName]);
									params.append(["value", value]);
									AdminConfig.create('VariableSubstitutionEntry', variableMap, params)
									created=1			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def enableCPALLLDAP():

	cellName = AdminControl.getCell()
	securityConfigID = AdminConfig.getid('/Cell:'+cellName+'/Security:/')
	AdminConfig.modify(securityConfigID,[['appEnabled','true']])
	
	AdminTask.configureAdminWIMUserRegistry('[-verifyRegistry true ]') 
	
	AdminTask.createIdMgrLDAPRepository('[-default true -id LDAP -adapterClassName com.ibm.ws.wim.adapter.ldap.LdapAdapter -ldapServerType AD -sslConfiguration -certificateMapMode exactdn -supportChangeLog none -certificateFilter -loginProperties uid]')
	AdminTask.addIdMgrLDAPServer('[-id LDAP -host tarldap.cpall.co.th -bindDN CN=gowasadmin,OU=Productions,OU=SystemAccounts,DC=7eleven,DC=cp,DC=co,DC=th -bindPassword lbmTbNcvHf,bo -referal ignore -sslEnabled false -ldapServerType AD -sslConfiguration -certificateMapMode exactdn -certificateFilter -authentication simple -port 389]') 
	
	AdminTask.addIdMgrRepositoryBaseEntry('[-id LDAP -name o=adsLDAP -nameInRepository dc=7eleven,dc=cp,dc=co,dc=th]')
	AdminTask.addIdMgrRealmBaseEntry('[-name defaultWIMFileBasedRealm -baseEntry o=adsLDAP]') 
	
	AdminConfig.save() 
			
def enableSecurityLDAP(primaryUser ,ldapPrimaryHost, bindPassword, ldapPort, ldapServerType, baseDN, bindDN):
	
	bindDN = bindDN+',OU=Productions,OU=SystemAccounts,DC=7eleven,DC=cp,DC=co,DC=th'
	nameInRepository = 'dc=7eleven,dc=cp,dc=co,dc=th'
	bindPassword = bindPassword.replace('|', ',')
	
	print "Jython primaryUser@ " + primaryUser
	print "Jython ldapPrimaryHost@ " + ldapPrimaryHost
	print "Jython bindDN@ " + bindDN
	print "Jython bindPassword@ " + bindPassword
	print "Jython ldapPort@ " + ldapPort
	print "Jython ldapServerType@ " + ldapServerType
	print "Jython baseDN@ " + baseDN
	print "Jython nameInRepository@ " + nameInRepository
	
	cellName = AdminControl.getCell()
	securityConfigID = AdminConfig.getid('/Cell:'+cellName+'/Security:/')
	AdminConfig.modify(securityConfigID,[['appEnabled','true']])
	
	AdminTask.configureAdminWIMUserRegistry('[-verifyRegistry true ]') 
	
	AdminTask.createIdMgrLDAPRepository('[-default true -id LDAP -adapterClassName com.ibm.ws.wim.adapter.ldap.LdapAdapter -ldapServerType AD -sslConfiguration -certificateMapMode exactdn -supportChangeLog none -certificateFilter -loginProperties uid]')
	AdminTask.addIdMgrLDAPServer('[-id LDAP -host '+ldapPrimaryHost+' -bindDN '+bindDN+' -bindPassword '+bindPassword+' -referal ignore -sslEnabled false -ldapServerType '+ldapServerType+' -sslConfiguration -certificateMapMode exactdn -certificateFilter -authentication simple -port '+ldapPort+']') 
	
	AdminTask.addIdMgrRepositoryBaseEntry('[-id LDAP -name '+baseDN+' -nameInRepository '+nameInRepository+']')
	AdminTask.addIdMgrRealmBaseEntry('[-name defaultWIMFileBasedRealm -baseEntry '+baseDN+']') 
	
	AdminConfig.save() 
	
def createUser():

	print 'createUser...'
	f = open(r'/tmp/DCA_CFG/createUser.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			userName = strTok.nextToken().strip()
			password = strTok.nextToken().strip()
			roleName = strTok.nextToken().strip()
			print userName, password, roleName			
			AdminTask.createUser ('[-uid %s -password %s -confirmPassword %s -cn %s -sn %s]' %(userName,password,password,userName,userName))
			AdminTask.mapUsersToAdminRole('[-accessids [user:defaultWIMFileBasedRealm/uid=%s ,o=defaultWIMFileBasedRealm ] -userids [%s] -roleName %s]' %(userName,userName,roleName)) 				
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()	
	
def mapUsersToAdminRole():

	print 'mapUsersToAdminRole...'
	f = open(r'/tmp/DCA_CFG/mapUsersToAdminRole.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			userName = strTok.nextToken().strip()
			roleName = strTok.nextToken().strip()
			print userName, roleName			
			AdminTask.mapUsersToAdminRole('[-accessids [user:defaultWIMFileBasedRealm/uid='+userName+',o=defaultWIMFileBasedRealm ] -userids ['+userName+' ] -roleName '+roleName+']') 			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
		
def createGroup():

	print 'createGroup...'
	f = open(r'/tmp/DCA_CFG/createGroup.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			groupName = strTok.nextToken().strip()
			print groupName				
			AdminTask.createGroup ('[-cn '+groupName+' -description]')			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def mapGroupsToAdminRole():

	print 'mapGroupsToAdminRole...'
	f = open(r'/tmp/DCA_CFG/mapGroupsToAdminRole.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			groupName = strTok.nextToken().strip()
			roleName = strTok.nextToken().strip()
			print groupName, roleName			
			AdminTask.mapGroupsToAdminRole('[-roleName '+roleName+' -accessids ["group:defaultWIMFileBasedRealm/CN='+groupName+',OU=Global Group,OU=Groups,o=adsLDAP" ] -groupids ["'+groupName+'@defaultWIMFileBasedRealm" ]]') 			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

def createWebServer():

	print 'createWebServer...'
	f = open(r'/tmp/DCA_CFG/createIHS_no_WAS.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			nodeName = strTok.nextToken().strip()
			webServerName = strTok.nextToken().strip()
			configDir = strTok.nextToken().strip()
			webPort = strTok.nextToken().strip()
			adminUserID = strTok.nextToken().strip()
			adminPasswd = strTok.nextToken().strip()
			print nodeName, webServerName, configDir , webPort, adminUserID, adminPasswd	
			IHS_port="80"
			adminPort='8008'
			IHS_Install_root='/opt/IBM/WebSphere/HTTPServer'
			dmgr_config ='/opt/IBM/WebSphere/Profiles/DefaultDmgr01/config'
			IHS_Plugin_Path='/opt/IBM/WebSphere/Plugins'
			IHS_Config_Path='/opt/IBM/WebSphere/HTTPServer/'+configDir+'/httpd.conf'
			IHS_WindowsServiceName=""
			IHS_ErrorLog_Path="" #"/opt/IBM/HTTPServer/logs/error_log"
			IHS_AccessLog_Path="" #"/opt/IBM/HTTPServer/logs/access_log"
			IHS_WebProtocol="HTTP"			
			AdminTask.createWebServer(nodeName, '[-name '+ webServerName+ ' -templateName IHS -serverConfig [-webPort ' + webPort + ' -serviceName -webInstallRoot ' + IHS_Install_root + ' -webProtocol HTTP -configurationFile -errorLogfile -accessLogfile -pluginInstallRoot '+ IHS_Plugin_Path + ' -webAppMapping ALL] -remoteServerConfig [-adminPort '+adminPort+' -adminUserID ' + adminUserID +' -adminPasswd  '+ adminPasswd + ' -adminProtocol HTTP]]')			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def configWebServer():

	print 'configWebServer...'
	f = open(r'/tmp/DCA_CFG/createIHS_no_WAS.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			nodeName = strTok.nextToken().strip()
			webServerName = strTok.nextToken().strip()
			configDir = strTok.nextToken().strip()
			print nodeName, webServerName, configDir			
			serverIds=AdminConfig.getid("/WebServer:" + webServerName).splitlines()	
			for serverId in serverIds:
				print "Jython serverId@ " + serverId
				print "Jython configDir@ " + configDir			
				webInstallRoot = '${WEB_INSTALL_ROOT}/'+configDir+'/httpd.conf'
				print "Jython webInstallRoot@" + webInstallRoot
				AdminConfig.modify(serverId, '[[configurationFilename "'+webInstallRoot+'"] [webserverInstallRoot "/opt/IBM/WebSphere/HTTPServer"]]')				
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

	
def createSIBContextInfo():

	print 'createSIBContextInfo...'
	f = open(r'/tmp/DCA_CFG/createSIBContextInfo.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			contextName = strTok.nextToken().strip()
			contextType = strTok.nextToken().strip()
			contextValue = strTok.nextToken().strip()
			print contextName, contextType, contextValue
			destLists = AdminConfig.list("SIBDestination").splitlines()
			result = []
			for destList in destLists:
				print "Jython destLists@ " + destList
				AdminConfig.create('SIBContextInfo', destList, '[[name '+contextName+'] [type '+contextType+'] [value '+contextValue+']]') 
			
			fdestLists = AdminConfig.list("SIBDestinationForeign").splitlines()
			for fdestList in fdestLists:
				print "Jython foreign destLists@ " + fdestList
				AdminConfig.create('SIBContextInfo', fdestList, '[[name '+contextName+'] [type '+contextType+'] [value '+contextValue+']]') 
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def modifySIBDestination():

	print 'modifySIBDestination...'
	f = open(r'/tmp/DCA_CFG/modifySIBDestination.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			busName = strTok.nextToken().strip()
			destName = strTok.nextToken().strip()
			point1 = strTok.nextToken().strip()
			point2 = strTok.nextToken().strip()
			print busName, destName, point1, point2					
			params = [];
			params.append([point1, point2]);		
			AdminTask.modifySIBDestination(["-bus", busName, "-name", destName, "-defaultForwardRoutingPath", params])			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createJVMCustomProperties():

	print 'createJVMCustomProperties...'
	f = open(r'/tmp/DCA_CFG/createJVMCustomProperties.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			propName = strTok.nextToken().strip()
			propValue = strTok.nextToken().strip()
			print clusterName, propName, propValue			
			jvms = AdminConfig.list('JavaVirtualMachine').splitlines()	
			for jvm in jvms:
				if (jvm.find('dynamicclusters') >=0 and jvm.find(clusterName) >=0):
					print 'Jython jvm' + jvm
					AdminConfig.create('Property', jvm, '[[validationExpression ""] [name "' + propName + '"] [description ""] [value ' + propValue + '] [required "false"]]')
					
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()


def createScheduler():
	
	print 'createScheduler...'
	f = open(r'/tmp/DCA_CFG/createScheduler.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			scheName = strTok.nextToken().strip()
			pollInterval = strTok.nextToken().strip()
			tablePrefix = strTok.nextToken().strip()
			datasourceJNDIName = strTok.nextToken().strip()
			datasourceAlias = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			workManager = strTok.nextToken().strip()
			print clusterName, scheName, pollInterval, tablePrefix, datasourceJNDIName, datasourceAlias, jndiName, workManager
			
			cellName = AdminControl.getCell()
			schedulerIds = 	 AdminConfig.getid('/Cell:'+cellName+'/ServerCluster:'+clusterName+'/SchedulerProvider:SchedulerProvider/')
			AdminConfig.create('SchedulerConfiguration', schedulerIds, '[[name "'+scheName+'"] [pollInterval '+pollInterval+'] [tablePrefix '+tablePrefix+'] [category ""] [datasourceJNDIName '+datasourceJNDIName+']  [useAdminRoles "false"] [datasourceAlias '+datasourceAlias+'] [jndiName '+jndiName+'] [workManagerInfoJNDIName '+workManager+'] [description ""]]') 
			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()

def createWorkManager():
	
	print 'createWorkManager...'
	f = open(r'/tmp/DCA_CFG/createWorkManager.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			wmName = strTok.nextToken().strip()
			jndiName = strTok.nextToken().strip()
			maxThreads = strTok.nextToken().strip()
			numAlarmThreads = strTok.nextToken().strip()
			isGrowable = strTok.nextToken().strip()
			workReqQFullAction = strTok.nextToken().strip()
			workReqQSize = strTok.nextToken().strip()
			print clusterName, wmName, jndiName, maxThreads, numAlarmThreads, isGrowable, workReqQFullAction, workReqQSize
			cellName = AdminControl.getCell()
			workManagerIds = AdminConfig.getid('/Cell:'+cellName+'/ServerCluster:'+clusterName+'/WorkManagerProvider:WorkManagerProvider/')
			AdminConfig.create('WorkManagerInfo', workManagerIds, '[[name "'+wmName+'"] [workReqQFullAction '+workReqQFullAction+'] [minThreads "0"] [category ""] [defTranClass ""] [daemonTranClass ""] [numAlarmThreads '+numAlarmThreads+'] [workReqQSize '+workReqQSize+'] [jndiName '+jndiName+'] [maxThreads '+maxThreads+'] [serviceNames ""] [isGrowable '+isGrowable+'] [threadPriority "5"] [description ""] [workTimeout "0"] ]') 					
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createWCCustomProperties():

	print 'createWCCustomProperties...'
	f = open(r'/tmp/DCA_CFG/createWCCustomProperties.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			propName = strTok.nextToken().strip()
			propValue = strTok.nextToken().strip()
			print clusterName, propName, propValue			
			cellName = AdminControl.getCell()
			AdminConfig.create('Property', '(cells/'+cellName+'/dynamicclusters/'+clusterName+'/servers/'+clusterName+'|server.xml#WebContainer_1)', '[[validationExpression ""] [name "'+propName+'"] [description ""] [value "'+propValue+'"] [required "false"]]') 			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	
def createASCustomProperties():

	print 'createASCustomProperties...'
	f = open(r'/tmp/DCA_CFG/createASCustomProperties.csv')
	skiphead = 0
	for user in f.readlines():
		if (skiphead >= 1 and user.strip()):
			strTok = StringTokenizer(user, ",")			
			clusterName = strTok.nextToken().strip()
			specName = strTok.nextToken().strip()
			propName = strTok.nextToken().strip()
			propValue = strTok.nextToken().strip()
			propType = strTok.nextToken().strip()
			propDesc = strTok.nextToken().strip()
			required = strTok.nextToken().strip()
			print clusterName, specName, propName, propValue, propType, propDesc, required
			
			specIds = AdminConfig.getid("/J2CActivationSpec:" + specName + "/").splitlines()
			for specId in specIds:		
				if (specId.find("/clusters/"+clusterName) >=0):
					print "Jython clusterName@ " + clusterName
					print "Jython specId@ " + specId					
					AdminConfig.create('J2EEResourceProperty', specId, '[[name "'+propName+'"] [type "'+propType+'"] [description "'+propName+'"] [value "'+propValue+'"] [required "'+required+'"]]')  			
		skiphead = skiphead + 1
	AdminConfig.save()
	f.close()
	

	
####### ########### End Adding for CPALL
# </ND IWD>
