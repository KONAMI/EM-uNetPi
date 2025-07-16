##################################################            

.SUFFIXES : .raw .bmp .jpg

##################################################

TIMESTAMP        ?= $(shell date +%Y_%m_%d_%H_%M_%S)
TARGET_FB        ?= "/dev/fb0"
RAW_FORMAT       ?= "rgb565"
RAW_SIZE         ?= "480x320"
FILENAME_BASE    ?= ${shell cat key.txt}
SCREENSHOT_DIR   ?= "/home/pi/EM-uNetPi/screenshots"
SCREENSHOT_OWNER ?= pi

##################################################

default:

key:
	echo ${TIMESTAMP} > key.txt

raw:
	cat ${TARGET_FB} > ${FILENAME_BASE}.raw

.raw.bmp: 
	ffmpeg -vcodec rawvideo -f rawvideo -pix_fmt ${RAW_FORMAT} -s ${RAW_SIZE} -i $< -f image2 -vcodec bmp $@

.bmp.jpg:
	convert $< $@ 

capture: key
	${MAKE} raw
	${MAKE} ${FILENAME_BASE}.bmp
	${MAKE} ${FILENAME_BASE}.jpg
	mv ${FILENAME_BASE}.jpg ${SCREENSHOT_DIR}/
	chown ${SCREENSHOT_OWNER} ${SCREENSHOT_DIR}/${FILENAME_BASE}.jpg
	chgrp ${SCREENSHOT_OWNER} ${SCREENSHOT_DIR}/${FILENAME_BASE}.jpg
	${MAKE} cleanup

cleanup:
	-rm *.raw 
	-rm *.bmp
	-rm *.txt
	-rm *.jpg

