BUILD_DIR=../build

all:
	mkdir -p ${BUILD_DIR}
	rm -Rf   ${BUILD_DIR}/*
	cp Dockerfile        ${BUILD_DIR}/
	cp -R ../backend     ${BUILD_DIR}/
	cp -R ../backend-app ${BUILD_DIR}/
	cd ${BUILD_DIR} && docker build -t oasis-backend -f Dockerfile .
