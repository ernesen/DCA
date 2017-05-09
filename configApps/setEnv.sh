
echo "version 2.0.0"
echo "date 20160105"
echo "create by Theerawut Dejphadung"
echo "modify by Theeradet Khawprasert"

###################### Set ENV ###############################

#rmdev -l ipsec_v4
#echo "rmsec:2:once:rmdev -l ipsec_v4 2>&1" >> /etc/inittab
######## Remove Default Lang
sed 's/^export LANG\=EN_US\.UTF\-8$/#export LANG=EN_US.UTF-8/' /etc/profile > /tmp/profile ; cat /tmp/profile > /etc/profile
sed 's/^export LC_ALL\=EN_US\.UTF\-8$/#export LC_ALL=EN_US.UTF-8/' /etc/profile > /tmp/profile ; cat /tmp/profile > /etc/profile
sed 's/^LC_ALL\=EN_US.UTF\-8$/#LC_ALL=EN_US.UTF-8/' /etc/environment > /tmp/environment ; cat /tmp/environment > /etc/environment
sed 's/^export LANG\=EN_US\.UTF\-8$/#export LANG=EN_US.UTF-8/' /home/virtuser/.profile > /tmp/virtuser.profile ; cat /tmp/virtuser.profile > /home/virtuser/.profile
sed 's/^export LC_ALL\=EN_US\.UTF\-8$/#export LC_ALL=EN_US.UTF-8/' /home/virtuser/.profile > /tmp/virtuser.profile ; cat /tmp/virtuser.profile > /home/virtuser/.profile
sed 's/^export LANG\=EN_US\.UTF\-8$/#export LANG=EN_US.UTF-8/' /home/wasapp/.profile > /tmp/wasapp.profile ; cat /tmp/wasapp.profile > /home/wasapp/.profile
sed 's/^export LC_ALL\=EN_US\.UTF\-8$/#export LC_ALL=EN_US.UTF-8/' /home/wasapp/.profile > /tmp/wasapp.profile ; cat /tmp/wasapp.profile > /home/wasapp/.profile
######## Append Config Default User
echo "" >> /etc/profile
echo "set -o vi" >> /etc/profile
echo "host=\$(hostname)" >> /etc/profile
echo 'PS1='\''[$LOGNAME@$host $PWD ]#'\''' >> /etc/profile
chlang en_US
echo "export LANG=en_US" >> /etc/profile

#echo "PATH=/usr/vac/bin:\$PATH" >> /etc/environment
#echo "export PATH" >> /etc/environment
 
##############################################################
 
 
###################### Set Host ############################## 
 
echo "" >> /etc/hosts
#echo "##########################################" >> /etc/hosts
#echo "#------ Mail Server ----" >> /etc/hosts
#echo "151.1.104.88  mailhost gosoft.co.th" >> /etc/hosts
#echo "##########################################" >> /etc/hosts
#echo "" >> /etc/hosts
#echo "#--------- NTP Server ---------" >> /etc/hosts
#echo "#Sync Time Server" >> /etc/hosts
#echo "10.151.19.7     TARDNS  ns1.7eleven.co.th" >> /etc/hosts
#echo "10.182.255.7    SBRDNS  ns2.7eleven.co.th" >> /etc/hosts
#echo "##########################################" >> /etc/hosts
#echo "" >> /etc/hosts
#echo "################ Zabbix Server ##############" >> /etc/hosts
#echo "10.153.1.150    outrpsv1" >> /etc/hosts
#echo "##########################################" >> /etc/hosts
#echo "" >> /etc/hosts
#echo "10.153.1.183    gooutap1  ### nagios server" >> /etc/hosts
#echo "##########################################" >> /etc/hosts
#echo "#Performance Report" >> /etc/hosts
#echo "10.151.18.19    technuke" >> /etc/hosts
#echo "##########################################" >> /etc/hosts
echo "#--------- backup server ---------" >> /etc/hosts
#echo "151.1.116.15    cpsebck1" >> /etc/hosts
#echo "10.151.22.219   sestbap1" >> /etc/hosts
echo "10.9.105.11     sestbap18.7eleven.cp.co.th" >> /etc/hosts
echo "10.151.22.223   sestbap2" >> /etc/hosts
#echo "10.151.22.220   sestbapb" >> /etc/hosts
echo "##########################################" >> /etc/hosts
 
##############################################################
 
#################### Set NTP #################################
 
stopsrc -s xntpd
echo "server ns1.7eleven.co.th" >> /etc/ntp.conf
echo "server ns2.7eleven.co.th" >> /etc/ntp.conf
startsrc -s xntpd
 
##############################################################
################### Set Sendmail Config ###########################
cp -p /etc/mail/sendmail.cf  /etc/mail/sendmail.cf_old
osLevel=$(oslevel)
if [ "$osLevel" == '7.1.0.0' ] ;  then
    sed '105s/DS/DStarmg.cpall.co.th/' /etc/mail/sendmail.cf_old > /etc/mail/sendmail.cf
elif [ "$osLevel" == '6.1.0.0' ] ;  then
    sed '96s/DS/DStarmg.cpall.co.th/' /etc/mail/sendmail.cf_old > /etc/mail/sendmail.cf
fi
 
#################### Set Uxadm ###############################
 
mkdir /uxadm
mkdir /uxadm/shell
mkdir /uxadm/shell/log_nmon
touch /uxadm/shell/nmon.sh
chmod 755 /uxadm/shell/nmon.sh
 
#############################################################
 
#################### Nmon Script ############################
echo "LOGDIR=/uxadm/shell/log_nmon" >> /uxadm/shell/nmon.sh
echo "NMONPATH=/usr/bin/nmon" >> /uxadm/shell/nmon.sh
 
 
echo "mkdir \$LOGDIR 1>/dev/null 2>&1" >> /uxadm/shell/nmon.sh
echo "mkdir \$LOGDIR/60min 1>/dev/null 2>&1" >> /uxadm/shell/nmon.sh
echo "mkdir \$LOGDIR/5min 1>/dev/null 2>&1" >> /uxadm/shell/nmon.sh
 
echo "cd \$LOGDIR/60min" >> /uxadm/shell/nmon.sh
echo "\$NMONPATH -fdt -s 3600 -c 24 &  # 60 Minutes & 24 times" >> /uxadm/shell/nmon.sh
echo "cd \$LOGDIR/5min" >> /uxadm/shell/nmon.sh
echo "\$NMONPATH -fdtT -s 300 -c 288  & # 5 Minutes & 288 times" >> /uxadm/shell/nmon.sh
 
echo "find \$LOGDIR -name \"*.nmon\" -mtime +2 |xargs -n1 compress 1>/dev/null 2>&1" >> /uxadm/shell/nmon.sh
 
echo "find \$LOGDIR -name \"*.nmon.Z\" -mtime +35 |xargs -n1 rm -f 1>/dev/null 2>&1" >> /uxadm/shell/nmon.sh
####################################################################
 
#################### Set Crontab ###################################
echo "0 0 * * * /uxadm/shell/nmon.sh" >> /var/spool/cron/crontabs/root
echo "05,25,45  *  *  * 0-6 /usr/lib/sa/sa1" >> /var/spool/cron/crontabs/adm
echo "00,20,40  *  *  * 0-6 /usr/lib/sa/sa1" >> /var/spool/cron/crontabs/adm
echo "15,35,55  *  *  * 0-6 /usr/lib/sa/sa1" >> /var/spool/cron/crontabs/adm
echo "10,30,50  *  *  * 0-6 /usr/lib/sa/sa1" >> /var/spool/cron/crontabs/adm
echo "56       23  *  * 0-6 /usr/lib/sa/sa2 -s 0:05 -e 23:55 -i 300 -A" >> /var/spool/cron/crontabs/adm
echo "#==================================================================" >> /var/spool/cron/crontabs/adm
######################################################################
echo "DATE=\`date +%d\`" > /uxadm/shell/sa.sh
echo "HISDATE=\`date +%y%m%d\`" >> /uxadm/shell/sa.sh
echo "DFILE=/var/adm/sa/sa\$DATE" >> /uxadm/shell/sa.sh
echo "INFILE=/tmp/saru" >> /uxadm/shell/sa.sh
echo "OUTDATE=\`date +%Y-%m-%d\`" >> /uxadm/shell/sa.sh
echo "WEEKDAY=\`date +%w\`" >> /uxadm/shell/sa.sh
echo "WEEK=\`date +%V\`" >> /uxadm/shell/sa.sh
echo "MONTH=\`date +%m\`" >> /uxadm/shell/sa.sh
echo "YEAR=\`date +%Y\`" >> /uxadm/shell/sa.sh
echo "SERVER_NAME=\`hostname\`" >> /uxadm/shell/sa.sh
echo "/usr/sbin/sar -qf /var/adm/sa/sa\$DATE > /tmp/sarq" >> /uxadm/shell/sa.sh
echo "/usr/sbin/sar -uf /var/adm/sa/sa\$DATE > /tmp/saru" >> /uxadm/shell/sa.sh

chmod 775 /uxadm/shell/sa.sh

echo "57 23  *  * * /uxadm/shell/sa.sh > /dev/null 2>&1" >> /var/spool/cron/crontabs/root


####################### Set Services ##################################
echo "omni             5555/tcp    # DATA-PROTECTOR" >> /etc/services
########################################################################
 
####################### Set Inittab ###################################################
echo "ntp:2:wait:/usr/bin/startsrc -s xntpd" >> /etc/inittab
#######################################################################################

####################### Set number of process default 128 #############################################
chdev -l sys0 -a maxuproc=1024
########################################################################################

######################## Refresh Cron Daemon #########################
pid=$(ps -ef |grep cron |grep -v grep |awk '{print$2}')
kill -9 $pid
######################################################################

######################## Reconfig resolv.conf ###########################
mv /etc/resolv.conf  /etc/resolv.conf_joe
echo "search counterservice.co.th gosoft.co.th cpall.co.th cpretailink.co.th dynamic-logistics.com 7catalog.com cpram.co.th 7eleven.cp.co.th" > /etc/resolv.conf
echo "nameserver	10.151.18.47" >> /etc/resolv.conf
echo "nameserver	10.151.18.12" >> /etc/resolv.conf
echo "nameserver	10.182.255.14" >> /etc/resolv.conf
#########################################################################
