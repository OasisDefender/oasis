all:
	echo 'REACT_APP_BACKEND_URI="http://oasis-backend:5000"'     >  .env
	echo 'REACT_APP_AUTH_TYPE="BASIC"'                           >> .env
	echo "REACT_APP_VERSION=\"`git describe --tags --abbrev=0` (`git symbolic-ref --short HEAD`, `git describe --always`)\"" >> .env
	echo 'REACT_APP_GTM_ID="G-FZQWZ6HET9"'                       >> .env
	docker build -t oasis-frontend -f Dockerfile .
