from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import College, Department
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_bot.vectore_store import vector_store
from langchain.schema import Document


@receiver(post_save, sender=College)
def college_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    print(f"[College {action}] {instance.name}")

    prompt = ChatPromptTemplate.from_template(
        """
    You are an assistant creating simple summaries about colleges.
    Write in basic English (not too professional). 
    The summary should be less than 500 words and suitable for embeddings.

    Rules:
    - If any field is "N/A" or empty, skip it.
    - Mention the college name first.
    - Mention the principal if available.
    - Mention the departments in the college (if available).
    - Use short, clear sentences so it can be queried easily later.

    Context (College record):
    Name: {name}
    Principal: {principal_name}
    Address: {address}
    Contact: {contact_email}, {contact_phone}
    Website: {website}
    Description: {description}

    Output: A simple, clear text summary that can be stored for search and embedding.
    """
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        max_output_tokens=800,
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "name": instance.name,
            "principal_name": instance.principal_name or "N/A",
            "address": instance.address or "N/A",
            "contact_email": instance.contact_email or "N/A",
            "contact_phone": instance.contact_phone or "N/A",
            "website": instance.website or "N/A",
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
        metadata={"college_id": instance.id, "name": instance.name},
    )

    vector_store.add_documents([doc])
    # vector_store.persist()


@receiver(post_delete, sender=College)
def college_deleted(sender, instance, **kwargs):
    print(f"[College Deleted] {instance.name}")
    # Optionally, you can remove the college documents from vector_store if needed


@receiver(post_save, sender=Department)
def department_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    print(f"[Department {action}] {instance.name} ({instance.college.name})")

    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant creating simple summaries about college departments.
        Write in basic English (not too professional). 
        The summary should be less than 500 words and suitable for embeddings.

        Rules:
        - If any field is "N/A" or empty, skip it.
        - Mention the department name and the college it belongs to.
        - Mention the HOD if available.
        - Include contact details if available.
        - Mention number of seats if available.
        - Use short, clear sentences so it can be queried easily later.

        Context (Department record):
        Department: {name}
        College: {college}
        HOD: {hod_name}
        Contact: {contact_email}, {contact_phone}
        Number of Seats: {num_seats}
        Description: {description}

        Output: A simple, clear text summary that can be stored for search and embedding.
        """
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        max_output_tokens=800,
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "name": instance.name,
            "college": instance.college.name,
            "hod_name": instance.hod_name or "N/A",
            "contact_email": instance.contact_email or "N/A",
            "contact_phone": instance.contact_phone or "N/A",
            "num_seats": instance.num_seats or "N/A",
            "description": instance.description or "N/A",
        }
    )

    summary = (
        getattr(response, "content", None)
        or getattr(response, "text", None)
        or str(response)
    )

    doc = Document(
        page_content=str(summary),
        metadata={
            "department_id": instance.id,
            "name": instance.name,
            "college": instance.college.name,
        },
    )

    vector_store.add_documents([doc])
    # vector_store.persist()


@receiver(post_delete, sender=Department)
def department_deleted(sender, instance, **kwargs):
    print(f"[Department Deleted] {instance.name} ({instance.college.name})")
    # Optionally, remove department docs from vector_store if needed
