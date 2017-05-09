#!/bin/sh

. /etc/virtualimage.properties
SCRIPT_DIR=${SCRIPT_DIR:-`pwd`}
. $SCRIPT_DIR/DCA_libraries.sh

DEBUG set -x
# Log environment
echoLog "********** Logging Environment Variables **********"
set
echoLog "***************************************************"
echoLog "============== $0 ======================"

function _initialSetting {
	echoLog "_initialSetting"
	set_time_zone 'Asia/Bangkok'
	# disable ipsec 4
	#disableIPsec4
	
	#wget_aix
	getdownloadfile $REMOTE_SERVER_DOWNLOAD
	downloadFile

	file_exists $configApps 
	clean_csv_files
	copyDCAartifacts

	install_db_driver "ORA10"
	install_db_driver "DB2"

	echoLog "version of current code release `lastmod $SCRIPT_DIR/configApps.sh` of file: $SCRIPT_DIR/configApps.sh"
	
	add_user "wasapp" "wasapp@dev" "monitor"
	usermod -g wasgroup wasapp
	
	was_groupname
}

function _postSetting {
	echoLog "_postSetting"
	echoLog "Set permissions to $WHV_USER for the following directories /tmp/$remoteWebServerDir | $SCRIPT_DIR and $WAS_PROFILE_ROOT"
	chown_dca $WHV_USER /tmp/${remoteWebServerDir}
	chown_dca $WHV_USER ${SCRIPT_DIR} 
	
	#chown_dca $WHV_USER ${WAS_INSTALL_ROOT}
	#chown_dca $WHV_USER ${WAS_PROFILE_ROOT}
	chown_dca $WHV_USER /opt/IBM/WebSphere/
	

	#chown_dca wasapp /wasapp
	#chown_dca $WHV_USER /wasdump
	#chown_dca $WHV_USER /wasbackup

	if [ "$PROFILE_TYPE" = "custom" ]; then
		gpfs=`df -g | grep /gpfs | awk '{ print $7 }'`
		chown_dca wasapp $gpfs/wasappshare
	fi
	usermod -g wasgroup wasapp
	chuser umask="002" wasapp
	chuser umask="002" virtuser
	
	chown -R virtuser:wasgroup /opt/IBM/WebSphere/Profiles
	chown -R wasapp:wasgroup /wasapp
	chown -R virtuser:wasgroup /wasdump
	chown -R virtuser:admingroup /wasbackup

}

function runrcmd_CPALL_monitor {
	echoLog "runrcmd_CPALL_monitor"
	expect -c "
	set timeout 10
	spawn $1
	expect \"Please Extend Filesystem / over 4 GB\" 
	send \"\r\"
	expect \"Press y to Continue Install software monitor OR n to quit\"
	send \"y\r\"
	expect \"Enter Choice\" 
	send \"1\r\" 
	expect \"Please kill process cron and Press Anykey to Continue\"
	send \"\r\"
	expect \"Enter Choice\"
	send \"\r\"
	interact
	"	
}

function _create_CPALL_profile {
	echoLog "_create_CPALL_profile"
	if [ `get_domain_name` = "cpall.co.th" ]; then 
		runrcmd_vmo 'vmo -p -o maxclient%=10 -o maxperm%=10'
		set_environment "hostname=`hostname`"
		set_environment 'PS1=$hostname:$USER:$PWD>'

		#Duplicatted with setEnv.sh
		#set_profile "set -o vi" 
		#set_profile "alias rm='rm -i'" 
		#set_profile "alias ll='ls -la'" 
		#set_profile "alias lg='ls -la |grep '" 

		#Disable Policy
		/usr/sbin/chfilt -v 4  -n '0' -a 'P'
		/usr/sbin/mkfilt -v4 -u

		#Duplicatted with setEnv.sh
		#set_resolv "search counterservice.co.th gosoft.co.th cpall.co.th cpretailink.co.th dynamic-logistics.com 7catalog.com cpram.co.th 7eleven.cp.co.th" 
		#set_resolv "nameserver  10.151.18.47" 
		#set_resolv "nameserver  10.151.18.12" 
		#set_resolv "nameserver  10.182.255.14"

		list_users "chuser umask=002"

		#Install monitor.sh selected only option 1.
		runrcmd_CPALL_monitor "$PWD/monitor.sh"
		usermod -G wasgroup wasapp
	fi
}

function _init {
	_initialSetting
	#_install_c_compiler
	#_create_CPALL_profile
}

#Create webserver instances on IHS Node only.
function decrypt_password {

	if [ -f security.csv ] ; then
		i=1

		while read line	   ; do
			test $i -eq 1 && ((i=i+1)) && continue

		  if aix ; then 
			set -A linetokens $line
		  else
			eval 'linetokens=($line)'
		  fi

			nodeName=${linetokens[0]}	
			memberName=${linetokens[1]}	
			password=${linetokens[2]}	
			webPort=${linetokens[3]}
			serviceName=${linetokens[6]}
			

			if [ ! -z "$password" ]; then	
			  /opt/IBM/WebSphere/AppServer/java/jre/bin/java -Djava.ext.dirs=/opt/IBM/WebSphere/AppServer/deploytool/itp/plugins/com.ibm.websphere.v85.core_1.0.1.v20121015_1658/wasJars -cp securityimpl.jar com.ibm.ws.security.util.PasswordDecoder $password | tee -a security.csv.log
			fi
				
			((++i))

		done < security.csv
	fi

}

function _configApps {
	i=1

	while read line	   ; do
	  test $i -eq 1 && ((i=i+1)) && continue  
	  
	  if aix ; then
		set -A linetokens $line
	  else
		eval 'linetokens=($line)'
	  fi
		
	  Cell_Name=${linetokens[0]}
	  Node_Name_dmgr=${linetokens[1]}
	  Node_Name_node=${linetokens[2]}
	  Node_Name_web=${linetokens[3]}
	  Member_Name_web=${linetokens[4]}
	  #$Label_name=${linetokens[5]}

	  #rename new cell name (done!)
	  if [ "$PROFILE_TYPE" = "dmgr" ]; then 
		if [ ! -z "$Cell_Name" ] && [ ! -z "$Node_Name_dmgr" ]; then
			renameCell $Cell_Name $Node_Name_dmgr
		fi
	  fi
			
	  # rename new node name (done!)
	  if [ "$PROFILE_TYPE" = "custom" ]; then
	   #backup_directory "NodeBackup" $WAS_PROFILE_ROOT
		if [ ! -z "$Cell_Name" ] && [ ! -z "$Node_Name_node" ]; then
		  renameNode $Cell_Name $Node_Name_node
		fi
	  fi
	  
	  #PROFILE_TYPE=${PROFILE_TYPE:-custom}
	  # create IHS server (done!)
	  if [ "$PROFILE_TYPE" = "custom" ] && [ ! -z "$IHS" ]; then
		#backup_directory "IHSBackup" $IHS_HOME
		if [ ! -z "$Node_Name_web" ] && [ ! -z "$Member_Name_web" ] ; then
		  createIHS $Node_Name_web $Member_Name_web
		fi
: '	  elif [ $IHS ]; then
		#backup_directory "IHSBackup" $IHS_HOME
		if [ ! -z "$Node_Name_web" ] && [ ! -z "$Member_Name_web" ] ; then
		  createIHS_no_WAS $Node_Name_web $Member_Name_web
		fi
	  else
		echo "_configApps empty review"
'
	  fi
	  
	  exit 0
	done < $configApps  
}

function _install_c_compiler {
	echoLog "_install_c_compiler"
	#NFS_HOST=10.160.126.16
	#NFS_MOUNT=/opt/CFG
	#/usr/sbin/rmdev -l ipsec_v4
	mkdir -m 777 -p  $NFS_MOUNT
	mount $NFS_HOST:$NFS_MOUNT $NFS_MOUNT
	GOSOFT_XL_CC=/uxadm/shell/software
	mkdir -p $GOSOFT_XL_CC
	cp -p $NFS_MOUNT/Shared/software.tar $GOSOFT_XL_CC
	tar -xvf $GOSOFT_XL_CC/software.tar -C $GOSOFT_XL_CC
	geninstall -I "a -cgNqwXY -J"  -Z   -d $GOSOFT_XL_CC/C_Compile/usr/sys/inst.images -f $PWD/Ccomp.C 2>&1
	export PATH=$PATH:/usr/vac/bin
	rm -rf $GOSOFT_XL_CC/software.tar
}

function _createNodeGroup {
	if [ -f $createNodeGroup ] ; then
		i=1
		
		while read line	   ; do
			test $i -eq 1 && ((i=i+1)) && continue

		  if aix ; then 
			set -A linetokens $line
		  else
			eval 'linetokens=($line)'
		  fi
		  
			groupName=${linetokens[0]}	

			echo "_createNodeGroup"
			echo "groupName@" $groupName
		  
			if [ ! -z "$groupName" ]; then	
			  createNodeGroup $groupName
			fi
				
			((++i))

		done < $createNodeGroup
	fi
}

function _addNodeGroupMember {
	if [ -f $addNodeGroupMember ] ; then
		i=1
		
		while read line	   ; do
			test $i -eq 1 && ((i=i+1)) && continue

		  if aix ; then 
			set -A linetokens $line
		  else
			eval 'linetokens=($line)'
		  fi
		  
			groupName=${linetokens[0]}
			nodeName=${linetokens[1]}
			echo "_addNodeGroupMember"
			echo "groupName@" $groupName
			echo "nodeName@" $nodeName
		  
			if [ ! -z "$groupName" ] && [ ! -z "$nodeName" ]; then	
			  addNodeGroupMember $groupName $nodeName
			fi
				
			((++i))

		done < $addNodeGroupMember
	fi
}

#comma separated value 
IFS=","

_init
#_configApps

if [ "$PROFILE_TYPE" = "dmgr" ]; then
	echo "Configure Nodes..."
	_createNodeGroup
	_addNodeGroupMember	
fi

if [ "$PROFILE_TYPE" = "custom" ]; then
	echo "Changing Node Name..."
	cpallhost=`echo $(hostname -s)Node01`
	renameNode_CPALL $cpallhost
	echo "Wait 30 Sec..."
	sleep 30
fi

_postSetting
echo "Wait 30 Sec..."
sleep 30

echo "Exit configApps.sh"

if [ "$IHS" = "CONFIGURED" ]; then 
	_createIHS_no_WAS
fi

umount $NFS_MOUNT

DEBUG set +x
