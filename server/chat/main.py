from openai import OpenAI
from pinecone import Pinecone

from utils.Utilities import OPENAI_API_KEY, PINECONE_API_KEY, CORS_HEADERS
from utils.Utilities import (
    encrypt_and_structure_data,
    api_key_required,
    embed_text,
    get_user_docs_by_type,
    update_document_firestore,
    insert_into_firestore,
    decrypt_text,
)

# To call service:
# curl -X POST \
#   -F "api_key=key" \
#   -F "doc_id=Akyc7QWwIbVk8rxrKaaT"
# http://localhost:8080
#   https://chat-286240844421.us-central1.run.app

PINECONE_INDEX = "puurlee-test"

oa = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "puurlee-test"  # the index where you stored user data
index = pc.Index(index_name)


def retrieve_relevant_docs(user_id, query, top_k=3):
    """
    1. Create query embedding
    2. Query pinecone
    3. Return the top_k docs
    """
    query_embedding = embed_text(oa, query)

    # Pinecone expects a single vector as a list, top_k results
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"user_id": {"$eq": user_id}},
    )

    # each match has .metadata["chunk"] if you stored your chunk text under "chunk"
    matches = []
    for match in result["matches"]:
        match_text = decrypt_text(match["metadata"].get("content", ""))
        matches.append(match_text)
    return matches


def answer_health_question(user_id, query):
    """
    1. Retrieve relevant chunks from Pinecone
    2. Construct a chat prompt
    3. Call OpenAI to generate an answer
    """
    # Retrieve relevant data from Pinecone
    relevant_docs = retrieve_relevant_docs(user_id, query)
    print("Num docs", len(relevant_docs))

    # Construct context for the LLM
    context = "\n\n".join(relevant_docs)

    # Get user conversation context
    user_conversation_doc = get_user_docs_by_type(user_id, "conversation")
    conversation = ""
    conversation_doc_data = dict()
    conversation_doc_id = None
    if user_conversation_doc:
        conversation_doc_id = user_conversation_doc.id
        conversation_doc_data = user_conversation_doc.to_dict()
        conversation += "\n" + decrypt_text(conversation_doc_data["content"])

    decline_msg = "Sorry, I'm here to assist with health and product related inquiries based on your health history and chat records."
    print("Conversation before:", conversation_doc_id, conversation)
    # Use a system message or a more advanced prompt. For example:
    system_prompt = (
        "You are a helpful health assistant with knowledge based on user-specific data.\n"
        "Assume that all data given are health status reports with actual quantative test results.\n"
        "Use the following data to answer the user's question:\n\n"
        f"{context}\n\n"
        "Additionally, use the following conversation content to augment your response:\n\n"
        f"{conversation}\n\n"
        "If the information is insufficient or unclear, say so.\n\n"
        "You do not need to always state that the user should consult a healthcare professional, only for very important reasons.\n\n"
        f"If the query is not health or product related, always decline with '{decline_msg}' "
    )

    # Call OpenAI ChatCompletion
    response = oa.chat.completions.create(
        model="gpt-4o",  # "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.4,
        max_tokens=300,
    )

    # Extract the assistant’s answer
    answer = response.choices[0].message.content
    print("\nAnswer:", answer + "\n")

    add_to_conversation = query not in conversation
    add_to_conversation &= decline_msg not in answer

    if add_to_conversation:
        conversation += query + "\n\n" + answer + "\n\n"
        conversation_doc_data = encrypt_and_structure_data(
            conversation, "", user_id, "conversation"
        )
        print("Conversation after:", conversation_doc_id, conversation)

        if conversation_doc_id:
            update_document_firestore(conversation_doc_id, conversation_doc_data)
        else:
            insert_into_firestore(conversation_doc_data)

    return (answer, 200, CORS_HEADERS)


# Entry point for Google Cloud Function
@api_key_required
def main(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        user_id = request.form.get("user_id")
        query = request.form.get("query")

        if user_id and query:
            return answer_health_question(user_id, query)

    return ("Bad request: user_id and query required.", 400, CORS_HEADERS)
