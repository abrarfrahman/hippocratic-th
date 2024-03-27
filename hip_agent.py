import weaviate
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Weaviate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI
from weaviate.embedded import EmbeddedOptions


class HIPAgent:
    def __init__(self):
        """
        Initializes parameters. 
        """
        self.textbook_path = "./textbook.txt"
        self.textbook = None
        self.embeddings = None
        self.retriever = None
        self.client = OpenAI()

    def load_data_and_embeddings(self):
        """
        Loads textbook.txt and generates embeddings for efficient retrieval.
        """

        # Load textbook.txt.
        loader = TextLoader(self.textbook_path, encoding = 'UTF-8')
        self.textbook = loader.load()

        # Chunk textbook.txt.
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=[" ", ",", "\n"])
        chunks = text_splitter.split_text(str(self.textbook))
        chunks = text_splitter.create_documents(chunks)

        # Generate and save embeddings.
        client = weaviate.Client(
            embedded_options = EmbeddedOptions()
        )
        vectorstore = Weaviate.from_documents(
            client = client,    
            documents = chunks,
            embedding = OpenAIEmbeddings(),
            by_text = False
        )
        self.embeddings = vectorstore

        # Define retriever.
        self.retriever = vectorstore.as_retriever()

    def get_response(self, question, answer_choices):
        """
        Calls the OpenAI 3.5 API to generate a response to the question.
        The response is then matched to one of the answer choices and the index of the
        matching answer choice is returned. If the response does not match any answer choice,
        -1 is returned.

        Args:
            question: The question to be asked.
            answer_choices: A list of answer choices.

        Returns:
            The index of the answer choice that matches the response, or -1 if the response
            does not match any answer choice.
        """

        # Load embeddings if not populated.
        if not self.embeddings:
            self.load_data_and_embeddings()
        if not self.retriever:
            raise ValueError("Retriever component not initialized.")

        # Prepare prompt template.
        template = """Use the following pieces of retrieved context to answer the question.
        Question: {question} 
        Context: {context} 
        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)

        # Define RAG chain
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt 
            | llm
            | StrOutputParser() 
        )

        # Invoke RAG chain
        answer = rag_chain.invoke(question)

        # Correlate RAG answer to answer choices.
        answer_str = "\n".join(answer_choices)
        prompt = f"Generated response: {answer} \n\n Which of the following multiple choice answers is the closest to the generated response? Respond with the answer string verbatim. \n\n {answer_str}"

        # Call the OpenAI 3.5 API.
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        response_text = response.choices[0].message.content.lower()

        # Match the response to one of the answer choices.
        for i, answer_choice in enumerate(answer_choices):
            if answer_choice.lower() in response_text:
                return i

        # If the response does not match any answer choice, return -1.
        return -1
