from app import db
from hashlib import md5

# we are not declaring this table as a model like for users and posts
# This is an auxiliary table that has no data other than the foreign keys
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    # We define the relatinoship as seen from the left side entity
    # with the name followed, because when we query this relationship 
    # from the left side we will get the list of followed users
    #
    # 'User', the right side entitity that is in this relationship 
    #   in this case, self-referential. Left-side also user
    # secondary = association table used for this relationship
    # primaryjoin = condition that links the left-side entity
    # secondaryjoin = condition that links that right side entity
    # backref = defines how the relationship will be accessed from the
    #   right side entity
    #   The back reference will be called followers, and will return
    #   all the left side users that are linked to the target User
    #   in the right side. The additional lazy argument indicates execution mode
    #   dynamic = sets up the query to not run until specifically requested

    followed = db.relationship('User',
                                secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'),
                                lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3
    
    def avatar(self,size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    # To promote reusablity, we will implement the follow and unfollow
    # functionality in the User model instead of doing it directly in the
    # view functions. To be invoked in view functions, and for unit testing

    # As a matter of principle, it is always best to move the logic
    # of our application away from view functions, and into models,
    # because that simplifies the testing. Viw functions are harder to test
    # in an automated way

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        """
            We are taking the followed relatinoship query,
            which returns all teh (follower, followed) pairs that
            have our user as the follower, and we filter it by 
            the followed user

            self.followed = finds all the relationships with self's id
            filters
                [The table pointed to by self.followed]
                followers.followed_id = the followed_ids by the self
                user.id = the id of the other user
            .count = must be at least one, or just one

        """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        # join tables of Post that have user_id == followed_id from followers
        # filter such that self.id == folowers.c.follower_id

        # to allow users to see their own posts for "followed_posts", 
        # just make sure that each user is added as a follower of him/herself
        # int he database, and that will take care of this problem
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return '<User %r>' % (self.nickname)

# Posts table
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

