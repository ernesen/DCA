#!/bin/sh

# ln -s EXISTING_FILE SYMLINK_FILE
# ln -s /opt/CFG/Shared/ /opt/IBM/WebSphere/HTTPServer/htdocs/Shared

: '
#########
# history
# http://aix4admins.blogspot.sg/2011/08/user-administration-related-files-login.html
# http://www.unixmantra.com/2013/04/using-traps-in-your-scripts.html
# Hisotry:
# 08-01-2016 createSIBContextInfo
# 08-01-2016 modifySIBDestination
# 08-01-2016 configWebServer
# 08-01-2016 createWebServer
# 08-01-2016 mapGroupsToAdminRole
# 08-01-2016 mapUsersToAdminRole
# 08-01-2016 enableCPALLLDAP
# 08-01-2016 createSIBJMSActivationSpec
# 08-01-2016 createJMSQueue
# 31-12-2015 set_profile
# 31-12-2015 set_resolv
# 29-12-2015 list_users v2
# 29-12-2015 createJMSConnectionFactory
# 29-12-2015 createJMS
# 29-12-2015 setJVMLog
# 29-12-2015 createEnvironmentEntries
# 29-12-2015 createAuthorizationGroup
# 29-12-2015 enableSecurityLDAP
# 29-12-2015 modifyProcessExecution
# 29-12-2015 modifyTransactionLog
# 29-12-2015 modifyThreadPool
# 29-12-2015 modifyServerPort
# 29-12-2015 createVirtualHost
# 29-12-2015 addHostAlias
# 29-12-2015 createWebsphereVariable
# 29-12-2015 makesymlink
# 29-12-2015 manageprofiles
# 26-12-2015 runrcmd_vmo
# 06-12-2015 createUser
# 06-12-2015 X11forwarding
# 21-11-2015 tokenized
# 21-11-2015 name_value_pair
# 11-11-2015 get_latency
# 09-11-2015 get_n_last
# 09-11-2015 remove_n_last
# 09-11-2015 getdownloadfile v2
# 06-11-2015 get_history
# 03-11-2015 dns_to_ip
# 31-10-2015 clean_csv_files v2
# 19-10-2015 runrcmd
# 18-10-2015 extract_sources, check_user
# 16-10-2015 set_environment
# 14-10-2015 insert_in_file
# 13-10-2015 modified set_time_zone  
# 11-10-2015 added $1 $2 $3 $4 $5 to make additional calls
# http://superuser.com/questions/106272/how-to-call-bash-functions
# 11-10-2015 improved nfs_client
# 05-10-2015 getusedports
# 04-10-2015 nppFirewall Open port(s) for Listener
# 04-10-2015 found out how to comment multi lines
# 04-10-2015 fix_virtualimage
# 02-10-2015 getdownloadfile
# 01-09-2015 get_virtualimage_properties
# 29-08-2015 added to meet FE Credit request extra_disk
# 16-08-2015 get_file_mount, nfs_client
# 12-08-2015 modified set_time_zone
# 11-08-2015 get_response_file
# 09-08-2015 added random function
# 01-08-2015 added install_wmq, extend_hard_disk
'
# set -o vi
# sed -i -e 's/\r$//' ${csv_file}
# split -b 2000m -a 2 STERLING_B2B_INTEGRATOR_5.2.5_MP.tar STERLING_B2B_INTEGRATOR_5.2.5_MP.tar.
# /usr/bin/expect -c 'expect "\n" { eval spawn ssh -oStrictHostKeyChecking=no -oCheckHostIP=no usr@$myhost.example.com; interact }'

. /etc/virtualimage.properties

SCRIPT_DIR=${SCRIPT_DIR:-`pwd`}
OS=`uname`
SCRIPT=${0##*/}
SCRIPT_NAME=${SCRIPT%%.*}
LOGFILE=`pwd`/${SCRIPT_NAME}.log

# Return true if the running operation system is AIX
function aix {
    test "$OS" = "AIX"
}

function debug {
	test "$_DEBUG" = "on"  
}


# Return true if the running operation system is Linux
function linux {
    test "$OS" = "Linux"
}

# if aix ; then
# if linux ; then

if [[ -z ${REMOTE_SERVER_DOWNLOAD} ]] ;  then 
	REMOTE_SERVER_DOWNLOAD="http://10.30.128.35/WAS/Nodes.zip"
fi

if [[ ${REMOTE_SERVER_DOWNLOAD} != http*://* ]]; then
  REMOTE_SERVER_DOWNLOAD=http://${REMOTE_SERVER_DOWNLOAD}
fi

if [[ ${REMOTE_SERVER_DOWNLOAD} = *[!\ ]* ]] ; then
  REMOTE_SERVER_DOWNLOAD=`echo $REMOTE_SERVER_DOWNLOAD | sed -e 's/ /_/g' `
fi

DOWNLOAD_FILE=${REMOTE_SERVER_DOWNLOAD##*/}
PRODUCT_INSTALL=${DOWNLOAD_FILE%%.*}

THIS_LOGFILE=${SCRIPT_DIR}/${PRODUCT_INSTALL}.log

remoteWebServerFile=${REMOTE_SERVER_DOWNLOAD##*/}
remoteWebServerDir=${remoteWebServerFile%%.*}

httpConfFile=${IHS_HOME}/conf/httpd.conf
adminConfFile=${IHS_HOME}/conf/admin.conf
location=/tmp/${remoteWebServerDir}
earLocation=/tmp/${remoteWebServerDir}/earfiles
configApps=/tmp/${remoteWebServerDir}/configApps.csv
createCluster=/tmp/${remoteWebServerDir}/createCluster.csv
createJAASDataSource=/tmp/${remoteWebServerDir}/createJAASDataSource.csv
createJMS=/tmp/${remoteWebServerDir}/createJMS.csv
installApps=/tmp/${remoteWebServerDir}/installApps.csv
createProperty=/tmp/${remoteWebServerDir}/createProperty.csv

####### ########### Start Adding for CPALL
createNodeGroup=/tmp/${remoteWebServerDir}/createNodeGroup.csv
createTemplateCluster=/tmp/${remoteWebServerDir}/createTemplateCluster.csv
addNodeGroupMember=/tmp/${remoteWebServerDir}/addNodeGroupMember.csv
createCoreGroup=/tmp/${remoteWebServerDir}/createCoreGroup.csv
modifyServerPort=/tmp/${remoteWebServerDir}/modifyServerPort.csv
setJVMProperties=/tmp/${remoteWebServerDir}/setJVMProperties.csv
modifyThreadPool=/tmp/${remoteWebServerDir}/modifyThreadPool.csv
setJVMLog=/tmp/${remoteWebServerDir}/setJVMLog.csv
createDynamicCluster=/tmp/${remoteWebServerDir}/createDynamicCluster.csv
createJAASAuthData=/tmp/${remoteWebServerDir}/createJAASAuthData.csv
createXADataSource=/tmp/${remoteWebServerDir}/createXADataSource.csv
createXADataSourceOracle=/tmp/${remoteWebServerDir}/createXADataSourceOracle.csv
modifyTransactionLog=/tmp/${remoteWebServerDir}/modifyTransactionLog.csv
createEnvironmentEntries=/tmp/${remoteWebServerDir}/createEnvironmentEntries.csv
modifyProcessExecution=/tmp/${remoteWebServerDir}/modifyProcessExecution.csv
modifyCPCustomProperties=/tmp/${remoteWebServerDir}/modifyCPCustomProperties.csv
modifyDataSourceProperty=/tmp/${remoteWebServerDir}/modifyDataSourceProperty.csv
addHostAlias=/tmp/${remoteWebServerDir}/addHostAlias.csv
createSIBus=/tmp/${remoteWebServerDir}/createSIBus.csv
addSIBusMember=/tmp/${remoteWebServerDir}/addSIBusMember.csv
createSIBForeignBus=/tmp/${remoteWebServerDir}/createSIBForeignBus.csv
createSIBDestination=/tmp/${remoteWebServerDir}/createSIBDestination.csv
createSIBJMSConnectionFactory=/tmp/${remoteWebServerDir}/createSIBJMSConnectionFactory.csv
createWMQConnectionFactory=/tmp/${remoteWebServerDir}/createWMQConnectionFactory.csv
modifyWMQConnectionFactory=/tmp/${remoteWebServerDir}/modifyWMQConnectionFactory.csv
createJMSQueue=/tmp/${remoteWebServerDir}/createJMSQueue.csv
createWMQQueue=/tmp/${remoteWebServerDir}/createWMQQueue.csv
createSIBJMSActivationSpec=/tmp/${remoteWebServerDir}/createSIBJMSActivationSpec.csv
createWMQActivationSpec=/tmp/${remoteWebServerDir}/createWMQActivationSpec.csv
modifyWMQActivationSpec=/tmp/${remoteWebServerDir}/modifyWMQActivationSpec.csv
createWebsphereVariable=/tmp/${remoteWebServerDir}/createWebsphereVariable.csv
enableSecurityLDAP=/tmp/${remoteWebServerDir}/enableSecurityLDAP.csv
createUser=/tmp/${remoteWebServerDir}/createUser.csv
mapUsersToAdminRole=/tmp/${remoteWebServerDir}/mapUsersToAdminRole.csv
createGroup=/tmp/${remoteWebServerDir}/createGroup.csv
mapGroupsToAdminRole=/tmp/${remoteWebServerDir}/mapGroupsToAdminRole.csv
createIHS_no_WAS=/tmp/${remoteWebServerDir}/createIHS_no_WAS.csv
createWebServer=/tmp/${remoteWebServerDir}/createIHS_no_WAS.csv
modifySIBDestination=/tmp/${remoteWebServerDir}/modifySIBDestination.csv
createSIBContextInfo=/tmp/${remoteWebServerDir}/createSIBContextInfo.csv
createJVMCustomProperties=/tmp/${remoteWebServerDir}/createJVMCustomProperties.csv
createWorkManager=/tmp/${remoteWebServerDir}/createWorkManager.csv
createScheduler=/tmp/${remoteWebServerDir}/createScheduler.csv
createWCCustomProperties=/tmp/${remoteWebServerDir}/createWCCustomProperties.csv
createASCustomProperties=/tmp/${remoteWebServerDir}/createASCustomProperties.csv
####### ########### End Adding for CPALL

function mk_dir {
	directory=$1
	mkdir -m 775 -p $directory
}

if [[ ! -z ${remoteWebServerDir} ]] ; then
	mk_dir /tmp/${remoteWebServerDir}
fi

function DEBUG {
    if debug ; then
        "$@"
    else
        : "$@"
    fi
}

DEBUG set -x

function DATE {
	echo `date +%F_%H_%M_%S`
}

function add_user {
	USERNAME=$1
	PASSWORD=$2
	roleName=$3

	if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ] ; 	then
		useradd -m ${USERNAME}
		usermod -g wasgroup wasapp
		echo "*** setting password for user ${USERNAME}"
		case $OS in
			AIX)
				echo "${USERNAME}:${PASSWORD}" | /usr/bin/chpasswd -c
				;;
			*)
				if [ -f /etc/lsb-release ] && [ ! -f /etc/redhat-release ]; then
					echo "${USERNAME}:${PASSWORD}" | chpasswd
				else
					echo ${PASSWORD} | /usr/bin/passwd --stdin ${USERNAME}
				fi
				;;
		esac
		echo "*** user ${USERNAME} created"
	fi
	if [ $PROFILE_TYPE == "dmgr" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createUser; createUser()"		
	fi
}

function _createUser {
	add_user $1 $2 $3
}

function del_user {
	userdel -r ${1}
}

### WIP ####
function add_group {
	case $OS in
		AIX)
			mkgroup -'A' id='1000' adms='root' oinstall
			mkgroup -'A' id='1031' adms='root' dba
			mkuser id='1101' pgrp='oinstall' groups='dba' home='/home/oracle' oracle
			;;
		*)
			echo
			;;
		esac
}

### WIP ####
function delmb {
	ps -ef|grep bip|grep -v grep
	ps -ef|grep Data|grep -v grep
	sudo su - virtuser -c "mqsilist"
	sudo su - mqm      -c "dspmq"
	line=`mqsilist | grep -v BIP8071I | awk -F "'" '{print $2}'`
	if aix ; then
		set -A BROKER_LIST $line
	else
		eval 'BROKER_LIST=($line)'
	fi

	QQ=0

	for j in ${BROKER_LIST[@]} ; do
		echo "${BROKER_LIST[$QQ]}"
		echo --------------------------------------------------
		sudo su - virtuser -c "mqsistop ${BROKER_LIST[$QQ]} -q -i"
		sudo su - virtuser -c "mqsideletebroker ${BROKER_LIST[$QQ]} -q -w"
		echo --------------------------------------------------	
		#let QQ=$QQ+1
		let QQ+=1
	done
	ps -ef|grep bip|grep -v grep
	ps -ef|grep Data|grep -v grep
	ps -ef|grep virtuser|grep -v grep
	sudo su - virtuser -c "mqsilist"
	sudo su - mqm  -c "dspmq"
}

### WIP ####
function deldmgr {
	sudo su - mqm      -c "dspmq"
	ps -ef|grep mqm|grep amq|grep -v grep
	
	line=`dspmq | cut -d ")" -f1 | cut -d "(" -f2`
	if aix ; then 
		set -A QMGR_LIST $line
	else
		eval 'QMGR_LIST=($line)'
	fi
	QQ=0

	for j in ${QMGR_LIST[@]} ; do
		echo "${QMGR_LIST[$QQ]}"
		# --------------------------------------------------
		sudo -u mqm endmqm -i ${QMGR_LIST[$QQ]} 2>&1 | tee $PWD/pureappErr.log
		sudo -u mqm dltmqm ${QMGR_LIST[$QQ]} 2>&1 | tee $PWD/pureappErr.log
		# --------------------------------------------------	
		let QQ=$QQ+1
	done

	sudo su - mqm      -c "dspmq"
	ps -ef|grep mqm|grep amq|grep -v grep

	echo "SUCCESS: Default Queue Manager deleted."
}

function chmod_dca {
	directory=$1
	if [ -d $directory ]; then 
		chmod -R 775 ${directory} 
	elif [ -f $directory ]; then 
		chmod 775 ${directory} 
	else
		echo "file or directory : \'$directory'\ not found"
	fi
}

function timestamp {
	if aix ; then
		echo `date "+%Y-%m-%d %T"`
	else
		echo `date --rfc-3339=seconds`
	fi
}

function echoLog {
  if [ ! -z ${2} ]; then 
	echo "$1" | tee -a  ${2}
  else
	echo "`timestamp`: $1" | tee -a  ${LOGFILE}
  fi
}

function move_file {
	mv -- ${1}.bak ${1}
}

function clean_windows_files {
	sed -e 's/\r$//' ${$1} > ${$1}.bak
	move_file ${$1}
}

function dos2unix {
	clean_windows_files $1
}

function debugStart {
    if debug ; then
		echoLog "++++++++++++++++++++++++++++===== START DEBUGING =====++++++++++++++++++++++++++"
		echoLog "we are in this file ${0} and this function ${1} is being executed"
		echoLog "=============================`timestamp`========================================"
	fi
}

function debugEnd {
    if debug ; then
		echoLog "+++++++++++++++++++++++++++++`timestamp`++++++++++++++++++++++++++++++++++++++++"
		#echoLog "we are in this file ${0} and this function ${FUNCNAME[1]} is being executed"
		echoLog "we are in this file ${0} and this function ${1} is being executed"
		echoLog "===========================++++++++ END DEBUGING ++++++++++++==================="
	fi
}

function disableIPsec4 {
	case $OS in
		AIX)
			echoLog "Detected AIX. Stopping ipsec_v4."
			/usr/sbin/rmdev -l ipsec_v4
			wait $!
			RC=$?

			if [[ $RC -ne 0 ]]; then
			  echoLog "Attempt to disable IPSec failed. Script cannot continue !" 2>&1 | tee $PWD/pureappErr.log
			  exit 1
			fi
			;;
		Linux)
			echoLog "Detected Linux. Stopping IPTables."
			service iptables save
			service iptables stop
			chkconfig iptables off
			wait $!
			RC=$?

			if [[ $RC -ne 0 ]]; then
			  echoLog "Attempt to disable IPTables failed. Script cannot continue !" 2>&1 | tee $PWD/pureappErr.log
			  exit 1
			fi
			;;
		*)
			echoLog "Unsupported OS: $OS"
			exit 1
			;;
	esac
}

function clean_csv_files_old {
	for csv_file in ${location}/*.csv; do
	  if aix ; then
		sed -e 's/\r$//' ${csv_file} > ${csv_file}.bak
		move_file ${csv_file}
	  else
		sed -i -e 's/\r$//' ${csv_file}
	  fi
	  chmod_dca ${csv_file}
	  echo ${csv_file}
	done
}

function clean_csv_files {
	ls ${location}/*.csv | xargs dos2unix
}

function copy_file_backup {
	fileName=$1
	if [[ -f $fileName ]] ; then 
		if [[ -f $fileName.backup ]] ; then 
			cp ${fileName}.backup ${fileName}.backup.`DATE`
		fi
		cp ${fileName} ${fileName}.backup
	fi
}

function chown_backup {
	fileName=$1
	copy_file_backup $fileName
	chown -hR ${WHV_USER}:${WAS_GROUPNAME} ${fileName}.backup
	debugEnd chown_backup
}

function restore_file_backup {
	fileName=$1
	#fileName+=".backup"
	fileName=${fileName}.backup
	if [[ -f $fileName ]]; then
		rm -f $1
		mv -- $fileName ${fileName%.backup}
	fi
}

function copy_file {
	fileName=$1
	if [[ -f $fileName ]] ; then 
		cp ${fileName} ${fileName}.`DATE`
	fi
}

function backup_directory {
	fileName=$1 
	directory=$2
    tar cvf ${fileName}.`DATE`.tar ${directory}
}

function file_exists {
	fileName=$1
	exit_function=$2
	if [ ! -f ${fileName} ] && [ ! -z ${exit_function} ]; then
		echoLog "The specified file $fileName does not exist" 2>&1 | tee $PWD/pureappErr.log
	elif [ ! -f ${fileName} ]; then 
		echoLog "The specified file $fileName does not exist please ensure that it exits before continuing" 2>&1 | tee $PWD/pureappErr.log
		exit -2 2>&1 | tee $PWD/pureappErr.log
	fi
}
# http://www-01.ibm.com/support/knowledgecenter/SSELE6_8.0.1/com.ibm.isam.doc_8.0.1/adk/concept/con_group_admin_ids.html
function was_groupname {
	#USER1000=`cat /etc/passwd | grep ":1000:" | cut -d : -f 1` 
	WHV_USER=${WHV_USER:-wasgroup}
	WAS_GROUPNAME_TMP=${WAS_GROUPNAME_TMP:-wasgroup}
	WAS_GROUPNAME=${WAS_GROUPNAME:-admingroup}
	if aix ; then 
		# create group with root privilege
		# http://www.ibm.com/developerworks/aix/library/au-aixuseradmin/
		mkgroup -a ${WAS_GROUPNAME_TMP}
				
		chuser pgrp=${WAS_GROUPNAME_TMP} virtuser 
		chuser pgrp=${WAS_GROUPNAME_TMP} ${WHV_USER}
		
		chgrpmem -m - virtuser admingroup
		chgrpmem -m - ${WHV_USER} admingroup
		chgrpmem -m - virtuser ${WAS_GROUPNAME_TMP}
		
		rmgroup admingroup
		rmgroup ${WAS_GROUPNAME_TMP}
		
		mkgroup -a ${WAS_GROUPNAME}		
		
	else
		groupadd ${WAS_GROUPNAME_TMP}
		
		usermod -g ${WAS_GROUPNAME_TMP} virtuser
		usermod -g ${WAS_GROUPNAME_TMP} ${WHV_USER}
		
		deluser virtuser admingroup
		deluser ${WHV_USER} admingroup
		deluser virtuser ${WAS_GROUPNAME_TMP}
		
		groupdel admingroup
		groupdel ${WAS_GROUPNAME_TMP}
		
		groupadd ${WAS_GROUPNAME}
	fi
	
	#usermod -G ${WAS_GROUPNAME} ${WHV_USER}
	#usermod -G ${WAS_GROUPNAME} virtuser
	
	usermod -g ${WAS_GROUPNAME} ${WHV_USER}
	usermod -g ${WAS_GROUPNAME} virtuser
	
	groupename=`cat /etc/virtualimage.properties | grep WAS_GROUPNAME=`
	if [[ ${#groupename} = 0 ]] ; then
		echo WAS_GROUPNAME=${WAS_GROUPNAME} | tee -a /etc/virtualimage.properties
		sed '/^$/d' /etc/virtualimage.properties > /etc/virtualimage.properties.bak
		move_file /etc/virtualimage.properties
	fi
}

function trim_whitespace {
	string=$1
	string="${string#"${string%%[![:space:]]*}"}"   # remove leading whitespace characters
	string="${string%"${string##*[![:space:]]}"}"   # remove trailing whitespace characters
	echo $string
} 

function trim {
    trimmed=$1
    trimmed=${trimmed%% }
    trimmed=${trimmed## }
    echo "$trimmed"
}

function chown_dca {
  WHV_USER=$1
  directory=$2
  if [ -d ${directory} ] ; then
		chown -hR ${WHV_USER}:${WAS_GROUPNAME} ${directory}
		chmod_dca ${directory} 
  elif [ -f $directory ]; then
		chown ${WHV_USER} ${directory}
		chmod_dca ${directory}
  else
	echo "This \'$directory'\ file or directory in the path name does not exist."
  fi
}

function sed_aix_linux {
    sed -e ${1} ${2} > ${2}.bak 
	move_file ${2}
}

function lastmod {
	 fileName=$1
	 if [ -f ${fileName} ] ; then
		 if aix ; then 
			mod=`istat $fileName | grep 'Last modified:'`;  mod=${mod%%.*} ; remove="Last modified:"; echo ${mod#${remove}}
		 else
			mod=`stat $fileName | grep 'Modify:'`;  mod=${mod%%.*} ; remove="Modify:"; echo ${mod#${remove}}
		 fi
	 fi
}

### WIP work in progress ###
function generate_ihs_plugin_cfg {
  sudo -u ${WHV_USER} -i ${WAS_PROFILE_ROOT}/bin/wsadmin.sh -lang jython -username ${WHV_USER} -password ${WAS_PASSWORD} -c "AdminControl.invoke(AdminControl.completeObjectName('type=PluginCfgGenerator,*'), 'generate', '[${WAS_PROFILE_ROOT}/profiles/${part_node_name}/config BPMCell ${hostname}-node webserver1 false]')"
}

### WIP work in progress ###
function propagate_ihs_plugin_cfg {
  sudo -u ${WHV_USER} -i ${WAS_PROFILE_ROOT}/bin/wsadmin.sh -lang jython -username ${WHV_USER} -password ${WAS_PASSWORD} -c "AdminControl.invoke(AdminControl.completeObjectName('type=PluginCfgGenerator,*'), 'propagate', '[${WAS_PROFILE_ROOT}/profiles/${part_node_name}/config BPMCell ${hostname}-node webserver1]')"
}

function update_ihs_cfg  {
  generate_ihs_plugin_cfg
  propagate_ihs_plugin_cfg 
}

function found_word {
	word=$1
	fileName=$2
	val=`grep $word $fileName`
	if [[ ${#val} > 0 ]]; then
		true
	else
		false
	fi
}

function set_virtualimage_password {
	case $1 in
		start)
			cp /etc/virtualimage.properties /etc/virtualimage.properties.setpassword
			WASpassword=`cat /etc/virtualimage.properties |grep "WAS_PASSWORD="`
			if [ ! -z ${2} ] ; then
				sed_aix_linux "s/$WASpassword/WAS_PASSWORD=${2}/g" /etc/virtualimage.properties
			else
				sed_aix_linux "s/$WASpassword/WAS_PASSWORD=password/g" /etc/virtualimage.properties
			fi
		;;
		end)
			rm -f /etc/virtualimage.properties
			mv -- /etc/virtualimage.properties.setpassword /etc/virtualimage.properties
			;;
		*)
			echo "Don't know" ;;
	esac
}

### WIP work in progress ###
function check_errs {
  # Function. Parameter 1 is the return code
  # Para. 2 is text to display on failure.
  if [ "${1}" -ne "0" ]; then
    echo "ERROR # ${1} : ${2}"
    # as a bonus, make our script exit with the right error code.
    exit ${1}
  fi
}

function stop_webserver { 
	if [ $PROFILE_TYPE == "custom" ] || [ $PROFILE_TYPE == "ihs" ]; then
	  #su $WHV_USER -c "${IHS_HOME}/bin/adminctl stop"
	  ${IHS_HOME}/bin/adminctl stop
	  sleep 5

	  #su $WHV_USER -c "${IHS_HOME}/bin/apachectl stop"
	  ${IHS_HOME}/bin/apachectl stop
	  sleep 5
	fi
}

function start_webserver { 
	if [ $PROFILE_TYPE == "custom" ] || [ $PROFILE_TYPE == "ihs" ]; then
	  #su $WHV_USER -c "${IHS_HOME}/bin/adminctl start"
	  ${IHS_HOME}/bin/adminctl start
	  sleep 5

	  #su $WHV_USER -c "${IHS_HOME}/bin/apachectl start"
	  ${IHS_HOME}/bin/apachectl start
	  sleep 5
	fi
}

function stop_start_webserver { 
	stop_webserver
	start_webserver
}

function restart_webserver { 
	su $WHV_USER -c "${IHS_HOME}/bin/adminctl -k restart"
	su $WHV_USER -c "${IHS_HOME}/bin/apachectl -k restart"
	echoLog "Restarted Web server"
}

function collect_was_log {
	if [ -d ${WAS_PROFILE_ROOT}/logs ]; then
		mk_dir ${SCRIPT_DIR}/logs 
		for x in `find $WAS_PROFILE_ROOT/logs -name System*.log` ; do
			case $OS in
				AIX)
					cp -p ${x} ${SCRIPT_DIR}/logs ;;
				Linux)
					cp -p --parents ${x} ${SCRIPT_DIR}/logs ;;
				SunOS)
					;;
				HP-UX)
					;;
			esac
		done
		echo "System Out logs copied to Log directory"
	fi
}

function wget_aix {
	if aix ; then 
		if [ -f $SCRIPT_DIR/wget-1.9.1-1.aix5.1.ppc.rpm ]; then
			rpm -ivh $SCRIPT_DIR/wget-1.9.1-1.aix5.1.ppc.rpm
		fi
	fi
}

function bash_aix {
	if aix ; then 
		if [ -f $SCRIPT_DIR/bash-4.2-1.aix6.1.ppc.rpm ]; then
			rpm -ivh $SCRIPT_DIR/bash-4.2-1.aix6.1.ppc.rpm
		fi
	fi
}

function copyDCAartifacts {
	if [ -d /tmp/$remoteWebServerDir/artifacts ]; then
		#su $WHV_USER -c "yes | cp -rf /tmp/$remoteWebServerDir/artifacts/*  $WAS_INSTALL_ROOT/lib/ext/ "
		yes | cp -rf /tmp/$remoteWebServerDir/artifacts/*  $WAS_INSTALL_ROOT/lib/ext/ 
	fi
}

function set_ssh {
	sshDir=""
	if aix ; then
		sshDir="/.ssh/"
	else
		sshDir="/root/.ssh/"
	fi

	echoLog "Verify file permissions"
	chmod 0600 $SCRIPT_DIR/id_rsa

	echoLog "Copy Public / Private Certificates"
	cp -p $SCRIPT_DIR/id_rsa ${sshDir}id_rsa
	cp -p $SCRIPT_DIR/id_rsa.pub ${sshDir}id_rsa.pub

	echoLog "Merge system and pre-defined authorized_keys file"
	templateContents=`cat $SCRIPT_DIR/authorized_keys.template`
	echo $templateContents >> ${sshDir}authorized_keys 

	echoLog "Disable strict host key checking in ssh"
	cp -p $SCRIPT_DIR/config ${sshDir}config
}

function telnet_redhat {
	if [[ $0S == 'Linux' ]]; then
		if [[ -d telnet-0.17-47.el6.x86_64.rpm ]] ; then
			rpm -i $SCRIPT_DIR/telnet-0.17-47.el6.x86_64.rpm
		fi
	fi
}

function install_db_driver {
	case $1 in
		DB2)
			if [ ! -d /opt/db2 ]; then
			  mk_dir /opt/db2
			fi

			if [ -f /tmp/$remoteWebServerDir/dbDrivers/db2jars.zip ]; then
				yes | cp -rf /tmp/$remoteWebServerDir/dbDrivers/db2java.zip /opt/db2
				yes | cp -rf /tmp/$remoteWebServerDir/dbDrivers/db2jars.zip /opt/db2
				#unzip -d -o /opt/db2 /tmp/$remoteWebServerDir/dbDrivers/db2jars.zip
				cd /opt/db2
				unzip -o db2jars.zip
				cd -
			fi
			;;
		ORA10)
			if [ -f /tmp/$remoteWebServerDir/dbDrivers/ojdbc14.jar ]; then
				cp /tmp/$remoteWebServerDir/dbDrivers/ojdbc14.jar  $WAS_INSTALL_ROOT/lib/ext/ 
			fi
			;;
		ORA11)
			if [ -f /tmp/$remoteWebServerDir/dbDrivers/ojdbc6.jar ]; then
				cp /tmp/$remoteWebServerDir/dbDrivers/ojdbc6.jar  $WAS_INSTALL_ROOT/lib/ext/ 
			fi
			;;
		MSSQL)
			if [ -f /tmp/$remoteWebServerDir/dbDrivers/sqljdbc4.jar ]; then
				cp /tmp/$remoteWebServerDir/dbDrivers/sqljdbc4.jar  $WAS_INSTALL_ROOT/lib/ext/ 
			fi
			;;
		NETEZZA)
			if [ -f /tmp/$remoteWebServerDir/dbDrivers/nzjdbc3.jar ]; then
				cp /tmp/$remoteWebServerDir/dbDrivers/nzjdbc3.jar  $WAS_INSTALL_ROOT/lib/ext/ 
			fi
			;;
	esac
}

function insert_in_file {
	test ! -f $2 ; touch $2
	if ! grep "$1" $2 > /dev/null ; then
	   echo "$1" | tee -a $2
	fi
}

function set_environment {
	insert_in_file "$1" /etc/environment
}

function set_time_zone {
	export TZ=$1
	if aix ; then
		chtz $TZ
	else
		insert_in_file "TZ=$TZ" /etc/environment
	fi
	echo `date`
}

function restart_was {
	case $PROFILE_TYPE in
		custom)
			su $WHV_USER -c "$WAS_PROFILE_ROOT/bin/stopNode.sh"
			su $WHV_USER -c "$WAS_PROFILE_ROOT/bin/startNode.sh"
			;;
		default)
			su $WHV_USER -c "$WAS_PROFILE_ROOT/bin/stopServer.sh server1"
			su $WHV_USER -c "$WAS_PROFILE_ROOT/bin/startServer.sh server1"
			;;
		dmgr)
			su $WHV_USER -c "$WAS_PROFILE_ROOT/bin/stopManager.sh"
			su $WHV_USER -c "$WAS_PROFILE_ROOT/bin/startManager.sh"
			;;
	esac
}

function backup_was {
if [ $PROFILE_TYPE == "dmgr" ] || [ $PROFILE_TYPE == "default" ]; then
	chmod_dca $SCRIPT_DIR/*
	chown_dca $WHV_USER $WAS_PROFILE_ROOT
	if [[ -f /tmp/${remoteWebServerDir}/WAS_backup.zip ]] ; then
		su ${WHV_USER} -c "$WAS_PROFILE_ROOT/bin/backupConfig.sh /tmp/${remoteWebServerDir}/WAS_backup.`DATE`.zip -nostop"
	else
		su ${WHV_USER} -c "$WAS_PROFILE_ROOT/bin/backupConfig.sh /tmp/${remoteWebServerDir}/WAS_backup.zip -nostop"
	fi
fi
}

### WIP ###
function execute {
	COMMAND=$1
	echo $COMMAND
	if [ ! -z $2 ] ; then
		if [ $2 == $WHV_USER ] ; then
			su - $WHV_USER -c "$COMMAND"
		fi
	else
		echo 
	fi
		
	echo RC: $?
}

### WIP ###
function symbolic_link {
	ln -s $1 $2
}

### WIP ###
function mount_disk {
	cp -pr /opt/IBM/HTTPServer/htdocs /tmp

	echo "Enter the new volume group name:"
	read vgname
	echo "Enter the new lv name"
	read lvname
	echo "Enter the size of the new LV" 
	read lvsize
	pvcreate $diskname
	vgcreate $vgname $diskname ## creating VG
	lvcreate -L $lvsize /dev/$vgname -n $lvname  ## creating LV
	mkfs.ext3 /dev/$vgname/$lvname ## creating the filesystem
	mount -t ext3 /dev/$vgname/$lvname /opt/IBM/HTTPServer/htdocs
	echo "/dev/$vgname/$lvname /opt/IBM/HTTPServer/htdocs	ext3	defaults 0 0" >> /etc/fstab ## updating the fstab file for permanent mount
	cp -pr /tmp/htdocs /opt/IBM/HTTPServer/htdocs
}

function reboot {
	# this takes about 5 minutes to reboot.
	shutdown -r now
}

### WIP ###
function some_hostname {
	SHORT_HOSTNAME=`hostname -s`
	FULL_HOSTNAME=`hostname`
}

# http://tldp.org/LDP/abs/html/testbranch.html
### WIP ####
function is_digit {  # Tests whether *entire string* is numerical.
          # In other words, tests for integer variable.
  SUCCESS=0
  FAILURE=1		  
  [ $# -eq 1 ] || return $FAILURE

  case $1 in
    *[!0-9]*|"") return $FAILURE;;
              *) return $SUCCESS;;
  esac
}

#get_n_last "ernese norelus" 5
function get_n_last {
	string=$1
	echo "${string: -$2}"
}

# remove_n_last "ernese norelus" 5
function remove_n_last {
	string=$1
	len=${#string}-$2
	echo "${string:0:$len}"
}

function rename_cell_node {
	new_cell_name=$1
	new_node_name=$2
	
	chown_backup $WAS_PROFILE_ROOT/bin/setupCmdLine.sh

	if [ $PROFILE_TYPE == "dmgr" ] ; then	
		WASCellName=`cat $WAS_PROFILE_ROOT/bin/setupCmdLine.sh |grep "WAS_CELL="`
		if [[ ${#WASCellName} > 0 ]] ; then
			sed_aix_linux "s/$WASCellName/WAS_CELL=$new_cell_name/g" $WAS_PROFILE_ROOT/bin/setupCmdLine.sh 
		fi
		
		WASNodeName=`cat $WAS_PROFILE_ROOT/bin/setupCmdLine.sh |grep "WAS_NODE="`
		if [[ ${#WASNodeName} > 0 ]] ; then
			sed_aix_linux "s/$WASNodeName/WAS_NODE=$new_node_name/g" $WAS_PROFILE_ROOT/bin/setupCmdLine.sh
		fi
	fi
	
	WASCellNameProperties=`cat /etc/virtualimage.properties | grep "CELL_NAME"`
	if [[ ${#WASCellNameProperties} > 0 ]] ; then
		sed_aix_linux "s/$WASCellNameProperties/CELL_NAME=$new_cell_name/g" /etc/virtualimage.properties
	fi

	WASNodeNameProperties=`cat /etc/virtualimage.properties | grep "NODE_NAME"`
	if [[ ${#WASNodeNameProperties} > 0 ]] ; then
		sed_aix_linux "s/$WASNodeNameProperties/NODE_NAME=$new_node_name/g" /etc/virtualimage.properties
	fi
}

### WIP ###
function genpasswd {
	l=$1
	[ "$l" == "" ] && l=20
	tr -dc A-Za-z0-9_ < /dev/urandom | head -c ${l} | xargs
}

### WIP ####
function run_again {
	# # Run again
	# exec $0
	echo "### WIP - run_again ####"
}

# this function kills the process from the process ID file
function kill_process {
	lockd.pid=$1
	# Kill running lockd process
	if [ -f "${lockd.pid}" ]; then
		pid=`cat ${lockd.pid}`
		kill -9 ${pid} > /dev/null 2>&1 | tee $PWD/pureappErr.log
	fi
}

### WIP ####
# Record lockd process id for shutdown
function shutdown {
	# echo $! > lockd.pid
	echo "### WIP  shutdown ####"
}

### WIP ####
function exit_on_error {
    if [ $? -ne 0 ] ; then
        echo ${ERR_MESSAGE:-"${1}"}
        exit 1
    fi
}

### WIP ####
# this is the process id
function process_id {
	file=$1
	wait $! > ${file}
}

function wait_for_app {
	# loop until 0config/0config.log reports status as RUNNING
	while true
	do
	  sleep 10
	  echoLog "Slept for 10 seconds .."
	  status=`grep -ic 'update status to RUNNING' /0config/0config.log`
	  if [[ "$status" == "1" ]]; then
		# sleep for 2 seconds
		sleep 2
		break
	  fi
	done
}

### WIP ####
function web_mount_point {
	MOUNT_POINT=$1
	echoLog "Alias /external/ \"$MOUNT_POINT/\"" ${httpConfFile}
	echoLog "<Directory \"$MOUNT_POINT\">" ${httpConfFile}
	echoLog "</Directory>" ${httpConfFile}
}

### WIP ####
function config_http_ssl {
	memberName=$1
	hostname=$2
	MOUNT_POINT=$3
	if [[ `grep -wc "^LoadModule ibm_ssl_module modules/mod_ibm_ssl.so" ${httpConfFile}` -eq 0 ]] ; then
		echoLog "Listen $hostname:80" ${httpConfFile}
		echoLog "LoadModule was_ap22_module ${wasModule}" ${httpConfFile}
		echoLog "WebSpherePluginConfig ${pluginConfigFile}" ${httpConfFile}
		echoLog "LoadModule ibm_ssl_module modules/mod_ibm_ssl.so" ${httpConfFile}
		echoLog "<IfModule mod_ibm_ssl.c>" ${httpConfFile}
		echoLog "  Listen 443" ${httpConfFile}
		echoLog "  <VirtualHost *:443>" ${httpConfFile}
		echoLog "    SSLEnable" ${httpConfFile}
		echoLog "  </VirtualHost>" ${httpConfFile}
		echoLog "</IfModule>"  ${httpConfFile}
		echoLog "SSLDisable" ${httpConfFile}
		echoLog "KeyFile \"${IHS_HOME}/${memberName}.kdb\"" ${httpConfFile}
	fi
	if [[ ! -z ${MOUNT_POINT} ]] ; then
		web_mount_point ${MOUNT_POINT}
	fi
}

### WIP ####
function string_manipulation {
echo "### WIP - string_manipulation ####"
	# need to test 
	#x=item2                                 
	# echo item1,item2,item3,...itemN| sed "s/$x//g"
	#item1,,item3,...itemN
	#string="Hello World"
	#prefix="Hell"
	#suffix="orld"
	#foo=${string#$prefix}
	#foo=${foo%$suffix}
	#first=$

	#echo "${foo}"

	#x="lkj" 
	#echo "${x%?}" 
	#lk

	#var="Memory Used: 19.54M"         
	#var=${var#*: } # Remove everything up to a colon and space                          
	#var=${var%M}   # Remove the M at the end

	#${string#?}

	#echo ${foo#?} # remove first character

	#http://tldp.org/LDP/abs/html/string-manipulation.html
	#http://tldp.org/LDP/abs/html/parameter-substitution.html
	#http://www.linuxtopia.org/online_books/advanced_bash_scripting_guide/string-manipulation.html
	#http://stackoverflow.com/questions/13570327/shell-script-deleting-a-substring
	#http://superuser.com/questions/697667/command-line-extract-substring-from-output
	#http://linuxmantra.com/2010/11/string-manipulation-in-bash-script.html
}

function list_users {
	echo `awk -F":" '{ print $1 }' /etc/passwd`
}

function list_users {
	if [[ ! -z ${1} ]] ; then
		for user in $(cat /etc/passwd |awk -F: '{if ($3>11 && $3!=200 && $3!=201) print $1}' | grep -v nobody | grep -v sshd); do  
			eval "$1 $user"
		done
	else
		echo `awk -F":" '{ print $1 }' /etc/passwd`
	fi
}

function rename_s { 
	filename=$1; old_ext=$2; new_ext=$3
	echo "$filename" "${filename%.$old_ext}.${new_ext}"
}

### WIP ####
function WAS_password_decoder {
	password_decoder=$1
	$WAS_PROFILE_ROOT/java/bin/java -Djava.ext.dirs=$WAS_PROFILE_ROOT/lib:$WAS_PROFILE_ROOT/plugins -Dwas.install.root=$WAS_PROFILE_ROOT -cp $WAS_PROFILE_ROOT/plugins/com.ibm.ws.runtime.jar:$WAS_PROFILE_ROOT/lib/bootstrap.jar com.ibm.ws.bootstrap.WSLauncher com.ibm.ws.security.util.PasswordDecoder "$password_decoder" | grep -v "user.install.root" | grep -v "^ERROR"
}

### WIP ####
function WAS_password_manager {
	password_encoder=$1
	$WAS_PROFILE_ROOT/java/bin/java -Djava.ext.dirs=$WAS_PROFILE_ROOT/lib:$WAS_PROFILE_ROOT/plugins -Dwas.install.root=$WAS_PROFILE_ROOT -cp $WAS_PROFILE_ROOT/plugins/com.ibm.ws.runtime.jar:$WAS_PROFILE_ROOT/lib/bootstrap.jar com.ibm.ws.bootstrap.WSLauncher com.ibm.ws.security.util.PasswordEncoder "$password_encoder" | grep -v "user.install.root" | grep -v "^ERROR"
}

### WIP ####
function rename_f { 
	filename=$1; 	old_ext=$2 ; 	new_ext=$3
	if [ $# -eq 3 ]; then
		#test -f "$filename"  && cp "$filename" "${filename%.$old_ext}.${new_ext}" && rm -f "$filename" || echo " file name : $filename  does not exist"
		test -f "$filename"  && mv -- "$filename" "${filename%.$old_ext}.${new_ext}" || echo " file name : $filename  does not exist"
	elif [ $# -eq 2 ]; then
		test -f "$filename"  && mv -- "$filename" "$old_ext" || echo " file name : $filename  does not exist"
	else
		echo " this function rename_f requires 2 or 3 arguments to work"
	fi
}

function open_ports {
	if [ $OS = "Linux" ] ; then 
		iptables -A INPUT -p tcp --dport $1 -j ACCEPT
		iptables -A INPUT -p tcp --dport $2 -j ACCEPT
		iptables -L
	else
		echo "not supported yet for $OS"
	fi
}

# not recommended for it's the best workaround i've found for now
function mount_point_disk {
	if [[ -z ${MOUNT_POINT} ]]; then
		MOUNT_POINT=`df -m | grep /dev/fslv02 | awk '{print $7}'`
		if [[ -z ${MOUNT_POINT} ]]; then
			MOUNT_POINT=${PWD}
		fi
	fi
}

function test_for_empty_directory {
	if [ ! `find $1 -maxdepth 0 -type d -empty 2>/dev/null` ]; then
		echo "Not empty or NOT a directory"
		cd ${1} 
		rm -rf .* *
		cd -
	fi
}

function insert_if_not_found {
	grep -q -F ${1} ${3} || echo ${1}${2}  | tee -a ${3}
}

function get_java_location {
	jvm_loc=`which java`
	if [[ -z ${1} ]] ; then 
		if [[ ${OS} == "AIX" ]] ; then
			echo ${jvm_loc%/jre/bin/java}
		else
			echo ${jvm_loc%/Java/javapath/java}
		fi
	else
		echo ${jvm_loc%${1}}
	fi
}

function get_dns_from_ip {
	echo `nslookup ${1} | grep name |  awk '{print $4}' | sed 's/.$//'`
}

function dns_to_ip {
	host $1 | cut -d" " -f3 | cut -d"," -f1
}

function get_domain_name {
	val=`hostname`
	echo ${val#*.}
}

function change_tmp_location {
	#getconf DISK_SIZE /dev/fslv00
	#export IATEMPDIR=$MOUNT_POINT export CHECK_DISK_SPACE=OFF
	export IATEMPDIR=${1} export CHECK_DISK_SPACE=OFF
}

function get_mount_point {
	#MOUNT_POINT=`df -m | grep /dev/fslv02 | awk '{print $7}'`
	MOUNT_POINT=`df -m | grep ${1} | awk '{print $7}'`
	echo ${MOUNT_POINT}
}

function get_properties {
	val=`grep -r ${1} ${PWD}/$DOWNLOAD_FILE`
	echo ${val##*/}
}

function get_line_number {
	echo `grep -n $1 $2 | cut -d':' -f1`
}

function read_from_virtualimage {
	virtualimage=`cat /etc/virtualimage.properties | grep -E "$1"`
	remove_duplicates ${2}
	remove_comments_and_empty_lines ${2}
	sed "/${1}/d" ${2} > ${2}.bak 
	move_file ${2}
	echo ${virtualimage} | tee -a ${2}
}

function delete_and_insert {
	sed "/${1}/d" ${3} > ${3}.bak 
	move_file ${3}
	echo ${2} | tee -a ${3}
}

function read_last_line {
	sed -e '/^[<blank><tab>]*$/d' ${1} | sed -n -e '$p'
}

function getIPAddress {
	if [[ -z ${1} ]]; then
		hostname=`hostname`
	else
		hostname=${1}
	fi
	echo `host $hostname | awk ' { print $3 }' | sed 's/.\{1\}$//'`		
}

function get_ip_from_dns {
	getIPAddress ${1}
}

function remove_comments_and_empty_lines {
	FILE_NAME=${1}
	grep  -v ^# ${FILE_NAME}  | grep -v ^$ > ${FILE_NAME}.bak
	move_file ${FILE_NAME}
}

function delete_line {
	sed "/${1}/d" ${2} > ${2}.bak 
	move_file ${2}
}

function remove_line_starts_with {
	grep -v "^$1" ${2} > ${2}.bak
	move_file ${2}
}

function remove_duplicates {
	awk '!seen[$0]++' ${1} > ${1}.bak
	move_file ${1}
}

function reconstruct_big_file {
	big_file=${1}
	cat ${big_file}* > TZ.${big_file}.TZ
	rm -rf ${big_file}*
	mv -- TZ.${big_file}.TZ ${big_file}
}

function read_log_big_file {
	big_file=${1}
	echo `cat ${big_file}.log`
}

function clean_up_tar_file {
	big_file=${1}
	location=${2}
	tar -tf ${big_file} > ${big_file}.log
	mk_dir ${location}
	tar -xf ${big_file} -C ${location} 
	rm -f ${big_file}
}

function clean_up_zip {
	ZIPFILE=${1}
	location=${2}
	unzip -l ${ZIPFILE} > ${ZIPFILE}.log
	mk_dir ${location}
	unzip -o ${ZIPFILE} -d ${location}
	rm -f ${ZIPFILE}
}

function clean_up_tar_gz {
	ZIPFILE=${1}
	MOUNT_POINT=${2}
	if [ $OS = 'AIX' ]; then 
		gunzip < ${ZIPFILE} | tar -xvf - | tee -a ${MOUNT_POINT}/${ZIPFILE}.log
	else
		tar -tf ${ZIPFILE} > ${ZIPFILE}.log
		gunzip -c ${ZIPFILE} | tar x -C ${MOUNT_POINT}
		JAR_FILE=${ZIPFILE}.log
	fi
	rm -f ${ZIPFILE}
}

function install3rdParty_WMQ {
	cd ${1}
	for f in *.jar ; do
		${SI_INSTALL_PATH}/bin/install3rdParty.sh mqseries 7.5 -j ${f} | tee -a ${2}/install3rdParty.log
	done
	cd -
}

### WIP ####
function set_properties {
	#space separated value 
	IFS=" "

	while read line	   ; do
		set -A  linetokens $line
		URL=${linetokens[0]}
		if [[ ${#URL} = 0 ]]; then
			break
		fi

		if [[ ${URL} == *"properties"* ]]; then
			DOWNLOAD_FILE_IN=${URL##*/}
			while read line2	   ; do
				set -A  linetokens2 $line2
				URL2=${linetokens2[0]}
				if ! grep -Fxq $URL2 /etc/virtualimage.properties ; then
					echo "$URL2" | tee -a /etc/virtualimage.properties
				fi
			done < $SCRIPT_DIR/$DOWNLOAD_FILE_IN	
			sed '/^ *$/d' /etc/virtualimage.properties > /etc/virtualimage.properties.bak
			move_file /etc/virtualimage.properties
			. /etc/virtualimage.properties
		fi
	done < $SCRIPT_DIR/$DOWNLOAD_FILE
}

### WIP ####
function del_big_file {
	i=1
	while read line	   ; do
		test $i -eq 1 && ((i=i+1)) && continue
		set -A linetokens $line
		URL=${linetokens[0]}
		DOWNLOAD_FILE_IN=${URL##*/}
		rm -f $SCRIPT_DIR/$DOWNLOAD_FILE_IN
		((++i))
	done < $SCRIPT_DIR/$DOWNLOAD_FILE
}

### WIP ####
function install_software {
	SOURCE="IM_AIX.zip"
	while read line	   ; do
		set -A linetokens $line
		LIST=${linetokens[0]}

		if echo "$LIST" | grep -q "$SOURCE"; then
		  echo "found match  for $SOURCE";
		  break
		fi
	
	done < $JAR_FILE
}

### WIP ####
function install_software_ext {
	
	FILENAME=$1 #$JAR_FILE
	SOURCE=$2 #"IM_AIX.zip"
	
	while read line	   ; do
		set -A linetokens $line
		LIST=${linetokens[0]}

		if echo "$LIST" | grep -q "$SOURCE"; then
		  echo "found match  for $SOURCE";
		  break
		fi
	
	done < $FILENAME
}

### WIP ###
function insert_before_pattern {
	awk '/${1}/{print "${2}"}1' ${3}  > ${3}.bak
	move_file ${3}
}

function set_nfs_domain_name {
	echo "Setting domain name"
	chnfsdom `get_domain_name`

	echo "starting nfs domain service"
	startsrc -s nfsrgyd
}

function start_nfs_daemon {
	user=$1
	group=$2
	NFS_MOUNT=$3
	
	if [[ `cat /etc/passwd| grep $user |wc -l` -eq 0 ]]; then 
	  echo "" 1>&2
	  echo "Error: Cannot execute script package because $user user does not exist." 1>&2
	  echo "" 1>&2
	  exit 1;
	fi

	echo "Creating shared directory and sub folders"
	mkdir -p $NFS_MOUNT/WMQ
	mkdir -p $NFS_MOUNT/WMQ/logs
	mkdir -p $NFS_MOUNT/WMQ/qmgrs
	mkdir -p $NFS_MOUNT/WMB

	echo "Set $user ownership"
	chown -R $user:$group $NFS_MOUNT


	echo "Set permissions"
	#chmod -R ug+rwx $NFS_MOUNT
	chmod -R 1777 $NFS_MOUNT

	echo "Start the NFS daemon"
	startsrc -g nfs

	echo "Make sure the daemons are running"
	lssrc -g nfs

	echo "Export the file system"
	mknfsexp -d $NFS_MOUNT -S 'sys' -t rw

	echo "Verify the mount point is being exported from this server"
	showmount -e

	echo "checking if nfs will start automatically"
	lsitab rcnfs
}

# https://www-01.ibm.com/support/knowledgecenter/ssw_aix_61/com.ibm.aix.cmds3/mknfsmnt.htm
# mknfsmnt -f /usr/share/man -d /usr/share/man -h host1
# nfs_client_mount mqm mqm $NFS_MOUNT $NFS_HOST # server location
function nfs_client_mount {
	user=$1
	group=$2
	NFS_MOUNT=$3
	NFS_NODE=$4
	
	echo "Creating mount point"
	mkdir -p $NFS_MOUNT
	chown $user:$group $NFS_MOUNT

	echo "Make sure nfs is running"
	startsrc -g tcpip
	startsrc -g nfs

	echo "Mounting directory"
	#mount -t nfs4 -o hard,intr ${NFS_HOST}:/$NFS_MOUNT
	mknfsmnt -f "$NFS_MOUNT" -d "$NFS_MOUNT" -h "$NFS_HOST" -M 'sys' -B -A -t rw -w bg -H

	echo "Verifying the mount point"
	#mount
	ls -l $NFS_MOUNT

	echo "Checking if nfs will start automatically"
	lsitab rcnfs
}

function nfs_client {
	NFS_HOST=$1
	NFS_MOUNT=$2
	if ( ! mount | grep -q "$NFS_MOUNT" ) ; then 
		mk_dir $NFS_MOUNT
		mount $NFS_HOST:$NFS_MOUNT $NFS_MOUNT
	fi
}

function nfs_client_server {
	user=$1
	group=$2
	NFS_MOUNT=$3
	NFS_HOST=$4
	
	set_nfs_domain_name

	if [[ ${#NFS_HOST} >  3 ]]; then
		nfs_client_mount $user $group $NFS_MOUNT $NFS_HOST
	else
		nfs_client $NFS_HOST $NFS_MOUNT	
	fi
}

# WIP ###
# su - db2inst1 -c "db2licm -l"
# su - db2inst1 -c "db2level gives | grep 'Product is installed at'"
# su - db2inst1 -c "db2ls -q -a -b"

function init_db2 {
	sed_aix_linux "s|DB2ADMIN|${databaseUser}|g" ${PWD}/db2move.lst
	sed_aix_linux "s|DB2ADMIN|${databaseUser}|g" ${PWD}/sws2_ddl.sql
	sed -e "/CONNECT TO / s/^/-- /" ${PWD}/sws2_ddl.sql > ${PWD}/sws2_ddl.sql.bak
	move_file ${PWD}/sws2_ddl.sql
	
	su - $instanceName -c  "db2 connect to ${databaseName} user ${databaseUser} using ${databaseUserPassword}"
	su - $instanceName -c  "db2 create schema ${databaseUser}"
	su - $instanceName -c  "db2 set current schema ${databaseUser}"
	su - $instanceName -c  "db2 -tvf $PWD/sws2_ddl.sql"
	su - $instanceName -c  "db2set DB2CODEPAGE=1208" # not working
	su - $instanceName -c  "db2move ${databaseName} load"
	su - $instanceName -c  "db2set DB2_SKIPDELETED=ON"
	su - $instanceName -c  "db2set DB2_SKIPINSERTED=ON"
	su - $instanceName -c  "db2set DB2_NUM_CKPW_DAEMONS=0"
	su - $instanceName -c  "db2set DB2LOCK_TO_RB=STATEMENT"

	rc=$?
	if [[ ${rc} -ne 0 ]] ; then
	   echo "Failed to create database."
	   exit ${rc}
	fi
}

function restart_db2 {
	# Restart DB2
	su - $instanceName -c  "db2stop force"
	su - $instanceName -c  "db2start"
}

function enable_ip_port_for_db2 {
	su - $instanceName -c  "db2 update dbm cfg using SVCENAME $1"
	su - $instanceName -c  "db2set DB2COMM=tcpip"
	restart_db
}

function delete_db_and_catalog {
	su - $instanceName -c  "db2 catalog db $1"
	su - $instanceName -c  "db2 drop db $1"
}

#line="passdb backend ="
#to comment it out:
#sed -i "/${line}/ s/^/# /" $F_NAME 
#uncomment:
#sed -i "/${line}/ s/# *//" $F_NAME

function bluepages {
	cell=$1
	node=$2

	if [ $PROFILE_TYPE == "default" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -user $WHV_USER -password $WAS_PASSWORD -lang jython -c "from DCA_libraries import bluepages; bluepages('$cell', '$node')"
	elif [ $PROFILE_TYPE == "dmgr" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $WAS_PASSWORD -lang jython -c "from DCA_libraries import bluepages; bluepages('$cell', '$node')"
	fi
}

function renameCell {
	new_cell_name=$1
	new_node_name=$2

	#kill_process $WAS_PROFILE_ROOT/logs/dmgr/dmgr.pid
	pid=$(cat $WAS_PROFILE_ROOT/logs/dmgr/dmgr.pid)
	kill -9 $pid

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/stopManager.sh -username ${WHV_USER} -password ${WAS_PASSWORD}"

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/wsadmin.sh -conntype none -user ${WHV_USER} -password ${WAS_PASSWORD} -lang jython -c \"from DCA_libraries import renameCell; renameCell('${new_cell_name}', '${new_node_name}', '${NODE_NAME}')\""

	rename_cell_node ${new_cell_name} ${new_node_name}

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/startManager.sh"

}

function renameNode {
	new_cell_name=$1
	new_node_name=$2
	DMGR_JMX_PORT=8879

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/stopNode.sh -user ${WHV_USER} -password ${HTTPPASS}"

	node_names=`$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import renameNode; renameNode('$new_node_name')"`

	new_node_name=${node_names#*@ } # Remove everything up to a @ and space 

	new_node_name=`trim_whitespace $new_node_name`

	rename_cell_node ${new_cell_name} ${new_node_name}

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/renameNode.sh ${DMGR_HOST} ${DMGR_JMX_PORT} ${new_node_name} -user ${WHV_USER} -password ${HTTPPASS}"

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/startNode.sh"
}

function updateMapModulesToServers {
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import updateMapModulesToServers; updateMapModulesToServers()"
} 


function createCluster {
	clusterName=$1
	serverName=$2

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createCluster; createCluster('$clusterName', '$serverName')"
}

function createJAASDataSource {
	Database=$1
	Alias=$2
	UserName=$3
	Data_source_name=$4
	JNDI_Name=$5
	Database_name_url=$6
	Server_name=$7
	Port_number=$8
	Cluster_Name=$9

	#echo $Database $Alias $UserName $Data_source_name $JNDI_Name $Database_name_url $Server_name $Port_number

	if [ $PROFILE_TYPE == "default" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createJAASDataSource; createJAASDataSource ('$Database', '$Alias $UserName', '$Data_source_name', '$JNDI_Name', '$Database_name_url', '$Server_name', '$Port_number', '$Cluster_Name')"
	elif [ $PROFILE_TYPE == "dmgr" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createJAASDataSource; createJAASDataSource('$Database', '$Alias', '$UserName', '$Data_source_name', '$JNDI_Name', '$Database_name_url', '$Server_name', '$Port_number', '$Cluster_Name')"
	fi
}  

function propagateKeyring {
	dmgr_path=$1
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import propagateKeyring; propagateKeyring('$dmgr_path')"
}

function getdownloadfile_old {
	#REMOTE_SERVER_DOWNLOAD=http://10.30.128.35/WAS/Oracle11gR2.cfg
	REMOTE_SERVER_DOWNLOAD=$1
	DOWNLOAD_FILE=${REMOTE_SERVER_DOWNLOAD##*/}
	curl -O $REMOTE_SERVER_DOWNLOAD
	if [ $# -gt 1 ] && [ `echo $2 | awk '{print tolower($0)}'` = "yes" ] ; then
		while read line ;  do 
			if [[ ! ${#line} = 0 ]] ; then
				curl -O $line 
			fi
		done < $DOWNLOAD_FILE 
	fi
}

# getdownloadfile http://10.30.128.35/WAS/Oracle11gR2.zip
# getdownloadfile -i Oracle11gR2.cfg
# getdownloadfile -b http://10.30.128.35/WAS/Oracle11gR2.zip
function getdownloadfile {
	if [[ $# -eq 1 ]] ; then
		curl -O $1
	elif [ $1 = '-i' ] ; then
		xargs -n 1 curl -O < $2
	elif [ $1 = '-b' ] ; then
		DOWNLOAD_URL=$2
		DOWNLOAD_FILE=${DOWNLOAD_URL##*/}
		curl -O $DOWNLOAD_URL
		xargs -n 1 curl -O < $DOWNLOAD_FILE
	else
		echo ""
	fi
}

function downloadFile {
	if [ ! -d /tmp/$remoteWebServerDir/logs ]; then
		mk_dir /tmp/$remoteWebServerDir/logs
	fi

	cd /tmp/$remoteWebServerDir

	curl -O $REMOTE_SERVER_DOWNLOAD

	unzip -l $remoteWebServerFile > $remoteWebServerDir.txt

	unzip -o $remoteWebServerFile

	package=`cat $remoteWebServerDir.txt | awk '$1=="0" {print $4}'| awk '$1 ~/configurations/' | sed -n '1,1p'`
	base=${package#*/} # looking for a particular directory
	directory=${base%?} # trim the last character in the word.

	if [ ! -z "${directory}" ]; then
		mk_dir /$directory
		yes | cp -rf /tmp/$remoteWebServerDir/$package* /$directory
	fi

	rm -f $remoteWebServerDir.txt

	echoLog "Set permissions"
	chmod -R ug+rwx $SCRIPT_DIR

	#go back to previous directory
	cd -
}

function installApps {
	App_Name=$1
	ear_file_name=$2
	cluster_name=$3
	mapModVH=$4
	installType=$5

	if [ $PROFILE_TYPE == "default" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import installApps; installApps ('$App_Name', '$ear_file_name', '$cluster_name', '$mapModVH', '$installType')"
	elif [ $PROFILE_TYPE == "dmgr" ] ; then
		$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import installApps; installApps ('$App_Name', '$ear_file_name', '$cluster_name', '$mapModVH', '$installType')"
	fi
}

function createVirtualHost_wip {
	vhostName=$1
	port=$2
	label=$3 

	hostName=`hostName`  

	echoLog "Listen $hostName:7443" $httpConfFile
	echoLog "                 "     $httpConfFile
	echoLog "<VirtualHost $hostName:7443>" $httpConfFile
	echoLog "##Add Content Here for new virtual host##" $httpConfFile
	echoLog "   SSLEnable" $httpConfFile
	echoLog "   SSLServerCert ${label}" $httpConfFile
	echoLog "   ErrorLog $MOUNT_POINT/http/${vhostName}_error.log " $httpConfFile
	echoLog "   CustomLog $MOUNT_POINT/http/${vhostName}_access.log common" $httpConfFile
	echoLog "</VirtualHost>" $httpConfFile

	echoLog "virtual host creation starts"
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createVirtualHost; createVirtualHost('$vhostName', '$port', '$hostName')"

	cd -
}

function createVirtualHost {
	
	VirtualHostName=$1
	VPort=$2
	VLabel=$3

	echo vhostName + $VirtualHostName
	echo port + $VPort
	echo label + $VLabel

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createVirtualHost; createVirtualHost('$DC_Name', '$Group_Name')"
}

function enableSecurityLDAP {
	
	primaryUser=$1
	ldapPrimaryHost=$2
	bindPassword=$3
	ldapPort=$4
	ldapServerType=$5
	baseDN=$6
	bindDN=$7

	#$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import enableSecurity; enableSecurity()"
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import enableSecurityLDAP; enableSecurityLDAP('$primaryUser', '$ldapPrimaryHost', '$bindPassword', '$ldapPort', '$ldapServerType', '$baseDN' , '$bindDN')"
}



function createJMS {
	Factory_Name=$1
	JNDI_Name=$2
	QMGR_NAME=$3
	QMGR_HOST_NAME=$4
	QMGR_PORT_NUMBER=$5
	QMGR_CHANNEL_NAME=$6
	cluster_scope=$7

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createJMS; createJMS ('$Factory_Name', '$JNDI_Name', '$QMGR_NAME', '$QMGR_HOST_NAME', '$QMGR_PORT_NUMBER', '$QMGR_CHANNEL_NAME', '$cluster_scope')"
}

function createIHS {
	hostname=`hostname`
	# duration here is 10 years, if you want just 365*number of years
	duration=3650
	nodeName=$1
	memberName=$2

	getNodeIHS=`${WAS_PROFILE_ROOT}/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user ${WHV_USER} -password ${HTTPPASS} -lang jython -c "from DCA_libraries import getNodeIHS; getNodeIHS('${nodeName}', '${memberName}')"` 		

	echo "$getNodeIHS" >  $PWD/getNodeIHS.txt

	nodeName=`cat getNodeIHS.txt | grep nodeName`
	memberName=`cat getNodeIHS.txt | grep memberName`

	nodeName=`echo $nodeName | grep nodeName`
	nodeName=${nodeName#*@ } # Remove everything up to a @ and space 
	nodeName=`trim_whitespace $nodeName`

	memberName=`echo $memberName | grep memberName`
	memberName=${memberName#*@ } # Remove everything up to a @ and space 
	memberName=`trim_whitespace $memberName`

	rm -rf $PWD/getNodeIHS.txt

	chown_dca $WHV_USER ${PLG_HOME}

	mk_dir ${PLG_HOME}/config/${memberName}
	mk_dir ${PLG_HOME}/logs/${memberName}

	file_exists ${httpConfFile}
	chown_backup ${httpConfFile}
	chown_backup ${adminConfFile}

	cp -p ${WAS_PROFILE_ROOT}/config/cells/plugin-cfg.xml ${PLG_HOME}/config/${memberName}/plugin-cfg.xml
	chmod_dca ${PLG_HOME}/config/${memberName}/plugin-cfg.xml
	chown_backup ${PLG_HOME}/config/${memberName}/plugin-cfg.xml 

	sed_aix_linux "s/@@AdminPort@@/8008/g" ${adminConfFile} 
	sed_aix_linux "s/@@SetupadmUser@@/$WHV_USER/g" ${adminConfFile} 
	sed_aix_linux "s/@@SetupadmGroup@@/users/g" ${adminConfFile}

	pluginConfigFile=${PLG_HOME}/config/${memberName}/plugin-cfg.xml

	wasModule=${PLG_HOME}/bin/64bits/mod_was_ap22_http.so
	file_exists ${wasModule}
	export WAS_PLUGIN_DRIVER=${wasModule}
		
	sed_aix_linux "s%WebSpherePluginConfig%#WebSpherePluginConfig%" ${httpConfFile} 

	echoLog "----------------- Config IHS ---------------------------"

	${IHS_HOME}/bin/htpasswd -cmb ${IHS_HOME}/conf/admin.passwd ${WHV_USER} ${HTTPPASS}	

	# Config SSL
	config_http_ssl ${memberName} ${hostname}
	echoLog "----------------- Config SSL ---------------------------"

	${IHS_HOME}/bin/gskcmd -keydb -create -db ${IHS_HOME}/${memberName}.kdb -pw ${HTTPPASS} -type cms -expire $duration -stash

	sslKeyFile=${IHS_HOME}/${memberName}.kdb
	#file_exists ${sslKeyFile}

	${WAS_PROFILE_ROOT}/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user ${WHV_USER} -password ${HTTPPASS} -lang jython -c "from DCA_libraries import createIHS; createIHS ('${nodeName}', '${memberName}', '${hostname}', '${WHV_USER}', '${HTTPPASS}')"

	chown_dca $WHV_USER ${PLG_HOME}

	echoLog "----------------- Restart webserver ---------------------------"

	stop_start_webserver
}

#Configure an HTTP server and WebSphere Application Server plug-in. 
#http://java.boot.by/ibm-317/ch05s02.html
#How to have multiple IHS (IBM HTTP) web servers in front of your WAS (WebSphere Application Server) app servers?
# https://developer.ibm.com/answers/questions/210148/how-to-have-multiple-ihs-ibm-http-web-servers-in-f.html
function createIHS_no_WAS_wip {
	hostname=`hostname`
	# duration here is 10 years, if you want just 365*number of years
	duration=3650
	nodeName=$1
	memberName=$2
    WAS_PROFILE_ROOT=${WAS_PROFILE_ROOT:-/opt/IBM/WebSphere/AppServer}
	getNodeIHS=`${WAS_PROFILE_ROOT}/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user ${WHV_USER} -password ${HTTPPASS} -lang jython -c "from DCA_libraries import getNodeIHS; getNodeIHS('${nodeName}', '${memberName}')"` 		

	echo "$getNodeIHS" >  $PWD/getNodeIHS.txt

	nodeName=`cat getNodeIHS.txt | grep nodeName`
	memberName=`cat getNodeIHS.txt | grep memberName`

	nodeName=`echo $nodeName | grep nodeName`
	nodeName=${nodeName#*@ } # Remove everything up to a @ and space 
	nodeName=`trim_whitespace $nodeName`

	memberName=`echo $memberName | grep memberName`
	memberName=${memberName#*@ } # Remove everything up to a @ and space 
	memberName=`trim_whitespace $memberName`

	rm -rf $PWD/getNodeIHS.txt

	chown_dca $WHV_USER ${PLG_HOME}

	mk_dir ${PLG_HOME}/config/${memberName}
	mk_dir ${PLG_HOME}/logs/${memberName}

	file_exists ${httpConfFile}
	chown_backup ${httpConfFile}
	chown_backup ${adminConfFile}

	cp -p ${WAS_PROFILE_ROOT}/config/cells/plugin-cfg.xml ${PLG_HOME}/config/${memberName}/plugin-cfg.xml
	chmod_dca ${PLG_HOME}/config/${memberName}/plugin-cfg.xml
	chown_backup ${PLG_HOME}/config/${memberName}/plugin-cfg.xml 

	sed_aix_linux "s/@@AdminPort@@/8008/g" ${adminConfFile} 
	sed_aix_linux "s/@@SetupadmUser@@/$WHV_USER/g" ${adminConfFile} 
	sed_aix_linux "s/@@SetupadmGroup@@/users/g" ${adminConfFile}

	pluginConfigFile=${PLG_HOME}/config/${memberName}/plugin-cfg.xml

	wasModule=${PLG_HOME}/bin/64bits/mod_was_ap22_http.so
	file_exists ${wasModule}
	export WAS_PLUGIN_DRIVER=${wasModule}
		
	sed_aix_linux "s%WebSpherePluginConfig%#WebSpherePluginConfig%" ${httpConfFile} 

	echoLog "----------------- Config IHS ---------------------------"

	${IHS_HOME}/bin/htpasswd -cmb ${IHS_HOME}/conf/admin.passwd ${WHV_USER} ${HTTPPASS}	

	# Config SSL
	config_http_ssl ${memberName} ${hostname}
	echoLog "----------------- Config SSL ---------------------------"

	${IHS_HOME}/bin/gskcmd -keydb -create -db ${IHS_HOME}/${memberName}.kdb -pw ${HTTPPASS} -type cms -expire $duration -stash

	sslKeyFile=${IHS_HOME}/${memberName}.kdb
	#file_exists ${sslKeyFile}

	${WAS_PROFILE_ROOT}/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user ${WHV_USER} -password ${HTTPPASS} -lang jython -c "from DCA_libraries import createIHS; createIHS ('${nodeName}', '${memberName}', '${hostname}', '${WHV_USER}', '${HTTPPASS}')"

	chown_dca $WHV_USER ${PLG_HOME}

	echoLog "----------------- Restart webserver ---------------------------"

	stop_start_webserver
}

function createIHS_no_WAS {
		hostname=`hostname`
	# duration here is 10 years, if you want just 365*number of years
	
	duration=3650
	
	nodeName=$1
	webServerName=$2
	configDir=$3
	webPort=$4
	serviceName=$5
    
	chown_dca $WHV_USER ${PLG_HOME}
	
	mk_dir ${IHS_INSTALL_ROOT}/${configDir}
	mk_dir ${IHS_INSTALL_ROOT}/logs/${configDir}
	mk_dir ${PLG_HOME}/config/${memberName}
	mk_dir ${PLG_HOME}/logs/${memberName}

	#file_exists ${httpConfFile}
	#chown_backup ${httpConfFile}
	#chown_backup ${adminConfFile}
	
	cp -p ${IHS_INSTALL_ROOT}/conf/* ${IHS_INSTALL_ROOT}/${configDir}
	
	sed_aix_linux "s/@@configDir@@/$configDir/g" $SCRIPT_DIR/httpd.conf
	sed_aix_linux "s/@@webPort@@/$webPort/g" $SCRIPT_DIR/httpd.conf 
	sed_aix_linux "s/@@ServerName@@/${hostname}/g" $SCRIPT_DIR/httpd.conf
	sed_aix_linux "s/@@memberName@@/$memberName/g" $SCRIPT_DIR/httpd.conf
	sed_aix_linux "s/@@serviceName@@/$serviceName/g" $SCRIPT_DIR/httpd.conf
	
	cp -p $SCRIPT_DIR/httpd.conf ${IHS_INSTALL_ROOT}/${configDir}
	
	sed_aix_linux "s/$configDir/@@configDir@@/g" $SCRIPT_DIR/httpd.conf
	sed_aix_linux "s/$webPort/@@webPort@@/g" $SCRIPT_DIR/httpd.conf 
	sed_aix_linux "s/${hostname}/@@ServerName@@/g" $SCRIPT_DIR/httpd.conf
	sed_aix_linux "s/$memberName/@@memberName@@/g" $SCRIPT_DIR/httpd.conf
	sed_aix_linux "s/$serviceName/@@serviceName@@/g" $SCRIPT_DIR/httpd.conf
	
	#chmod_dca ${IHS_INSTALL_ROOT}/${configDir}/*
	#chown_backup ${IHS_INSTALL_ROOT}/${configDir}/*
	
	cp -p ${PLG_HOME}/config/webserver1/* ${PLG_HOME}/config/${memberName}/
	
	sed_aix_linux "s/@@memberName@@/$memberName/g" $SCRIPT_DIR/plugin-cfg.xml
	
	cp -p $SCRIPT_DIR/plugin-cfg.xml ${PLG_HOME}/config/${memberName}
	
	sed_aix_linux "s/$memberName/@@memberName@@/g" $SCRIPT_DIR/plugin-cfg.xml

	#cp -p ${WAS_PROFILE_ROOT}/config/cells/plugin-cfg.xml ${PLG_HOME}/config/${memberName}/plugin-cfg.xml
	#chmod_dca ${PLG_HOME}/config/${memberName}/plugin-cfg.xml
	#chown_backup ${PLG_HOME}/config/${memberName}/plugin-cfg.xml 

	#sed_aix_linux "s/@@AdminPort@@/8008/g" ${adminConfFile} 
	#sed_aix_linux "s/@@SetupadmUser@@/$WHV_USER/g" ${adminConfFile} 
	#sed_aix_linux "s/@@SetupadmGroup@@/users/g" ${adminConfFile}

	pluginConfigFile=${PLG_HOME}/config/${memberName}/plugin-cfg.xml

	wasModule=${PLG_HOME}/bin/64bits/mod_was_ap22_http.so
	file_exists ${wasModule}
	export WAS_PLUGIN_DRIVER=${wasModule}
		
	sed_aix_linux "s%WebSpherePluginConfig%#WebSpherePluginConfig%" ${httpConfFile} 

	#echoLog "----------------- Config IHS ---------------------------"

	#${IHS_HOME}/bin/htpasswd -cmb ${IHS_HOME}/conf/admin.passwd ${WHV_USER} ${HTTPPASS}	

	# Config SSL
	#config_http_ssl ${memberName} ${hostname}
	#echoLog "----------------- Config SSL ---------------------------"

	#${IHS_HOME}/bin/gskcmd -keydb -create -db ${IHS_HOME}/${memberName}.kdb -pw ${HTTPPASS} -type cms -expire $duration -stash

	#sslKeyFile=${IHS_HOME}/${memberName}.kdb
	#file_exists ${sslKeyFile}

	#${WAS_INSTALL_ROOT}/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user ${WHV_USER} -password ${HTTPPASS} -lang jython -c "from DCA_libraries import createIHS; createIHS ('${nodeName}', '${memberName}', '${hostname}', '${WHV_USER}', '${HTTPPASS}')"
	#$WAS_INSTALL_ROOT/bin/wsadmin.sh -conntype JSR160RMI -host $DMGR_HOST -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWebServer; createWebServer('$nodeName', '$webServerName', '$configDir', '$webPort', '$adminPort', '$adminUserID' , '$adminPasswd')"
	
	chown_dca $WHV_USER ${PLG_HOME}
	chown_dca $WHV_USER ${WAS_INSTALL_ROOT}
	chown_dca $WHV_USER ${IHS_INSTALL_ROOT}

	echoLog "----------------- Restart webserver ---------------------------"
	
	su ${WHV_USER} -c "${IHS_INSTALL_ROOT}/bin/apachectl -k start -f ${IHS_INSTALL_ROOT}/$configDir/httpd.conf"

	#stop_start_webserver
}

function create_db {
	inst_name=$1
	db_name=$2
	sqltype=$3
	codeset=$4
	territory=$5
	collate=$6
	pagesize=$7
	dataMountPoint=$8

	if [[ ${sqltype} == "ORACLE" ]] ; then
		if [[ ${pagesize} -ne 32 ]] ; then
			echo "Force overwriting database page size to 32 K for Oracle compatibility..."
			pagesize=32
		fi
	fi

	db2 "CREATE DATABASE ${db_name} ON ${dataMountPoint} USING CODESET ${codeset} TERRITORY ${territory} COLLATE USING ${collate} PAGESIZE ${pagesize} K"
	rc=$?
	if [[ ${rc} -ne 0 ]] ; then
	   echo "Failed to create database."
	   exit ${rc}
	fi
}

### WIP ###
function install_wmq {
	mk_dir $SCRIPT_DIR/tmp
	
	WS_MQ=`get_properties "WS_MQ_FOR_AIX_V7.5.0.1.tar.z"`
	AixPPC64=`get_properties "7.5.0-WS-MQ-AixPPC64-FP0005.tar.Z"`

	# unzip
	gunzip < $SCRIPT_DIR/tmp/$WS_MQ | tar -xvf -  | tee $PWD/pureappErr.log

	# install
	installp -acY -d . mqm.*  | tee $PWD/pureappErr.log
	wait $!
	RC=$?
	if [[ $RC -ne 0 ]]; then
		echoLog "Errors received from installp execution .."
	fi
	 
	rm -rf $SCRIPT_DIR/tmp/$WS_MQ

	gunzip < $SCRIPT_DIR/tmp/$AixPPC64 | tar -xvf - | tee $PWD/pureappErr.log

	# fix pack installation
	/usr/lib/instl/sm_inst installp_cmd -a -d . -f _update_all -S -X

	cd $SCRIPT_DIR/

	if [[ $RC -eq 0 ]]; then
	  # delete MQ V7.5.0.1 installer 
	  rm -rf $SCRIPT_DIR/tmp
	fi

	# set path
	cd /usr/mqm/bin/
	./setmqinst -i -p /usr/mqm
}

### WIP ###
function install_iib {
	echo
}

function extend_hard_disk { 
	partition=$1
	size_l=$2
	# Log /usr extension by 5GB
	echoLog "********** Logging usr extension **********"
	# df -g /usr
	df -g $partition
	lspv
	lsvg
	lsvg rootvg | grep -i 'FREE PPs:'
	echo
	chdev -l hdisk1 -a pv=yes
	extendvg -f rootvg hdisk1
	# chfs -a size=+5G /usr
	chfs -a size=+${size_l}G $partition
	lsvg rootvg | grep -i 'FREE PPs:'
	# df -g /usr
	df -g $partition
}

function random {
	if [ $# -eq 0 ]; then
		minimal=10; maximal=120
	else
		minimal=$1; maximal=$2
	fi
	count=3; val2=0
	val=`expr $maximal \- $minimal`
	while [[ $count -gt 0 ]];do
		(( val2 += $((RANDOM%val+minimal))))
		(( count -= 1 ))
	done
	echo `expr $val2 / 2`
}

function get_response_file {
	file_name=$1
	toking_search=$2
	password=`cat $file_name | grep $toking_search`
	echo ${password##*=}
}

function get_file_mount {
	location=$1
	searchfile=$2
	if [[ `uname` == 'AIX' ]]; then   
		set -A FIND_DIR1 `find $location -name $searchfile` 
	else
		eval 'FIND_DIR1=(`find $location -name $searchfile`)'
	fi
	echo ${FIND_DIR1}
}

# https://www-01.ibm.com/support/knowledgecenter/ssw_aix_71/com.ibm.aix.cmds1/crfs.htm
# http://mailist.wikia.com/wiki/Create_new_filesystem_in_AIX
# http://www.torontoaix.com/wpar/create-wpar
function extra_disk {
	cp -p /etc/filesystems /etc/filesystems.bak
	chfs -a size=40G /
	crfs -v jfs2 -g rootvg -a size=100G -p rw -m /opt
	crfs -v jfs2 -g rootvg -a size=30G -p rw -m /tmp
	mount /tmp
	chps -s 96 hd6
	df -g
}

function get_virtualimage_properties {
	val=`grep -r ${1} /etc/virtualimage.properties`
	echo ${val##*=}
}

function fix_virtualimage {
	sed '/$$status_id$$=/d' /etc/virtualimage.properties > /etc/virtualimage.properties.bak
	move_file /etc/virtualimage.properties
}

function nppFirewall {
	PORT=$1
	if [ ${#PORT} = 0 ]; then
		PORT=ports248.txt
	fi
	for port in `cat $PORT`; do
		python -c "from DCA_libraries import nppFirewall; nppFirewall('$port')"
	done
}

function getusedports {
	for port in `netstat -ant | egrep 'Proto|LISTEN' | awk '{print $4}' | sort | uniq | sed -e 's/*.//g' | sed -e 's/127.0.0.1.//g' | sed -e 's/Local//g'` ; do
		python -c "from DCA_libraries import nppFirewall; nppFirewall('$port')"
	done
}

function download_file {

	INSTALL=$1
	LOCATION=$2	
	MODE=$3
	cd $LOCATION
	
	case "${MODE}" in
	zip)
		for list in `find $INSTALL -name \*.${MODE} -print`; do
			#unzip ${list} 
			yes | unzip -o ${list}
		done
		;;
	tar)
		for list in `find $INSTALL -name \*.${MODE} -print`; do
			tar -xvf ${list}
		done
		;;
	tar.Z)
		for list in `find $INSTALL -name \*.${MODE} -print`; do
			gunzip < ${list} | tar -xvf - 2>&1
		done
		;;
	tgz)
		for list in `find $INSTALL -name \*.${MODE} -print`; do
			gunzip < ${list} | tar -xvf - 2>&1
		done
		;;
	*)
		exit 1
	esac
	cd -
}

####### ########### Start Adding for CPALL

function _prepareInput {
	su ${WHV_USER} -c cp -R /tmp/${remoteWebServerDir}/ /tmp/DCA_CFG/
}

function _createNodeGroup {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createNodeGroup; createNodeGroup()"
}

function _addNodeGroupMember {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import addNodeGroupMember; addNodeGroupMember()"
}

function _createCoreGroup {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createCoreGroup; createCoreGroup()"
}

function _createTemplateCluster {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createTemplateCluster; createTemplateCluster()"
}

function _modifyServerPort {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyServerPort; modifyServerPort()"
}

function _setJVMPropertiesCluster {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import setJVMPropertiesCluster; setJVMPropertiesCluster()"
}

function _setJVMPropertiesNode {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import setJVMPropertiesNode; setJVMPropertiesNode()"
}

function _modifyThreadPool {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyThreadPool; modifyThreadPool()"
}

function _createDynamicCluster {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createDynamicCluster; createDynamicCluster()"  
}

function _createJAASAuthData {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createJAASAuthData; createJAASAuthData()" 
}

function _createXADataSource {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createXADataSource; createXADataSource()"

} 

function _createXADataSourceOracle {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createXADataSourceOracle; createXADataSourceOracle()"

}  
 
function _setJVMLogCluster {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import setJVMLogCluster; setJVMLogCluster()"
}

function _setJVMLogNode {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import setJVMLogNode; setJVMLogNode()"
}

function _modifyTransactionLog {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyTransactionLog; modifyTransactionLog()"
}

function _createEnvironmentEntries {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createEnvironmentEntries; createEnvironmentEntries()"
}

function _modifyProcessExecutionCluster {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyProcessExecutionCluster; modifyProcessExecutionCluster()"
}

function _modifyProcessExecutionNode {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyProcessExecutionNode; modifyProcessExecutionNode()"
}

function _modifyCPCustomProperties {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyCPCustomProperties; modifyCPCustomProperties()"

} 

function _modifyDataSourceProperty {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyDataSourceProperty; modifyDataSourceProperty()"

} 

function _addHostAlias {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import addHostAlias; addHostAlias()"

}

function _createSIBus {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createSIBus; createSIBus()" 
}

function _addSIBusMember {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import addSIBusMember; addSIBusMember()" 
}

function _createSIBForeignBus {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createSIBForeignBus; createSIBForeignBus()" 
}

function _createSIBDestination {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createSIBDestination; createSIBDestination()" 
}

function _createSIBJMSConnectionFactory {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createSIBJMSConnectionFactory; createSIBJMSConnectionFactory()" 
}

function _createWMQConnectionFactory {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWMQConnectionFactory; createWMQConnectionFactory()" 
}

function _modifyWMQConnectionFactory {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyWMQConnectionFactory; modifyWMQConnectionFactory()" 
}

function _createJMSQueue {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createJMSQueue; createJMSQueue()" 
}

function _createWMQQueue {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWMQQueue; createWMQQueue()" 
}

function _createSIBJMSActivationSpec {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createSIBJMSActivationSpec; createSIBJMSActivationSpec()" 
}

function _createWMQActivationSpec {
		
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWMQActivationSpec; createWMQActivationSpec()" 
}

function _modifyWMQActivationSpec {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifyWMQActivationSpec; modifyWMQActivationSpec()" 
}

function _createWebsphereVariable {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWebsphereVariable; createWebsphereVariable()"

}

function _enableCPALLLDAP {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import enableCPALLLDAP; enableCPALLLDAP()"
	
}

function _createGroup {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createGroup; createGroup()"
}

function _mapUsersToAdminRole {
		
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import mapUsersToAdminRole; mapUsersToAdminRole()"
}

function _mapGroupsToAdminRole {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import mapGroupsToAdminRole; mapGroupsToAdminRole()"
}


function _createWebServer {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWebServer; createWebServer()"
} 

function _configWebServer {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import configWebServer; configWebServer()"

} 

function _modifySIBDestination {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import modifySIBDestination; modifySIBDestination()"
}

function _createSIBContextInfo {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createSIBContextInfo; createSIBContextInfo()"

}

function _createJVMCustomProperties {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createJVMCustomProperties; createJVMCustomProperties()"

}

function _createScheduler {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createScheduler; createScheduler()"

}

function _createWorkManager {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWorkManager; createWorkManager()"

}

function _createWCCustomProperties {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createWCCustomProperties; createWCCustomProperties()"

}

function _createASCustomProperties {
	
	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import createASCustomProperties; createASCustomProperties()"
}

function _syncNode {

	$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "from DCA_libraries import syncNode; syncNode()"

}

#install_xlc $XLC_PATH $PWD 'tar.Z'
function install_xlc {
	if ! test `which /opt/IBM/xlc` ; then
		XLC_PATH=$1
		PATH=$2
		TYPE=$3
		download_file $XLC_PATH $PATH $TYPE
		cd - ; cd runtime
		installp -acY -d . xl* 2>&1
		cd -
	fi
}

#extract_sources $XLC_PATH $PWD 'tar.Z'
function extract_sources {
	INSTALL=$1
	LOCATION=$2	
	MODE=$3
	download_file $INSTALL $LOCATION $MODE
}

function check_user {
    if [ $(id -un) != "${1}" ]; then
        echoLog "you must run this as ${1}"
    fi
}

#runrcmd "ssh -o StrictHostKeyChecking=no root@10.30.133.67" "$password"
function runrcmd {
	expect -c "
	set timeout 10
	spawn $1 
	expect \"*password:*\" 
	send \"$2\r\"
	#expect \"#\"
	#send \"host `hostname`\r\"
	interact 
    "
}

function runrcmd_vmo {
	expect -c "
	set timeout 10
	spawn $1 
	expect \"*confirmation required yes/no*\" 
	send \"yes\r\"
	expect \"*confirmation required yes/no*\" 
	send \"yes\r\"
	interact 
    "
}

function set_profile {
	insert_in_file "$1" /etc/profile
}

function set_resolv {
	insert_in_file "$1" /etc/resolv.conf
}

function renameNode_CPALL {
	#new_node_name=`hostname -s`
	new_node_name=$1
	DMGR_JMX_PORT=8879

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/stopNode.sh -user ${WHV_USER} -password ${HTTPPASS}"

	new_cell_name=`$WAS_PROFILE_ROOT/bin/wsadmin.sh -conntype JSR160RMI -port 9809 -user $WHV_USER -password $HTTPPASS -lang jython -c "AdminControl.getCell()"`

	#rename_cell_node ${new_cell_name} ${new_node_name}

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/renameNode.sh ${DMGR_HOST} ${DMGR_JMX_PORT} ${new_node_name} -user ${WHV_USER} -password ${HTTPPASS}"

	su ${WHV_USER} -c "${WAS_PROFILE_ROOT}/bin/startNode.sh"
}

####### ########### End Adding for CPALL

function get_history {
	history -1000 | tee -a $1
}

function get_latency {
	if [[ ! -z $1 ]] ; then
		#directory to write info, info must be a file not a directory
		date; dd if=/dev/zero of=$1 bs=512 count=12000000;date
	else
		date; dd if=/dev/zero of=$PWD/`hostname`.`date +%s` bs=512 count=12000000;date
	fi
}

#tokenized "username/ernese/password/zaq12wsx/keyfile/cde32wsx/keyname/oiuy/crypto/0900" '/'
function tokenized {
	string=$1; 	token=$2
	echo `(IFS=$token; for word in $string; do echo "$word"; done)`
}

#name_value_pair ${linetokens[@]}
function name_value_pair {
	for arg in "$@"; do
		param=${arg%%=*}
		value=${arg##*=}
		echo $param=$value
	done
}

# https://www.ibm.com/developerworks/community/blogs/AIXDownUnder/entry/putting_the_x_in_aix12?lang=en
# https://www.ibm.com/developerworks/community/blogs/paixperiences/entry/remotex11aix?lang=en
# http://scn.sap.com/community/unix/blog/2012/12/26/resolve-error-cant-open-display-on-aix
# http://aix4admins.blogspot.sg/2011/06/using-x11-forwarding-in-ssh-ssh.html
# http://websphere-howto.blogspot.sg/2014/02/install-ibm-websphere-application.html?m=1
function X11forwarding {
	echo "X11Forwarding yes" | tee -a /etc/ssh/sshd_config
: '
	#echo "X11DisplayOffset 10" | tee -a /etc/ssh/sshd_config
	#echo "X11UseLocalhost yes" | tee -a /etc/ssh/sshd_config
	#export DISPLAY="127.0.0.1:10.0"
	#echo $DISPLAY
	#xauth list
	#cd /etc/ssh
'
	stopsrc -s sshd; wait 2; startsrc -s sshd
	#startx
	# need to initiate another session before X11 forwarding to work as this command "stopsrc -s sshd; wait 2; startsrc -s sshd" \
	does not seem to work as entended
	xclock &
}

function manageprofiles {
	#Node Agent 01
	#Use a unique name even though you plan to federate the custom profile or stand alone profile into a deployment manager cell.
	#WAS_HOME=/opt/IBM/WebSphere/AppServer
	PROFILE_NAME=PRPC_SMA_Node_Test03
	#WAS_PROFILE_DIR=/opt/IBM/WebSphere/Profiles
	#CELL_NAME=Cell_${PROFILE_NAME}
	HOST=`hostname`
	NODE_NAME=$PROFILE_NAME
	START_PORT=10100
	#DMGR_ADMIN_USER=wasadmin
	DMGR_ADMIN_PASSWORD=$HTTPPASS
	DMGR_SOAP_PORT=8879
	DMGR_HOST=`hostname`
	${WAS_HOME}/bin/manageprofiles.sh -create -profileName ${PROFILE_NAME} -profilePath ${PROFILES_HOME}/${PROFILE_NAME} -templatePath ${WAS_HOME}/profileTemplates/managed -cellName Cell_${CELL_NAME} -hostName ${HOST} -nodeName ${NODE_NAME} -startingPort ${START_PORT} -dmgrHost ${DMGR_HOST} -dmgrPort ${DMGR_SOAP_PORT} -dmgrAdminUserName ${WAS_USERNAME} -dmgrAdminPassword ${DMGR_ADMIN_PASSWORD} -enableAdminSecurity true -isDefault
}

function makesymlink {
	echo "Symlink name:"
	read sym
	echo "File to link to:"
	read fil
	ln -s $fil $sym
}

: '
function WIP {
a=0
n=${#town[*]}
while [[ $a -lt $n ]] ; do
	echo There is ${town[$a]}
    let a+=1
done

#while (($#)); do
while [ "$1" ]; do
	echo "yum install $1"
	shift
done
}

COUNT=0
for f in *.sh;
do
  let COUNT+=1
  echo "Processing BAR file: $f"
done

Firewall with AIX TCP/IP filtering
http://emmanuel.iffly.free.fr/doku.php?id=aix:aixfilter

'

DEBUG set +x

# scp -P 22 /tmp/gpfs.snapOut/24248364/all.1112151510.tar root@10.30.128.58:/tmp/log

# the next line calls the function passed as the first parameter to the script.
# the remaining script arguments can be passed to this function.
# DCA_libraries.sh random 10 200
#http://superuser.com/questions/106272/how-to-call-bash-functions
$1 $2 $3 $4 $5


