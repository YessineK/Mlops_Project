FROM nginx:alpine

# Copier les rapports HTML dans le dossier Nginx
COPY *.html /usr/share/nginx/html/
COPY *.json /usr/share/nginx/html/

# Exposer le port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]