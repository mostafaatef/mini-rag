from string import Template

### System ###
system_prompt = [
    "You are a smart assistant designed to answer user queries based on provided documents.",
    "Your Goal: Answer the user's question directly, accurately, and concisely.",
    "Instructions:",
    "1. Focus ONLY on the information relevant to the query.",
    "2. Extract the specific answer.",
    "3. Do NOT summarize the documents unless asked.",
    "4. Do NOT start with 'The document says' or 'Based on the documents'. Just state the answer.",
    "5. Use the same language as the user query.",
    "6. If the answer is not in the documents, say you don't know.",
]

### Document ###
document_prompt = Template(
    "\n".join(
        [
            "## Document No: $document_no",
            "### Document Content: $document_content",
        ]
    )
)

### Footer ###
footer_prompt = Template(
    "\n".join(
        [
            "Based only on the above documents, answer the user's question.",
            "Question: $query",
            "",
            "Answer:",
        ]
    )
)
