upstream keen_app {
	server 127.0.0.1:8000;
}

server {
        listen 80 default_server; 
	server_name .keensmb.com;

	client_max_body_size 32M;

	include /var/apps/keensmb.com/keen/conf/nginx/keensmb.com.static;

	location = / {
		return 301 https://$host/;
	}

	location /api/ {
		return 301 https://$host$request_uri;
	}

	location /admin/ {
		return 301 https://$host$request_uri;
	}
	
	location / {
		uwsgi_pass keen_app;
		include uwsgi_params;
		uwsgi_param UWSGI_SCHEME $scheme;
	}
}

server {
	listen 443;
	server_name .keensmb.com;

	ssl on;
	ssl_certificate /var/apps/keensmb.com/cert/keensmb+gd-ca.crt;
	ssl_certificate_key /var/apps/keensmb.com/cert/keensmb.key;

	client_max_body_size 32M;

	include /var/apps/keensmb.com/keen/conf/nginx/keensmb.com.static;
	
	location / {
		uwsgi_pass keen_app;
		include uwsgi_params;
		uwsgi_param UWSGI_SCHEME $scheme;
	}
}
