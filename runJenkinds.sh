# docker run -p 8080:8080 -v jenkins_data:/var/jenkins_home jenkins/jenkins:lts
# docker stop jenkins-server
# docker rm -f jenkins-server
# sudo chmod 666 /var/run/docker.sock
# docker run -d \
#   -p 8080:8080 \
#   -v jenkins_data:/var/jenkins_home \
#   -v /var/run/docker.sock:/var/run/docker.sock \
#   --name jenkins-server \
#   jenkins/jenkins:lts

brew services start jenkins-lts
# brew services restart jenkins-lts