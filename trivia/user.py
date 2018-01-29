def get_user():

    return db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])

def rows():

    return db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

def register():

    db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", \
                                username = request.form.get("username"), \
                                hash = pwd_context.hash(request.form.get("password")))

def old_hash():

    return db.execute("SELECT hash FROM users WHERE id=:id", id=session["user_id"])

def check_hash():

    return pwd_context.verify(request.form.get("old_password"), old_hash[0]["hash"])

def update_pass():

    return db.execute("UPDATE users set hash=:hash WHERE id=:id", \
                    hash=pwd_context.hash(new_pass), id=session["user_id"])