upstream keen_app {
	server 127.0.0.1:8000;
}

server {
        listen 80 default_server; 
	server_name .keensmb.com;
	client_max_body_size 32M;

	location = /favicon.ico {
		alias /var/apps/keensmb.com/keen/shared_static/favicon.ico;
	}

	location = /favicon.ico {
		alias /var/apps/keensmb.com/keen/shared_static/favicon.ico;
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
