from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "../data/izypizy.db")
PI_FILE: str = os.getenv("PI_FILE", "../data/pi.txt")
