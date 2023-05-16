FROM python:3.10-slim
WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENV RUN_IN_DOCKER Yes
RUN echo 'PS1="\h:\w$ "' >> /etc/bash.bashrc
#RUN echo "PS1='\[\e]0;\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '" >> /etc/bash.bashrc
CMD ["python", "app.py"]



