
- **Backend:** FastAPI  
- **Frontend:** React.js  
- **Database:** PostgreSQL  


-----------------------
Backend Setup

1.Navigate to the backend folder:

cd /backend


2.Create and activate a virtual environment :

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


3.Install Python dependencies:

pip install -r requirements.txt

fastapi==0.112.0
uvicorn[standard]==0.23.2
sqlalchemy==2.0.23
asyncpg==1.0.0
psycopg2-binary==2.9.7
pydantic==1.10.12
fakeredis==2.20.0
python-multipart==0.0.6

4.Run the backend:

uvicorn app.main:app --reload


The backend will run at http://127.0.0.1:8000.

----------------------------------Frontend Setup-------------------------------------------------------

1.Navigate to the frontend folder:

cd ../frontend


I2.nstall frontend dependencies:

npm install


3.Run the frontend:

npm start


The frontend will run at http://localhost:3000.
