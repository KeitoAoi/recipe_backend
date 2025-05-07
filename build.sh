set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate 
python manage.py load_recipes --path ./backend/recipes_sample500.csv  