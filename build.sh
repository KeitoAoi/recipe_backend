set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate 
python manage.py load_recipes --path ./backend/recipes_sample500.csv  
python manage.py seed_predefined_catalogs
python manage.py populate_search_vector