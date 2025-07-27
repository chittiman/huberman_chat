from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class AnswerType(str, Enum):
    DESCRIPTIVE = "descriptive"
    PRESCRIPTIVE = "prescriptive"
    METHODOLOGICAL = "methodological"


class DifficultyLevel(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class AnswerScope(str, Enum):
    SINGLE_CHAPTER = "single_chapter"
    CROSS_CHAPTER = "cross_chapter"


class RAGQuestion(BaseModel):
    question_id: int = Field(
        ...,
        description="Unique identifier for the question, starting from 1"
    )
    question: str = Field(
        ...,
        description="The actual question a user might ask",
        min_length=10,
        max_length=500
    )
    expected_answer_type: AnswerType = Field(
        ...,
        description="Type of content function the question targets"
    )
    context_requirements: str = Field(
        ...,
        description="Brief description of what information is needed to answer",
        min_length=10,
        max_length=300
    )
    ground_truth_reference: List[int] = Field(
        ...,
        description="List of chapter_id integers that contain the answer",
        min_items=1,
        max_items=5
    )  # type: ignore
    difficulty_level: DifficultyLevel = Field(
        ...,
        description="Complexity level of the question"
    )
    answer_scope: AnswerScope = Field(
        ...,
        description="Whether answer requires single chapter or cross-chapter synthesis"
    )
    question_category: str = Field(
        ...,
        description="Topic category (e.g., sleep, exercise, nutrition)",
        min_length=3,
        max_length=50
    )

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "question_id": 1,
                "question": "What physiological changes occur in the brain during REM sleep?",
                "expected_answer_type": "descriptive",
                "context_requirements": "Information about brain activity and physiological processes during REM sleep stage",
                "ground_truth_reference": [2],
                "difficulty_level": "moderate",
                "answer_scope": "single_chapter",
                "question_category": "sleep"
            }
        }


class RAGQuestionSet(BaseModel):
    questions: List[RAGQuestion] = Field(
        ...,
        description="List of generated questions for RAG evaluation",
        min_items=4,
        max_items=8
    )  # type: ignore

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "question_id": 1,
                        "question": "What physiological changes occur in the brain during REM sleep?",
                        "expected_answer_type": "descriptive",
                        "context_requirements": "Information about brain activity and physiological processes during REM sleep stage",
                        "ground_truth_reference": [2],
                        "difficulty_level": "moderate",
                        "answer_scope": "single_chapter",
                        "question_category": "sleep"
                    }
                ]
            }
        }


class Chapter(BaseModel):
    """Represents a single chapter in the video analysis."""
    timestamp: str = Field(..., description="Timestamp in format like '0:00' or '12:45'")
    heading: str = Field(..., description="Chapter heading describing the main topic")
    content: str = Field(..., description="Summary of the chapter content in proper sentences")


class VideoAnalysis(BaseModel):
    """Main video analysis structure containing summary, chapters, and topics."""
    overall_summary: str = Field(..., description="3-4 sentence summary of the entire video")
    chapters: List[Chapter] = Field(..., description="List of chapters with timestamps and content")
    topics: List[str] = Field(..., description="Key topics and keywords from the video")

# Example usage:
if __name__ == "__main__":
    # Example JSON data
    example_data = {
            "overall_summary": "This video explains machine learning fundamentals. It covers basic concepts, algorithms, and practical applications. The presenter demonstrates how to implement simple models and discusses real-world use cases.",
            "chapters": [
                {
                    "timestamp": "0:00",
                    "heading": "Introduction to Machine Learning",
                    "content": "The video begins with an overview of machine learning and its importance in modern technology."
                },
                {
                    "timestamp": "5:30",
                    "heading": "Core Algorithms",
                    "content": "Discussion of fundamental algorithms including linear regression, decision trees, and neural networks."
                }
            ],
            "topics": ["machine learning", "algorithms", "neural networks", "data science", "AI"]
        }
    
    # Parse and validate the data
    analysis = VideoAnalysis(**example_data)
    print(analysis.model_dump_json(indent=2))