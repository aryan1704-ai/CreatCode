import os
from unittest import result

from dotenv import load_dotenv
from openai import OpenAI  # type: ignore[reportMissingImports]


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)


# =========================================================
# OPENROUTER CLIENT
# =========================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "CreatCode"
    }
)


# =========================================================
# COMMON AI REQUEST
# =========================================================

def ask_ai(
    prompt: str,
    temperature: float = 0.2
):
    """
    Send a request to OpenRouter.

    Lower temperature is used because
    CreatCode should produce predictable
    programming results.
    """

    try:

        response = client.chat.completions.create(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CreatCode, an expert AI "
                        "programming assistant. "
                        "Write accurate, clean, practical "
                        "and beginner-friendly programming "
                        "solutions."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=temperature
        )

        result = response.choices[0].message.content

        if not result:
            raise RuntimeError(
                "AI returned an empty response."
            )

        return result.strip()


    except Exception as e:

        error_message = str(e)

        print(
            f"OpenRouter error: {error_message}"
        )


        if "429" in error_message:

            raise RuntimeError(
                "AI service is temporarily "
                "rate-limited. Please try again "
                "after a short time."
            )


        if (
            "401" in error_message
            or "403" in error_message
        ):

            raise RuntimeError(
                "AI API authentication failed. "
                "Please check the OpenRouter API key."
            )


        raise RuntimeError(
            "AI service error. Please try again later."
        )


# =========================================================
# CLEAN AI CODE
# =========================================================

def clean_code_response(text: str) -> str:

    if not text:
        return ""

    code = text.strip()


    # Remove opening Markdown fence

    if code.startswith("```"):

        first_newline = code.find("\n")

        if first_newline != -1:

            code = code[
                first_newline + 1:
            ]


    # Remove closing Markdown fence

    if code.endswith("```"):

        code = code[:-3]


    return code.strip()


# =========================================================
# GENERATE CODE
# =========================================================

def generate_code(prompt: str):
    system_prompt = """
You are an expert software developer.

Generate complete, working source code for the user's request.

STRICT OUTPUT RULES:
1. Return ONLY the source code.
2. Do NOT use Markdown code fences such as ```python or ```.
3. Do NOT add explanations before or after the code.
4. Do NOT write labels such as "Here is the code:".
5. Do NOT write "Output:", "Explanation:", or similar text.
6. Include all required imports.
7. Make the code complete and directly usable.
8. Prefer simple, readable code unless the user specifically requests advanced code.
"""

    full_prompt = f"""
{system_prompt}

User request:
{prompt}
"""

    result = ask_ai(full_prompt)

    return clean_code_response(result)

def clean_code_response(code: str) -> str:
    if not code:
        return ""

    code = code.strip()

    # Remove Markdown code fences
    if code.startswith("```"):
        lines = code.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    return code

# =========================================================
# EXPLAIN CODE
# =========================================================

def explain_code(code: str):

    ai_prompt = f"""
You are CreatCode's code explanation engine.

Explain the following code in simple,
student-friendly language.

CODE:

{code}


Provide the explanation using this structure:

1. Purpose
   - What the program does.

2. How It Works
   - Explain the logic step by step.

3. Important Parts
   - Explain important variables,
     functions, classes or statements.

4. Example
   - Give a simple example if useful.

5. Complexity
   - Give time complexity.
   - Give space complexity.

6. Summary
   - Give a short final summary.

Rules:

- Use simple language.
- Avoid unnecessary jargon.
- Do not rewrite the entire code.
- Do not invent functionality that
  does not exist in the code.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.25
    )


# =========================================================
# DEBUG CODE
# =========================================================

def debug_code(
    code: str,
    error: str = ""
):

    ai_prompt = f"""
You are CreatCode's debugging engine.

Analyze the following code and identify
programming errors.

CODE:

{code}


ERROR MESSAGE:

{error if error else "No error message was provided."}


Use this structure:

1. Problem
2. Cause
3. Solution
4. Corrected Code
5. Prevention Tips

Rules:

- Identify syntax errors.
- Identify logical errors.
- Identify common runtime problems.
- Do not invent errors that are not supported
  by the code.
- If the code is already correct, clearly
  say that no obvious error was found.
- Keep the explanation beginner-friendly.
- When corrected code is required, provide
  complete corrected code.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.2
    )


# =========================================================
# OPTIMIZE CODE
# =========================================================

def optimize_code(code: str):

    ai_prompt = f"""
You are CreatCode's code optimization engine.

Analyze the following code:

{code}


Provide the result using:

1. Current Approach
2. Problems
3. Optimization Opportunities
4. Optimized Code
5. Complexity Before
6. Complexity After
7. Summary

Rules:

- Preserve the original functionality.
- Do not optimize only for shorter code.
- Consider readability and maintainability.
- Consider time complexity.
- Consider space complexity.
- Explain important changes simply.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.2
    )


# =========================================================
# COMPLEXITY ANALYSIS
# =========================================================

def analyze_complexity(code: str):

    ai_prompt = f"""
You are CreatCode's algorithm complexity
analysis engine.

Analyze this code:

{code}


Determine:

1. Best-case time complexity
2. Average-case time complexity
3. Worst-case time complexity
4. Space complexity

Then explain why.

Use Big-O notation where appropriate.

Also identify the main loop,
nested loops, recursion, sorting,
searching or other operations that
affect complexity.

Keep the explanation simple and accurate.

Do not change the code.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.15
    )


# =========================================================
# TEST CASE GENERATOR
# =========================================================

def generate_test_cases(code: str):

    ai_prompt = f"""
You are CreatCode's test-case generation engine.

Analyze this code:

{code}


Generate useful test cases.

Use this format:

| # | Input | Expected Output | Purpose |
|---|---|---|---|

Include:

- Normal cases
- Small cases
- Large cases
- Edge cases
- Empty input when applicable
- Invalid input when applicable
- Boundary cases

After the table, explain
important edge cases briefly.

Do not invent behavior that the
program does not define.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.25
    )


# =========================================================
# CODE CONVERSION
# =========================================================

def convert_code(
    code: str,
    target_language: str
):

    ai_prompt = f"""
You are CreatCode's code conversion engine.

Convert the following code to:

TARGET LANGUAGE:
{target_language}


SOURCE CODE:

{code}


Rules:

1. Preserve the original functionality.

2. Use idiomatic syntax for the target
   programming language.

3. Use appropriate standard libraries.

4. Keep variable and function meaning
   understandable.

5. Return the complete converted program.

6. Do not use Markdown code fences.

7. Do not include explanations.

8. Return ONLY the converted source code.
"""

    result = ask_ai(
        ai_prompt,
        temperature=0.15
    )

    return clean_code_response(result)


# =========================================================
# PROMPT GENERATOR
# =========================================================

def generate_prompt(requirement: str):

    ai_prompt = f"""
You are CreatCode's AI prompt engineering assistant.

The user wants to build:

{requirement}


Create a high-quality reusable AI prompt.

Use this structure:

ROLE:
Define the expert role the AI should act as.

TASK:
Clearly describe what the AI must do.

REQUIREMENTS:
List important functional requirements.

INPUT:
Describe expected inputs.

OUTPUT:
Describe exactly what should be returned.

CONSTRAINTS:
List limitations and rules.

QUALITY:
Define quality expectations.

The final prompt should be:

- Clear
- Specific
- Reusable
- Well structured
- Easy to copy

Return only the generated prompt.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.3
    )

# =========================================================
# CONTEXT-AWARE AI CHAT
# =========================================================

def chat_with_code(
    message: str,
    code: str = "",
    language: str = "Auto"
):

    ai_prompt = f"""
You are CreatCode's context-aware programming
assistant.

The user is currently working on this code.

LANGUAGE:
{language}

CURRENT CODE:

{code if code.strip() else "No code has been entered yet."}


USER MESSAGE:

{message}


TASK:

Answer the user's programming question
using the current code as context.

IMPORTANT RULES:

1. Focus on the user's question.

2. Use the current code when relevant.

3. If the user asks about an error,
   identify the likely problem and explain
   how to fix it.

4. If the user asks for a modification,
   explain the required change and provide
   the relevant corrected code.

5. If complete code is useful, provide it.

6. Keep the explanation beginner-friendly.

7. Do not invent code behavior that does
   not exist.

8. Do not claim that code was executed
   unless execution actually happened.

9. Use Markdown formatting when helpful.

10. Keep the response concise but useful.

11. If the user asks about a specific
    line or function, focus on that part.

12. If there is no code, answer the
    programming question normally.
"""

    return ask_ai(
        ai_prompt,
        temperature=0.25
    )