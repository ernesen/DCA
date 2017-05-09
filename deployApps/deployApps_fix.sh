#!/bin/sh

. /etc/virtualimage.properties
SCRIPT_DIR=${SCRIPT_DIR:-`pwd`}
. $SCRIPT_DIR/DCA_libraries.sh

DEBUG set -x
# Log environment
echoLog "********** Logging Environment Variables ***********"
#set
echoLog "****************************************************"
echoLog "============== $0 ======================"

####### ########### Start Adding for CPALL
#DCA Deploys WAS applications for CPALL
#Version 2.0
#Built Date 27 April 2016 by IBM Software Services Thailand

#comma separated value 
IFS=","

#Note. The following configuration related to configure Dynamic Cluster
#_createNodeGroup
#_addNodeGroupMember
#_createCoreGroup
#_createTemplateCluster
#_modifyServerPort
#_createDynamicCluster
#_setJVMPropertiesNode
#_setJVMPropertiesCluster
#restart_was
#_modifyThreadPool
#_modifyTransactionLog
#_createEnvironmentEntries
#_createJVMCustomProperties
#_setJVMLogNode
#_setJVMLogCluster
#_modifyProcessExecutionNode
#_modifyProcessExecutionCluster
#_createWCCustomProperties
#Note. The following configuration related to configure Data Source
#_createJAASAuthData
#_createXADataSource
#_createXADataSourceOracle
#_modifyCPCustomProperties
#_modifyDataSourceProperty
#_createWorkManager
#_createScheduler
#Note. The following configuration related to configure SIBus
#_createSIBus
#_addSIBusMember
#_createSIBForeignBus
#_createSIBDestination
#_modifySIBDestination
#_createSIBContextInfo
#Note. The following configuration related to configure ConnectionFactory
#_createSIBJMSConnectionFactory
#_createWMQConnectionFactory
#_modifyWMQConnectionFactory
#Note. The following configuration related to configure Queues
#_createJMSQueue
#_createWMQQueue
#Note. The following configuration related to configure ActivationSpec
#_createSIBJMSActivationSpec
#_createWMQActivationSpec
#_modifyWMQActivationSpec
#_createASCustomProperties
#_createWebsphereVariable
#Note. The following configuration related to configure Security
#_addHostAlias
#_enableCPALLLDAP
#_createUser
#_createGroup
#_mapUsersToAdminRole
#_mapGroupsToAdminRole
#Note. The following configuration related to configure WebServer
#_createWebServer
#_configWebServer

#_syncNode
#restart_was

#Enter fix fuction here...

_setJVMPropertiesNode

DEBUG set +x

####### ########### End Adding for CPALL
