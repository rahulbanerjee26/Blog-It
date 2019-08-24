from sqlalchemy import Column,ForeignKey,Integer,String,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime 


Base = declarative_base()

class User(Base):
    #table name
    __tablename__ = 'user'

    #Mappers
    id = Column(Integer,primary_key = True)
    name = Column(String(250),nullable = False)
    email = Column(String(250),nullable = False)
    picture = Column(String(250))



#Classes
class Post(Base):
    #table name
    __tablename__ = 'post'

    #Mappers
    id = Column(Integer,primary_key = True)
    title = Column(String(50),nullable = False)
    subtitle = Column(String(50),nullable = False)
    author = Column(String(50),nullable = False)
    datetime = Column(DateTime, default=datetime.utcnow)
    description = Column(String(),nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
       return {
           'title'          : self.title,
           'id'             : self.id,
           'subtitle'       : self.subtitle,
           'author'         : self.author,
           'datetime'       : self.datetime,
           'description'    : self.description
       }    


#Configuration
engine = create_engine('sqlite:///PostsUser.db')
Base.metadata.create_all(engine)       

