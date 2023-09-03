#!/bin/bash

# this file shall be copied into workdir during building the docker image

VERBOSE=0
PKGFILE="/include.pkg"
USERFILE="/user.dat"
PIP3FILE="/include.pip3.pkg"

verbose(){
    [ $VERBOSE -eq 1 ] && echo "$1"
}

fexist_or_exit(){
    if [ ! -f "$1" ]; then
    verbose "Error! File $1 is not exist." 
    exit 1; 
    fi
}

create_user(){
    local id=$1
    local pw=$2
    useradd -rm -d /home/$id -s $SHELL -g root -G sudo $id
    local tmpfile=`mktemp`
    echo "$id:$pw" > $tmpfile
    chpasswd -c SHA512 < $tmpfile && rm -f $tmpfile
    if [ "$id" == "root" ]; then
       prefix="/root"
    else
       prefix="/home/${user[0]}"
    fi

    mkdir -p $prefix/.ssh
    mkdir -p $prefix/.vscode 
    mkdir -p $prefix/.vscode-server
    chown $id $prefix/.ssh
    chown $id $prefix/.vscode
    chown $id $prefix/.vscode-server
}



while getopts "v" opt
do
    case $opt in 
        "v")
            VERBOSE=1
            ;;
        ?)
            echo "$0 [-v]"
            exit 1
            ;;
    esac
done


cat $USERFILE | while read -r line; do
    verbose "parsing $USERFILE where $line"
    user=($(echo $line|tr ":" "\n"))
    if [ ${#user[@]} -ne 2 ]; then 
        verbose "Warnning! Syntax error: $line"
    else
        create_user ${user[0]} ${user[1]}
        if [ "${user[0]}" == "root" ]; then
            prefix="/root"
        else
            prefix="/home/${user[0]}"
        fi
        if [ -f "/ssh_key_busydocker.pub" ]; then 
          cat /ssh_key_busydocker.pub >> $prefix/.ssh/authorized_keys
        fi
    fi
done

cat $PKGFILE | uniq | while read line; do 
    DEBIAN_FRONTEND=noninteractive apt-get install -yq $line
    [ !"$?" = "0" ] && echo "apt-get install $line Fail"
done

#allow remote ssh login
sed -i "s/#Port.*/Port 22/" /etc/ssh/sshd_config && \
sed -i "s/#X11UseLocalhost.*/X11UseLocalhost no/" /etc/ssh/sshd_config && \
sed -i "s/#PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config && \
sed -i "s/#PasswordAuthentication.*/PasswordAuthentication yes/" /etc/ssh/sshd_config
sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

echo "PATH=\"/opt/conda/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"" >/etc/environment
echo "NVIDIA_REQUIRE_CUDA=cuda>=11.0 brand=tesla,driver>=418,driver<419 brand=tesla,driver>=440,driver<441 brand=tesla,driver>=450,driver<451" >> /etc/environment
echo "NVIDIA_DRIVER_CAPABILITIES=compute,utility" >> /etc/environment
echo "CUDA_VERSION=11.0.3" >> /etc/environment
echo "LIBRARY_PATH=/usr/local/cuda/lib64/stubs" >> /etc/environment
echo "NCCL_VERSION=2.7.8" >> /etc/environment
echo "NVIDIA_VISIBLE_DEVICES=all" >> /etc/environment


mkdir /var/run/sshd

