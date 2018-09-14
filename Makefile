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
	echo "blacklist brcmfmac" > /etc/wanem/tpl/raspi-blacklist-24.conf
	echo "blacklist brcmutil" >> /etc/wanem/tpl/raspi-blacklist-24.conf
	echo "blacklist rtl8812au" > /etc/wanem/tpl/raspi-blacklist-5.conf
	sudo cp /etc/wanem/tpl/raspi-blacklist-5.conf /etc/modprobe.d/raspi-blacklist.conf
	sudo cp misc/iptables/iptables.ipv4.nat.type2 /etc/
	sudo cp misc/iptables/iptables.ipv4.nat.type3 /etc/
	sudo cp /etc/iptables.ipv4.nat.type2 /etc/iptables.ipv4.nat

#########################################################################################

YAPF           ?= yapf
PYTHON_SCRIPTS ?= ${shell ls *.py}

format:
	yapf -i ${PYTHON_SCRIPTS}
