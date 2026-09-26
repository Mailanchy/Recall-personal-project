from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'), echo=True)
Session = sessionmaker(engine)
