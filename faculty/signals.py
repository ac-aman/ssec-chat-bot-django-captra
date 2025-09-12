from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Faculty
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_bot.vectore_store import vector_store
from langchain.schema import Document


@receiver(post_save, sender=Faculty)
def faculty_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    print(f"[Faculty {action}] {instance.name} ({instance.designation})")

    prompt = ChatPromptTemplate.from_template(
        """
    You are an assistant creating simple summaries about faculty members.
    Write in basic English (not too professional). 
    The summary should be less than 500 words and suitable for embeddings.

    Rules:
    - If any field is "N/A" or empty, skip it.
    - Mention the faculty name first.
    - If room_no is available, describe it as the place where the lab seats are. 
      Example: "teaches in room 101" or "seats in lab 202".
    - Use short, clear sentences so it can be queried easily later.

    Context (Faculty record):
    Name: {name}
    Designation: {designation}
    Department: {department}
    Room: {room_no}
    Expertise: {expertise}
    Experience: {years_of_experience} years
    Qualifications: {qualifications}
    Contact: {contact_email}, {contact_phone}
    Extra: {extra_curriculum}
    Notes: {description}

    Output: A simple, clear text summary that can be stored for search and embedding.
    """
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0.7, max_output_tokens=800
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "name": instance.name,
            "designation": instance.designation or "N/A",
            "department": instance.department or "N/A",
            "room_no": instance.room_no or "N/A",
            "expertise": instance.expertise or "N/A",
            "years_of_experience": instance.years_of_experience or "N/A",
            "qualifications": instance.qualifications or "N/A",
            "contact_email": instance.contact_email or "N/A",
            "contact_phone": instance.contact_phone or "N/A",
            "extra_curriculum": instance.extra_curriculum or "N/A",
            "description": instance.description or "N/A",
        }
    )

    summary = (
        getattr(response, "content", None)
        or getattr(response, "text", None)
        or str(response)
    )

    doc = Document(
        page_content=summary,
        metadata={"faculty_id": instance.id, "name": instance.name},
    )

    vector_store.add_documents([doc])
    # vector_store.persist()


@receiver(post_delete, sender=Faculty)
def faculty_deleted(sender, instance, **kwargs):
    print(f"[Faculty Deleted] {instance.name}")
