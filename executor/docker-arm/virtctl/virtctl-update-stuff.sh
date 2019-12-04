#!/usr/bin/env bash
##############################################################
##
##      Copyright (2019, ) Institute of Software
##          Chinese Academy of Sciences
##             Author: wuheng@otcaix.iscas.ac.cn
##
################################################################

#SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
#cd $SHELL_FOLDER
#rm -rf dist/ build/ vmm.spec
#pyinstaller -F vmm.py -p ./
#chmod +x dist/vmm
#cp -f dist/vmm /usr/bin

# update config file
echo "+++ Processing: update config file"
cp -f /home/kubevmm/bin/config /etc/kubevmm/config.new
rm -f /etc/kubevmm/config
mv -f /etc/kubevmm/config.new /etc/kubevmm/config
echo "--- Done: update config file"
# update VERSION file
echo "+++ Processing: update VERSION file"
cp -f /home/kubevmm/bin/VERSION /etc/kubevmm/VERSION.new
rm -f /etc/kubevmm/VERSION
mv -f /etc/kubevmm/VERSION.new /etc/kubevmm/VERSION
echo "--- Done: update VERSION file"
# update yamls file
echo "+++ Processing: update yamls file"
cp -rf /home/kubevmm/bin/yamls /etc/kubevmm/yamls.new
rm -rf /etc/kubevmm/yamls
mv -f /etc/kubevmm/yamls.new /etc/kubevmm/yamls
echo "--- Done: update yamls file"
# apply kubevirtResource.yaml
if [ -f "/etc/kubevmm/yamls/kubevirtResource.yaml" ];then
	echo "+++ Processing: apply new kubevirtResource.yaml"
	kubectl apply -f /etc/kubevmm/yamls/kubevirtResource.yaml
	echo "--- Done: apply new kubevirtResource.yaml"
else
	echo "*** Warning: apply new kubevirtResource.yaml failed!"
	echo "*** Warning: file /etc/kubevmm/yamls/kubevirtResource.yaml not exists!"
fi
# run virtctl service
echo "Now starting virtctl service..."
python virtctl_in_docker.py