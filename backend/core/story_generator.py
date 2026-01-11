from sqlalchemy.orm import Session

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM
from dotenv import load_dotenv
import os

load_dotenv()

def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


class StoryGenerator:

    @classmethod
    def _get_llm(cls):
        """
        Initialize Google's Gemini model (free tier available)
        Get your free API key from: https://makersuite.google.com/app/apikey
        """
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Get a free API key from: https://makersuite.google.com/app/apikey"
            )

        # Correct model names for Gemini:
        # - "gemini-pro" (older, stable)
        # - "gemini-1.5-pro-latest" (latest pro version)
        # - "gemini-1.5-flash-latest" (latest flash version - faster and free)
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.7
        )

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        # Get format instructions
        format_instructions = story_parser.get_format_instructions()
        
        # Build the complete prompt as a string (no template variables)
        complete_prompt = f"{STORY_PROMPT}\n\n{format_instructions}\n\nCreate the story with this theme: {theme}"

        # Invoke directly with the string
        raw_response = llm.invoke(complete_prompt)

        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        story_structure = story_parser.parse(response_text)

        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        return story_db

    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        node = StoryNode(
            story_id=story_id,
            content=node_data.content,
            is_root=to_bool(is_root),
            is_ending=to_bool(node_data.isEnding),
            is_winning_ending=to_bool(node_data.isWinningEnding),
            options=[]
        )
        db.add(node)
        db.flush()

        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                child_node = cls._process_story_node(db, story_id, next_node, False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()
        return node