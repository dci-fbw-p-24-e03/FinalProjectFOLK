web: apt-get update && apt-get install -y nginx && cp /app/.do/nginx.conf /etc/nginx/sites-enabled/default && service nginx restart && daphne -b 0.0.0.0 -p 8080 AI_quiz.asgi:application --http-timeout 3600