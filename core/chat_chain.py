# core/chat_chain.py

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

def build_chat_chain(llm, retriever, get_history_func):
    # Prompt to rewrite follow-up question
    contextualize_q_prompt = PromptTemplate(
        input_variables=["chat_history", "input"],
        template="""
        Given the following conversation and a follow-up question, rephrase the follow-up
        to be a standalone question. If the question is already standalone, return it unchanged.

        Chat History:
        {chat_history}

        Follow-up question:
        {input}
        """
    )

    # Use it to create a history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=contextualize_q_prompt
    )

    # System QA prompt
    system_prompt = (
        "You are a helpful assistant. Use the retrieved context below to answer the question.\n"
        "If the answer is not in the context, say you don't know. Answer concisely.\n"
        "\n\n{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Runnable chain with memory support
    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        get_history_func,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    return conversational_chain
