BRANCH=`git symbolic-ref --short HEAD`
BUILD =`git describe --always`


all:
	echo 'REACT_APP_BACKEND_URI="http://oasis-backend:5000"'     >  frontend/.env
	echo 'REACT_APP_LOGOUT_TYPE="basic"'                         >> frontend/.env
	echo "REACT_APP_VERSION=\"`git describe --tags --abbrev=0` (`git symbolic-ref --short HEAD`, `git describe --always`)\"" >> frontend/.env
	echo 'REACT_APP_GTM_ID="G-FZQWZ6HET9"'                       >> frontend/.env
	docker build -t oasis-frontend -f Dockerfile-frontend .
	docker save  -o oasis-frontend-$(BRANCH)-$(BUILD).tar oasis-frontend:latest
	docker build -t oasis-backend -f Dockerfile .
	docker save  -o oasis-backend-$(BRANCH)-$(BUILD).tar oasis-backend:latest

clean:
	rm -f oasis-*-*-*.tar
	docker image rm oasis-frontend:latest --force
	docker image rm oasis-backend:latest  --force
