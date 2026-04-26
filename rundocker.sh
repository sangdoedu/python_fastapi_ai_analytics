# docker run -p 8080:8080 -v jenkins_data:/var/jenkins_home jenkins/jenkins:lts
docker run -d \
  -p 8080:8080 \
  -v jenkins_data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins-server \
  jenkins/jenkins:lts