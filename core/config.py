DB = 'postgresql'
DB_USER = 'postgres'
DB_PASSWORD = '3636'
DB_SERVER = 'localhost'
DB_PORT = '5433'
DB_NAME = 'msp_database'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'dudqls327@bctone.kr'
SENDER_PASSWORD = 'mwdc lebe phqy rovf'

CLAUDE_API = "API KEY"
GPT_API = "API KEY"

OPENAI_MODELS = ['gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
ANTHROPIC_MODELS = ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']

VECTOR_DB_CONNECTION = f'{DB}://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}'
EMBEDDING_MODEL = 'text-embedding-ada-002'
DEFAULT_CHAT_MODEL = 'gpt-3.5-turbo'
CHROMA_PERSIST_DIRECTORY = './chroma_db'

UPLOADED_FILES = "C:\\Users\\leegy\\Desktop\\2025\\back\\saved_file"