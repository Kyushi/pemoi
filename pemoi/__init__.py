"""Init file for package. Create flask app."""
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
# Get static path from config
app.static_url_path=app.config.get('STATIC_FOLDER')

import pemoi.pmoi_auth
import pemoi.pmoi_cat
import pemoi.fboauth
import pemoi.githuboauth
import pemoi.googleoauth
import pemoi.pmoi_index
import pemoi.pmoi_item
import pemoi.pmoi_user
import pemoi.pmoi_helpers

# Make sure that admin and category 0 exist when starting the app.
admin = pemoi.pmoi_helpers.get_or_create_admin()
cat_zero = pemoi.pmoi_helpers.get_or_create_cat_zero()

@app.context_processor
def categories_for_menu():
    return dict(categories=pemoi.pmoi_cat.get_categories())
