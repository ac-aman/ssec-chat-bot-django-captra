# faculty/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from .prompts import finally_prompt, rewritten_history_prompt
from .vectore_store import vector_store


# ----------------------------
# LLM Setup
# ----------------------------
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


# ----------------------------
# Retriever Setup
# ----------------------------
retriever = vector_store.as_retriever(search_kwargs={"k": 3})


# ----------------------------
# Rewrite Chain
# ----------------------------
rewrite_chain = LLMChain(
    llm=llm,
    prompt=rewritten_history_prompt,
    output_key="rewritten_prompt",
)


# ----------------------------
# QA Chain (with retriever + final prompt)
# ----------------------------
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    combine_docs_chain_kwargs={"prompt": finally_prompt},
    return_source_documents=False,
)


# ----------------------------
# API View
# ----------------------------
class ChatBotView(APIView):
    """API endpoint for chatting with Santilal Shah Bot."""

    def post(self, request):
        query = request.data.get("question")
        history = request.data.get("history", [])
        print(history)

        if not query:
            return Response(
                {"error": "Missing 'question' in request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # ----------------------------
            # Prepare chat history
            # ----------------------------
            chat_history = []
            for h in history[-10:]:  # keep last 10 only
                role = h.get("role")
                msg = h.get("message", "")
                if role == "user":
                    chat_history.append(HumanMessage(content=msg))
                elif role == "CAPTRA":
                    chat_history.append(AIMessage(content=msg))

            # ----------------------------
            # Stage 1: Rewrite Query
            # ----------------------------
            rewrite_result = rewrite_chain.invoke(
                {"current_info": query, "history_data": history}
            )
            rewritten_prompt = rewrite_result["rewritten_prompt"]

            # ----------------------------
            # Stage 2: Final Answer
            # ----------------------------
            result = qa_chain.invoke(
                {"question": rewritten_prompt, "chat_history": chat_history}
            )
            response = result["answer"]

            return Response(
                {
                    "rewritten_prompt": rewritten_prompt,
                    "answer": response,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
