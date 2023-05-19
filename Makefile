export SVN_REV=`svn info | grep Revision | sed 's/^.*: //g'`


all:
	docker build -t oasis .
	docker save -o oasis-$(SVN_REV).tar oasis:latest
