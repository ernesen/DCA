#main ${*:-}

function main
{

clear
echo "###################################################################################"
echo "#################### Please Extend Filesystem / over 4 GB #########################"
echo "###################################################################################"
echo "Press Anykey to Continue ] ? : \c"
	read ANSQ10
	case $ANSQ10 in
	*)

clear	
echo "Please Copy /uxadm/shell/software.tar from GPFS Server (sepas001-003.cpall.co.th) to this host and extract to /uxadm/shell/software"
echo "[if you copy and extract this data and Install C Compiler (/uxadm/shell/software/C_Compile) Press y to Continue Install software monitor OR n to quit] ? : \c"
read ANSQ7
case $ANSQ7 in
y)

	ls -ld /usr/local/etc
 
	if [ $? != 0 ];then      ### Check path /usr/local/etc

	mkdir /usr/local/etc

	fi
	
	while [ true ]
	do
	clear

	clear
	echo "############ Script for Unixadmin setup Monitor Server On Pureapp Only ################"
	echo ""
	echo "  1. Add Crontab root for Monitor System"
	echo "  2. Setup syslog-ng"
	echo "  3. Setup Nagios"
	echo "  4. Setup Zabbix"
	echo "  5. Delete ipsec_v4 device (Choose this choice only one)"
	echo ""
	echo "  Anykey = Quit"
	echo "  Enter Choice : \c"
	read AddRm
	case $AddRm in
	1)
	crontab
	;;

	2)
	syslog
	;;

	3)
	nagios
	;;

	4)
	zabbix
	;;
	
	5)
        ipsec_v4
        ;;

	*)
	break
	;;

	esac
	done



;;

*)

	echo "Please Copy software.tar from GPFS Server (sepas001-003.cpall.co.th) to this host and extract to /uxadm/shell/software And Run This program again [Anykey to Quit] ? : \c"
	read ANSQ8
	case $ANSQ8 in
	*)
	break
	;;

	esac
	
break
;;

esac

	;;

	esac


}

function ipsec_v4
{
/usr/sbin/rmdev -dl ipsec_v4
        lsdev |grep ipsec_v4
        if [ $? != 0 ];then
        echo "ipsec_v4 has been deleted Thank you!!!"
        echo "Press Anykey to Continue ] ? : \c"
        read ipsec
        case $ipsec in
        *)
        break
        ;;
        esac
        else
        echo "ipsec_v4  Not delete Please check lsdev command and call admin"
        echo "Press Anykey to Continue ] ? : \c"
        read ipsec
        case $ipsec in
	*)
        break
        ;;
	esac
	fi

}


function crontab                    
{

cd /uxadm/shell/software/scripts

############################ Monthly Report ####################################
cp -p sm* /uxadm/shell/
cp -p mem* /uxadm/shell/
echo "#---------------------- Technical Unix Support Area -------------------------#" >> /var/spool/cron/crontabs/root
echo "59 23  *  * * /uxadm/shell/sm1.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root                    
echo "59 23  *  * * /uxadm/shell/sm2.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root                  
echo "58 23  * * 0 /uxadm/shell/smvg.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root
echo "0,5,10,15,20,25,30,35,40,45,50,55 * * * * /uxadm/shell/mem_adm.ksh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root   
echo "59 23  *  * *  /uxadm/shell/smmem.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root
echo "30 08 * * * /uxadm/shell/syslog_chkhealth.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root
echo "0,5,10,15,20,25,30,35,40,45,50,55 * * * * /uxadm/shell/chknagios.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root
################################################################################
echo "################Add Crontab Completed#########################"
echo "Please kill process cron and Press Anykey to Continue ] ? : \c"
	read ANSQ18
	case $ANSQ18 in
	*)
	break
	;;
	esac

}



function syslog          
{

########################### Syslog-ng Setup ################################################
ps -ef |grep syslog-ng |grep -v grep

if [ $? = 0 ];then

echo "Process syslog is running So This Program cannot run again please check all config this server [Anykey to Quit] ? : \c"
	read ANSQ6
	case $ANSQ6 in
	*)
	break
	;;

	esac

else

echo "Enter Path directory file setup syslog-ng (ex./uxadm/shell/software/syslog-ng) : \c"
read syslogsetup

ls -ld $syslogsetup

if [ $? = 0 ];then	### Check path syslog setup

cd $syslogsetup

rpm -ivh bash-4.2-4.aix5.1.ppc.rpm
rpm -ivh expat-2.0.1-3.aix5.1.ppc.rpm
rpm -Uvh gettext-0.17-1.aix5.1.ppc.rpm --nodeps
touch /etc/info-dir
rpm -ivh info-4.13a-2.aix5.1.ppc.rpm
rpm -ivh readline-6.2-2.aix5.1.ppc.rpm
rpm -ivh bzip2-1.0.6-1.aix5.1.ppc.rpm
rpm -ivh pcre-8.12-1.aix5.1.ppc.rpm
rpm -Uvh glib2-2.22.5-2.aix5.1.ppc.rpm
rpm -ivh eventlog-0.2.10-1.aix5.1.ppc.rpm
rpm -Uvh openssl-1.0.0d-1.aix5.1.ppc.rpm
rpm -ivh syslog-ng-3.1.4-1.aix5.1.ppc.rpm

cp -p $syslogsetup/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
cp -p $syslogsetup/syslog-ng.add /tmp/syslog-ng.add
odmadd /tmp/syslog-ng.add
logger -p local0.notice "Health status: OK"

genfilt -v 4 -n 3 -a P -s 0.0.0.0 -m 0.0.0.0 -d 0.0.0.0 -M 0.0.0.0 -g Y -c all -o any -p 0 -O eq -P 514 -r B -w B -l N -f Y -i all

genfilt -v 4 -n 3 -a P -s 0.0.0.0 -m 0.0.0.0 -d 0.0.0.0 -M 0.0.0.0 -g Y -c all -o eq -p 514 -O any -P 0 -r B -w B -l N -f Y -i all

mkfilt -u

echo "syslog-ng:2:respawn:/usr/bin/startsrc -s syslogng > /dev/null 2>&1" >> /etc/inittab

	ls -l /uxadm/shell/software/scripts/syslog_chkhealth.sh

	if [ $? = 0 ];then

		cp -p /uxadm/shell/software/scripts/syslog_chkhealth.sh /uxadm/shell/syslog_chkhealth.sh

		echo "Syslog-ng Setup Completed Please check log OK in /var/log/messages [Anykey to Quit] ? : \c"
		read ANSQ17
		case $ANSQ17 in
		*)
		break
		;;

		esac

	else

	echo "Syslog-ng engin Setup Completed Please check log OK in /var/log/messages and Please check script monitor syslog in morning everyday ( /uxadm/shell/syslog_chkhealth.sh )[Anykey to Quit] ? : \c"
	read ANSQ15
	case $ANSQ15 in
	*)
	break
	;;

	esac

	fi

else	### loop check path syslog setup

	echo "Directory syslog-ng setup Not found Please check path $syslogsetup and run this program again [Anykey to Quit] ? : \c"
	read ANSQ14
	case $ANSQ14 in
	*)
	break
	;;

	esac

fi	### loop check path syslog setup

fi

##############################################################################################

}




function nagios
{

######################### Nagios Setup ###############################
more /etc/passwd |grep nagios

if [ $? = 0 ];then	### Check user nagios

echo "User Nagios found in System So This Program cannot run again please check all config this server [Anykey to Quit] ? : \c"
	read ANSQ4
	case $ANSQ4 in
	*)
	break
	;;

	esac

else		### Loop check user nagios

echo "Enter Path directory file setup nagios (ex./uxadm/shell/software/nrpe-2.12) : \c"
read nagiossetup

ls -ld $nagiossetup

if [ $? = 0 ];then	### Check path nagios setup

mkgroup nagios
useradd -md /home/nagios -g nagios nagios
passwd nagios

cd $nagiossetup
#./configure --enable-command-args --disable-ssl
$nagiossetup/configure --enable-command-args --disable-ssl
make all
make install

mkdir -p /usr/local/nagios/etc
cp -p $nagiossetup/sample-config/nrpe.cfg /usr/local/nagios/etc/

echo "nrpe     5666/tcp # NRPE" >> /etc/services

cp -p /uxadm/shell/software/scripts/chknagios* /uxadm/shell/



########################################################################################################################

	echo "Enter Path directory file setup nagios Plugin (ex./uxadm/shell/software/nagios-plugins-1.4.15) : \c"
	read nagiosplugin

	ls -ld $nagiosplugin

	if [ $? = 0 ];then 	### Check path nagios plugin

cd $nagiosplugin
#./configure --without-ssl
$nagiosplugin/configure --without-ssl
make
make install

ls -l $nagiossetup/nrpe.cfg

	if [ $? = 0 ];then

		cp -p $nagiossetup/nrpe.cfg /usr/local/nagios/etc/nrpe.cfg

		genfilt -v 4 -n 3 -a P -s 0.0.0.0 -m 0.0.0.0 -d 0.0.0.0 -M 0.0.0.0 -g Y -c all -o any -p 0 -O eq -P 5666 -r B -w B -l N -f Y -i all

		genfilt -v 4 -n 3 -a P -s 0.0.0.0 -m 0.0.0.0 -d 0.0.0.0 -M 0.0.0.0 -g Y -c all -o eq -p 5666 -O any -P 0 -r B -w B -l N -f Y -i all

		mkfilt -u

	else

	echo "Please check file config for copy to /etc/local/nagios/etc/nrpe.cfg ( $nagiossetup/nrpe.cfg )"
	
	fi

echo "Install Service Nagios Completed Please edit /usr/local/nagios/etc/nrpe.cfg on this host and After Config On nagios server next step restart nagios process on client [Anykey to Quit] ? : \c"

	read ANSQ5
	case $ANSQ5 in
	*)
	break
	;;

	esac

	else	### loop check path nagios plugin
	
	echo "Nagios engine setup completed But Directory nagios Plugin Not found Please check path $nagiosplugin and Install plugin manual [Anykey to Quit] ? : \c"
	read ANSQ13
	case $ANSQ13 in
	*)
	break
	;;

	esac

	fi	### loop check path nagios plugin


else	### loop check path nagios setup

	echo "Directory nagios setup Not found Please check path $nagiossetup and path plugin and run this program again [Anykey to Quit] ? : \c"
	read ANSQ12
	case $ANSQ12 in
	*)
	break
	;;

	esac

fi	### loop check path nagios setup
	
fi	### Loop check user nagios

#######################################################################

}




function zabbix
{

######################## Zabbix Config ############################
echo "Enter Path directory file setup zabbix (ex./uxadm/shell/software/zabbix-2.4.2) : \c"
read zabbixsetup

ls -ld $zabbixsetup

if [ $? = 0 ];then

cd $zabbixsetup

more /etc/passwd |grep zabbix

if [ $? = 0 ];then

echo "This Program cannot run again please check all config this server [Anykey to Quit] ? : \c"
	read ANSQ3
	case $ANSQ3 in
	*)
	break
	;;

	esac

else

mkgroup zabbix
useradd -md /home/zabbix -g zabbix zabbix
#passwd zabbix ### password_zabbix
./configure --enable-agent
make install
chown zabbix:zabbix /usr/local/*/zabbix*
echo "zabbix-agent    10050/tcp  Zabbix Agent" >> /etc/services
echo "zabbix-agent    10050/udp  Zabbix Agent" >> /etc/services
echo "zabbix-trapper  10051/tcp  Zabbix Trapper" >> /etc/services
echo "zabbix-trapper  10051/udp  Zabbix Trapper" >> /etc/services

echo "10.153.1.150    outrpsv1 #### zabbix server" >> /etc/hosts

echo "zabbix:2:once:/usr/local/sbin/zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf >/dev/console 2>&1" >> /etc/inittab

cp -p $zabbixsetup/zabbix_agentd.conf /usr/local/etc/zabbix_agentd.conf

echo "Please check your edit host on file config /usr/local/etc/zabbix_agentd.conf Befor start process [Press y to Continue start process ] ? : \c"
read ANSQ
case $ANSQ in
y)
	/usr/local/sbin/zabbix_agentd    #### Start zabbix process

	ps -ef |grep zabbix

	if [ $? = 0 ];then

	echo "You Config zabbix client Completed & Please config your server on web zabbix server [Anykey to Quit] ? : \c"
	read ANSQ1
	case $ANSQ1 in
	*)
	break
	;;

	esac

	else

	echo "Service not start!!! Please check all config file /usr/local/etc/zabbix_agentd & run command /usr/local/sbin/zabbix_agentd to start process [Anykey to Quit] ? : \c"
	read ANSQ9
	case $ANSQ9 in
	*)
	break
	;;

	esac

	fi
;;

*)

	echo "Please check config file /usr/local/etc/zabbix_agentd & run command /usr/local/sbin/zabbix_agentd to start process [Anykey to Quit] ? : \c"
	read ANSQ2
	case $ANSQ2 in
	*)
	break
	;;

	esac
	
#break
;;

esac

fi     

	else

	echo "Directory zabbix setup Not found [Anykey to Quit] ? : \c"
	read ANSQ11
	case $ANSQ11 in
	*)
	break
	;;

	esac

fi

}
main ${*:-}




