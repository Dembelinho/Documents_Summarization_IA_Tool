import os
import docx2txt
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class SummaryPrompt:
    """Class for structuring and managing summary prompts."""

    BASE_PROMPTS = {
        'english': {
            'concise': "Write a very concise summary in English in about 2-3 sentences of the following text:\n\n{text}",
            'moderate': "Write a moderate-length summary in English in about 4-5 paragraphs of the following "
                        "text:\n\n{text}",
            'detailed': "Write a detailed comprehensive summary in English while maintaining clarity of the following "
                        "text:\n\n{text}"
        },
        'french': {
            'concise': "Écrivez un résumé très concis en français en 2-3 phrases du texte suivant :\n\n{text}",
            'moderate': "Écrivez un résumé de longueur modérée en français en 4-5 paragraphes du texte suivant :\n\n{"
                        "text}",
            'detailed': "Écrivez un résumé détaillé et complet en français tout en maintenant la clarté du texte "
                        "suivant :\n\n{text}"
        }
        # U can add more languages as needed
    }

    BULLET_PROMPTS = {
        'english': {
            'concise': "Write 3-5 key bullet points in English summarizing the main ideas of the following text:\n\n{"
                       "text}",
            'moderate': "Write 5-8 bullet points in English providing a thorough summary of the following text:\n\n{"
                        "text}",
            'detailed': "Write 10-15 detailed bullet points in English covering all important aspects of the "
                        "following text:\n\n{text}"
        },
        'french': {
            'concise': "Écrivez 3-5 points clés en français résumant les idées principales du texte suivant :\n\n{text}",
            'moderate': "Écrivez 5-8 points en français fournissant un résumé approfondi du texte suivant :\n\n{text}",
            'detailed': "Écrivez 10-15 points détaillés en français couvrant tous les aspects importants du texte "
                        "suivant :\n\n{text}"
        }
    }

    KEY_POINTS_PROMPTS = {
        'english': {
            'concise': "Extract 3-5 key points in English from the following text. Each point should be concise and "
                       "capture the main idea:\n\n{text}",
            'moderate': "Extract 5-8 key points in English from the following text. Each point should be clear and "
                        "capture the main idea:\n\n{text}",
            'detailed': "Extract 10-15 key points in English from the following text. Each point should be detailed "
                        "and cover all important aspects:\n\n{text}"
        },
        'french': {
            'concise': "Extrayez 3-5 points clés en français du texte suivant. Chaque point doit être concis et "
                       "capturer l'idée principale :\n\n{text}",
            'moderate': "Extrayez 5-8 points clés en français du texte suivant. Chaque point doit être clair et "
                        "capturer l'idée principale :\n\n{text}",
            'detailed': "Extrayez 10-15 points clés en français du texte suivant. Chaque point doit être détaillé et "
                        "couvrir tous les aspects importants :\n\n{text}"
        }
        # Add more languages as needed
    }

    @staticmethod
    def get_prompt(summary_type, length, language="english"):
        """Returns the appropriate prompt based on the summary type and length selected."""
        if summary_type == "bullet_points":
            prompts = SummaryPrompt.BULLET_PROMPTS[language]
        elif summary_type == "key_points":
            prompts = SummaryPrompt.KEY_POINTS_PROMPTS[language]
        else:
            prompts = SummaryPrompt.BASE_PROMPTS[language]

        return PromptTemplate(template=prompts[length], input_variables=["text"])


def load_document(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return PyPDFLoader(file_path).load()
    elif file_extension == '.txt':
        return TextLoader(file_path).load()
    elif file_extension in ['.docx', '.doc']:
        # Extract text from docx file
        text = docx2txt.process(file_path)
        return [Document(page_content=text, metadata={"source": file_path})]
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def extract_summary_content(summary):
    """Extracts the content of the summary from the response object."""
    if hasattr(summary, "content"):
        return summary.content
    return str(summary)


class DocumentProcessor:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini",
                              api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, length_function=len)

    def process_document(self, file_path, summary_type="default", length="moderate", language="english"):
        try:
            # load & split documents
            documents = load_document(file_path)
            print("Documents loaded ---> ", documents)
            texts = self.text_splitter.split_documents(documents)
            text_content = "\n\n".join([doc.page_content for doc in texts])
            print("Texts split ---> ", texts)
        except Exception as e:
            raise ValueError(f" Error loading document: {str(e)}")

        try:
            # Get the appropriate prompt
            prompt = SummaryPrompt.get_prompt(summary_type, length, language)
            # Create LLM chain
            summarization_chain = prompt | self.llm
            # Generate summary
            summary = summarization_chain.invoke({"text": text_content})
            print("Summary ---> ", summary)
            return extract_summary_content(summary)
        except Exception as e:
            raise ValueError(f"Error when summarising : {str(e)}")
