#use this file to build Jenkins with Docker to avoid issue Docker-in-Docker with python script in Jenkins pipeline


FROM jenkins/jenkins:lts
USER root
# Install Docker CLI inside the image
RUN apt-get update && apt-get install -y docker.io
# Switch back to the jenkins user for security
USER jenkins



#docker build -t my-jenkins-with-docker .



# Remove the old one first
# docker rm -f jenkins-server

# Start the new one
# docker run -d \
#   -p 8080:8080 \
#   -v jenkins_data:/var/jenkins_home \
#   -v /var/run/docker.sock:/var/run/docker.sock \
#   --name jenkins-server \
#   my-jenkins-with-docker