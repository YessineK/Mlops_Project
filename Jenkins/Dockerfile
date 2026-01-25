FROM jenkins/jenkins:lts

USER root

# Install lsb-release
RUN apt-get update && apt-get install -y lsb-release

# Install Python3 and pip
RUN apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean

# Install Docker CLI and Docker Compose
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    apt-get clean

USER jenkins

# Install Jenkins plugins
RUN jenkins-plugin-cli --plugins git workflow-aggregator docker-workflow credentials-binding