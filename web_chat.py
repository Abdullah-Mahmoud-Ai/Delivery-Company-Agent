from dotenv import load_dotenv
from agent import create_agent_deps, shipping_agent


load_dotenv()

deps = create_agent_deps()

app = shipping_agent.to_web(

    deps=deps,

)