from peewee import *
import datetime
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin #the packages are installed to the ext module..import
#ext = external area where the file is stored
#UserMixin =
DATABASE = SqliteDatabase("social.db") #tells ppl that we want this to be a constant

class User(UserMixin,Model): #it is a model but user mixin is being used as a layer over it
    username = CharField(unique=True) #must be unique
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now) #now is the time we use here
    is_admin = BooleanField(default=False) # special ui abilities for certain users

    def get_posts(self):
        return Post.select().where(Post.user << self.following() | (Post.user == self))
    def get_stream(self):
        return Post.select().where(Post.user == self)
    def following(self):
        """Users we following bruh"""
        return(
            User.select().join(Relationship,on=Relationship.to_user).where(Relationship.from_user == self))#model we select from,field we select on
        # select all the users where the from user is me
    def followers(self):
        """ppl following current user """
        return(User.select().join(Relationship,on=Relationship.from_user).where(Relationship.to_user==self))

    class Meta:
        database = DATABASE
        order_by = ("-joined_at",)


    @classmethod #method that belongs to a class that can create a class it belongs to
    #with cls, it will create the user model instance when it runs this method
    #so were basically saying User.create --> creating an instance of the class from inside of it
    def create_user(cls,username, email,password,admin= False): # we use cls instead of self
        try :
            with DATABASE.transaction():

                # try this if it works keep going,
            # if it fails remove whatever doesnt work... only create full users with all attrs
                cls.create(
                    username=username,
                    email= email,
                    password=generate_password_hash(password),
                    is_admin = admin)
        except IntegrityError:
            raise ValueError("User already exists bruh")
class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User,related_name='posts')#model this foregin key points to,what the related model will call this model
    content = TextField()
    class Meta:
        database = DATABASE

        order_by = ("-timestamp")# tuple so we can have it ordered by dif filters

class Relationship(Model):
    from_user = ForeignKeyField(User,related_name="relationships")
    to_user = ForeignKeyField(User,related_name="related to")

    class Meta:
        #tell db how to find and remember the data.. specifies if an index is unique
        database = DATABASE
        indexes = ((('from_user',"to_user"),True),)
def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User],safe = True)
    DATABASE.create_tables([Post],safe = True)
    DATABASE.create_tables([Relationship],safe = True)
    DATABASE.close()