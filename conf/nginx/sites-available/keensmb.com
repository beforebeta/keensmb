upstream keen_app {
	server 127.0.0.1:8000;
}

server {
        listen 80 default_server; 
	server_name .keensmb.com;

	location = /robots.txt {
		alias /var/apps/keensmb.com/keen/conf/robots.txt;
	}

	location = /favicon.ico {
		alias /var/apps/keensmb.com/keen/shared_static/favicon.ico;
	}

	rewrite ^ https://$host$request_uri permanent;
}

server {
	listen 443;
	server_name .keensmb.com;

	ssl on;
	ssl_certificate /var/apps/keensmb.com/cert/keensmb+gd-ca.crt;
	ssl_certificate_key /var/apps/keensmb.com/cert/keensmb.key;

	client_max_body_size 32M;

	location = /robots.txt {
		alias /var/apps/keensmb.com/keen/conf/robots.txt;
	}

	location = /favicon.ico {
		alias /var/apps/keensmb.com/keen/shared_static/favicon.ico;
	}

	rewrite ^/blog$ /blog/ permanent;

	location /blog/ {
		root /var/apps/keensmb.com/;
		index index.php index.html index.htm;
		try_files $uri $uri/ /blog/index.php?$args;

		location ~* \.(html|htm|css|jpeg|jpg|gif|png)$ {
			# serve static files 
			log_not_found off;
		}

		location ~ \.php$ {
			fastcgi_pass 127.0.0.1:9000;
			include fastcgi_params;
		}
	}

	location /static/ { 
        	alias /var/apps/keensmb.com/keen/static/;
		autoindex off;
        	expires max;
		gzip on;
		gzip_buffers 16 8k;
		gzip_comp_level 4;
		gzip_http_version 1.0;
		gzip_min_length 1280;
		gzip_types text/css application/x-javascript text/javascript image/x-icon image/jpeg;
		gzip_vary on;
		gzip_disable "msi6";
    	}

	location /media/ { 
        	alias /var/apps/keensmb.com/keen/media/;
		autoindex off;
        	expires max;
		gzip on;
		gzip_buffers 16 8k;
		gzip_comp_level 4;
		gzip_http_version 1.0;
		gzip_min_length 1280;
		gzip_types text/css application/x-javascript text/javascript image/x-icon image/jpeg;
		gzip_vary on;
		gzip_disable "msi6";
    	}
	
	location / {
		uwsgi_pass keen_app;
		include uwsgi_params;
	}
}
