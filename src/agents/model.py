import yaml
from dotenv import load_dotenv
from langchain_perplexity import ChatPerplexity
from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint

from src.utils.format import clean_format

load_dotenv()

with open("src/configs/config.yaml",'r') as f:
    config = yaml.safe_load(f)

llm_hugg = HuggingFaceEndpoint(
    repo_id = config['llm_huggingface']['repo_id'],
    task = config["llm_huggingface"]['task']
)

huggingface_model = ChatHuggingFace(llm=llm_hugg)

perplexity_model = ChatPerplexity(
    temperature = config["llm_perplexity"]["temperature"],
    model = config["llm_perplexity"]["model"]
)

if __name__ == '__main__':
     result = huggingface_model.invoke("What is the capital of India")
     r1 = perplexity_model.invoke("What is the capital of India")
     print(clean_format(r1.content))