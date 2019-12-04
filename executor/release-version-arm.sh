#!/usr/bin/env bash

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
cd $SHELL_FOLDER

##############################init###############################################
if [ ! -n "$1" ] ;then
    echo "error: please input a release version number!"
    echo "Usage $0 <version number>"
    exit 1
else
    if [[ "$1" =~ ^[A-Za-z0-9.-]*$ ]] ;then
        echo -e "\033[3;30;47m*** Build a new release version: \033[5;36;47m($1)\033[0m)"
        echo -e "Institute of Software, Chinese Academy of Sciences"
        echo -e "        wuyuewen@otcaix.iscas.ac.cn"
        echo -e "              Copyright (2019)\n"
    else
        echo "error: wrong syntax in release version number, support chars=[A-Za-z0-9.]"
        exit 1
    fi
fi

VERSION=$1

echo -e "\033[3;30;47m*** Pull latest version from Github.\033[0m"
git pull origin arm8
if [ $? -ne 0 ]; then
    echo "    Failed to pull latest version from Github!"
    exit 1
else
    echo "    Success pull latest version."
fi

##############################patch stuff#########################################
SHELL_FOLDER=$(dirname $(readlink -f "$0"))
cd ${SHELL_FOLDER}
if [ ! -d "./dist" ]; then
	mkdir ./dist
fi
cp -f config ./dist
cp -rf ../yamls ./dist
echo ${VERSION} > ./VERSION

cp -rf ./dist/yamls/ ./VERSION ./dist/config docker/virtctl
if [ $? -ne 0 ]; then
    echo "    Failed to copy stuff to docker/virtctl!"
    exit 1
else
    echo "    Success copy stuff to docker/virtctl."
fi

##############################patch image#########################################

# step 1 copy file
if [ ! -d "./docker/virtctl/utils" ]; then
	mkdir ./docker-arm/virtctl/utils
fi
if [ ! -d "./docker/virtlet/utils" ]; then
	mkdir ./docker-arm/virtlet/utils
fi
cp -rf utils/*.py docker-arm/virtctl/utils/
cp -rf utils/*.py docker-arm/virtlet/utils/
cp -rf config arraylist.cfg virtctl_in_docker.py invoker.py virtctl.py docker-arm/virtctl
cp -rf config arraylist.cfg virtlet_in_docker.py host_cycler.py libvirt_event_handler_for_4_0.py libvirt_event_handler.py os_event_handler.py virtlet.py monitor.py docker-arm/virtlet

#step 2 docker build
cd docker-arm
#docker build base -t registry.cn-hangzhou.aliyuncs.com/cloudplus-lab/kubeext-base:v1.5.0-arm8
docker build virtlet -t registry.cn-hangzhou.aliyuncs.com/cloudplus-lab/kubeext-let:${VERSION}
docker build virtctl -t registry.cn-hangzhou.aliyuncs.com/cloudplus-lab/kubeext-ctl:${VERSION}

#step 3 docker push
#echo -e "\033[3;30;47m*** Login docker image repository in aliyun.\033[0m"
#echo "Username: bigtree0613@126.com"
#docker login --username=bigtree0613@126.com registry.cn-hangzhou.aliyuncs.com
#if [ $? -ne 0 ]; then
#    echo "    Failed to login aliyun repository!"
#    exit 1
#else
#    echo "    Success login...Pushing images!"
#fi
#docker push registry.cn-hangzhou.aliyuncs.com/cloudplus-lab/kubeext-base:v1.5.0-arm8
#docker push registry.cn-hangzhou.aliyuncs.com/cloudplus-lab/kubeext-ctl:${VERSION}
#docker push registry.cn-hangzhou.aliyuncs.com/cloudplus-lab/kubeext-let:${VERSION}

###############################patch version to SPECS/kubevmm.spec######################################################
#echo -e "\033[3;30;47m*** Patch release version number to SPECS/kubevmm.spec\033[0m"
#cd ..
#sed "4s/.*/%define         _verstr      ${VERSION}/" SPECS/kubevmm.spec > SPECS/kubevmm.spec.new
#mv SPECS/kubevmm.spec.new SPECS/kubevmm.spec
#if [ $? -ne 0 ]; then
#    echo "    Failed to patch version number to SPECS/kubevmm.spec!"
#    exit 1
#else
#    echo "    Success patch version number to SPECS/kubevmm.spec."
#fi

#echo -e "\033[3;30;47m*** Push new SPECS/kubevmm.spec to Github.\033[0m"
#git add ./SPECS/kubevmm.spec
#git add ./kubeovn-adm
#git commit -m "new release version ${VERSION}"
#git push
#if [ $? -ne 0 ]; then
#    echo "    Failed to push SPECS/kubevmm.spec to Github!"
#    exit 1
#else
#    echo "    Success push SPECS/kubevmm.spec to Github."
#fi

