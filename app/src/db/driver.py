import time


def init_db(db):
    import app.src.db.models.usersDb
    import app.src.db.models.userPermissionDb
    import app.src.db.models.permissionDb


    dbRetries = 0

    while dbRetries != 12:
        try:
            # db.drop_all()
            db.create_all()
            break
        except:
            print('Couldn\'t connect to the database, retry in 5 sec')
            time.sleep(5)
            dbRetries += 1