DEPLOY_TARGET = 192.168.31.67 

default:

prop:
	mkdir -p /etc/wanem/tpl
	echo "0" > /etc/wanem/apchannel.prop
	echo "0" > /etc/wanem/apmode.prop
	echo "0" > /etc/wanem/wanemmode.prop
	echo "0" > /etc/wanem/tpl/0.prop
	echo "1" > /etc/wanem/tpl/1.prop
	echo "2" > /etc/wanem/tpl/2.prop
	echo "3" > /etc/wanem/tpl/3.prop
	sudo cp misc/iptables/iptables.ipv4.nat.type2 /etc/
	sudo cp misc/iptables/iptables.ipv4.nat.type3 /etc/
	sudo cp /etc/iptables.ipv4.nat.type2 /etc/iptables.ipv4.nat

#########################################################################################

YAPF           ?= yapf
PYTHON_SCRIPTS ?= ${shell ls *.py}

format:
	yapf -i ${PYTHON_SCRIPTS}

deploy:
	rsync -avz ./ pi@192.168.31.67:EM-uNetPi/
