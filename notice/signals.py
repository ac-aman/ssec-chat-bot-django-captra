# notice/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notice
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_bot.vectore_store import vector_store
from langchain.schema import Document


@receiver(post_save, sender=Notice)
def notice_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    print(f"[Notice {action}] {instance.title} ({instance.department})")

    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant creating simple summaries about college notices.
        Write in basic English (not too professional). 
        The summary should be less than 1000 words and suitable for embeddings.

        Rules:
        - If any field is "N/A" or empty, skip it.
        - Mention the notice title first.
        - Mention the department if available.
        - Use short, clear sentences so it can be queried easily later.

        Context (Notice record):
        Title: {title}
        Department: {department}
        Content: {content}

        Output: A simple, clear text summary that can be stored for search and embedding.
        """
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        max_output_tokens=1000,
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "title": instance.title,
            "department": instance.department or "N/A",
            "content": instance.content or "N/A",
        }
    )

    summary = (
        getattr(response, "content", None)
        or getattr(response, "text", None)
        or str(response)
    )

    doc = Document(
        page_content=summary,
        metadata={
            "notice_id": instance.id,
            "title": instance.title,
            "department": instance.department,
        },
    )

    vector_store.add_documents([doc])
    # vector_store.persist()


@receiver(post_delete, sender=Notice)
def notice_deleted(sender, instance, **kwargs):
    print(f"[Notice Deleted] {instance.title} ({instance.department})")
    # Optionally, remove the notice document from vector_store if needed
