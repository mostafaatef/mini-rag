from string import Template

### System ###
# system_prompt = "You are a smart assistant. Read the provided documents below, then answer the user's question at the end. Focus ONLY on the specific information requested by the user. Ignore irrelevant biography or details."
system_prompt = "نوعك هو مساعد ذكي. قوم بقراءة المستندات المقدمة أدناه، ثم اجب على سؤال المستخدم في النهاية. التركيز فقط على المعلومات المطلوبة من المستخدم. تجاهل التفاصيل غير ذات صلة."

### Document ###
document_prompt = Template(
    "\n".join(
        [
            "## رقم المستند: $document_no",
            "### المحتوى: $document_content",
        ]
    )
)

### Footer ###
footer_prompt = Template(
    "\n".join(
        [
            "",
            "---",
            "بناءً على المستندات المقدمة أعلاه، اجب على سؤال المستخدم في النهاية:",
            "السؤال: $query",
            "",
            "الإجابة:",
        ]
    )
)
