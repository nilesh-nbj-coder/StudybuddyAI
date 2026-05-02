from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuestion,FillBlankQuestion
from src.prompts.templates import mcq_prompt_template,fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.custom_exception import CustomException
from src.common.logger import get_logger


class QuestionGenerator:
    def __init__(self):
        self.llm=get_groq_llm()
        self.logger=get_logger(self.__class__.__name__)
        
    def _retry_and_parse(self,prompt,parser,topic,difficulty):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic {topic} with difficulty {difficulty}")
                response=self.llm.invoke(prompt.format(topic=topic,difficulty=difficulty),)
                parsed=parser.parse(response.content)
                self.logger.info("Succsessfully parse the question")
                return parsed
            except Exception as e:
                self.logger.error(f"Error : {str(e)}")
                if attempt == settings.MAX_RETRIES-1:
                    raise CustomException(f"Generation failed after {settings.MAX_RETRIES} attempts",e)
                
    def generate_mcq(self,topic:str,difficulty:str='Medium')-> MCQQuestion:
        try:
            parser=PydanticOutputParser(pydantic_object=MCQQuestion)            
            mcq_question=self._retry_and_parse(mcq_prompt_template,parser,topic,difficulty)
            if len(mcq_question.options) != 4 or mcq_question.correct_answer not in mcq_question.options: # type: ignore
                raise ValueError("Invalid MCQ structure")
            
            self.logger.info("Generated a valid MCQ Question")
            return mcq_question # type: ignore
        except Exception as e:
            self.logger.error(f"Failed to generate MCQ : {str(e)}")
            raise CustomException("MCQ generation failed",e)
        
        
    def generate_fill_blank(self,topic:str,difficulty:str='Medium')-> FillBlankQuestion:
        try:
            parser=PydanticOutputParser(pydantic_object=FillBlankQuestion)            
            fib_question=self._retry_and_parse(fill_blank_prompt_template,parser,topic,difficulty)
            if "___" not in fib_question.question:  # type: ignore
                raise ValueError("Fill in blank should contain '___'")
            self.logger.info("Generated a valid Fill in blank Question")                
            return fib_question # type: ignore
        except Exception as e:
            self.logger.error(f"Failed to generate Fill in blank question : {str(e)}")
            raise CustomException('Fill in blank question generation failed',e)
        
                             
