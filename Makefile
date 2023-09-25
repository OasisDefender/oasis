BRANCH=`git symbolic-ref --short HEAD`
BUILD =`git describe --always`

all:
	docker build -t oasis-frontend -f Dockerfile-frontend .
	docker save  -o oasis-frontend-$(BRANCH)-$(BUILD).tar oasis-frontend:latest
	docker build -t oasis-backend -f Dockerfile .
	docker save  -o oasis-backend-$(BRANCH)-$(BUILD).tar oasis-backend:latest

clean:
	rm -f oasis-*-*-*.tar
	docker image rm oasis-frontend:latest --force
	docker image rm oasis-backend:latest  --force
