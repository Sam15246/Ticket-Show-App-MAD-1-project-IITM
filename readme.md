# Local Setup
- Run `local_setup.sh`.


# Local Development Run
- `local_run.sh` It will start the flask app in `development`.



# Folder Structure

- `db_directory` has the sqlite DB. Path can be adjusted in ``application/config.py`.
- `application` is where our application code is.
- `local_setup.sh` set up the virtualenv inside a local `.env` folder.
- `local_run.sh`  Used to run the flask application in development mode.
- `static` - default `static` files folder. It serves at '/static' path.
- `static/css` CSS files.
- `static/images` imagess.
- `templates` - Default flask templates folder.

```
├── application
     ├── config.py
       ├── controllers.py
       ├── database.py
       ├── models.py

├── db_directory
    └── proj.sqlite3

├── static
    ├── images
    	└── CSS

└── templates
    ├── admin_login.html
    	└── index.html

└── docs
    ├── report

├── local_run.sh
├── local_setup.sh
├── main.py
├── readme.md
├── requirements.txt
```