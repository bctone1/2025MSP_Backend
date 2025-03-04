### To run server ( PORT 5000 )

`
uvicorn main:app --host 0.0.0.0 --port 5000
`

### Input your Claude API Key

`
client = anthropic.Anthropic(
    api_key="Your Claude API Key"
)
`

### Input your OpenAI (ChatGPT) API Key

`
openai.api_key = 'Your OpenAI API Key'
`

If you want to create table, run 'create_table.py'
