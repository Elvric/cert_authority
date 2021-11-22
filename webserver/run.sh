cp /webserver/nginx/nginx.conf /etc/nginx/sites-available/default
#npm run build --prefix /webserver/frontend
cp -r /webserver/frontend/build/* /var/www/html/
service nginx restart