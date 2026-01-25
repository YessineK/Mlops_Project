FROM nginx:alpine

# Supprimer la config par défaut
RUN rm -rf /usr/share/nginx/html/*

# Copier les rapports
COPY . /usr/share/nginx/html/

# Permissions propres
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80
