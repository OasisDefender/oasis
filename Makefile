export REV=`git describe --always`


all:
	docker build -t oasis .
	docker save -o oasis-$(REV).tar oasis:latest
