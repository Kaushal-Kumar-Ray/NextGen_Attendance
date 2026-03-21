import psycopg2

def get_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_AqMiW60UHuZX@ep-winter-poetry-a473vvsy-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
    )