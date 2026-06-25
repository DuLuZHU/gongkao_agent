import os
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SYSTEM_PROMPT

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

def call_deepseek(prompt, system_prompt=SYSTEM_PROMPT, stream=False):
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        stream=stream,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    
    if stream:
        return response
    else:
        return response.choices[0].message.content

def analyze_question(question):
    from config import QUESTION_ANALYSIS_PROMPT
    prompt = QUESTION_ANALYSIS_PROMPT.format(question=question)
    return call_deepseek(prompt)

def critique_shenlun(requirements, answer, material=""):
    from config import SHENLUN_CRITIQUE_PROMPT
    prompt = SHENLUN_CRITIQUE_PROMPT.format(
        requirements=requirements,
        answer=answer,
        material=material
    )
    return call_deepseek(prompt)

def simulate_interview(question, answer):
    from config import INTERVIEW_SIMULATION_PROMPT
    prompt = INTERVIEW_SIMULATION_PROMPT.format(
        question=question,
        answer=answer
    )
    return call_deepseek(prompt)

def generate_variant_questions(base_question, num_questions=2):
    prompt = f"""
    根据以下题目，生成{num_questions}道变式题：

    原题：{base_question}

    要求：
    1. 变式题的题干材料可以不同，但考查的知识点和解题方法必须与原题完全一致
    2. 每道题都要提供选项（如果是选择题）和正确答案
    3. 提供简要的解析说明

    请按照以下格式输出：
    【变式题1】
    题目内容...
    A. ...
    B. ...
    C. ...
    D. ...
    答案：...
    解析：...

    【变式题2】
    ...
    """
    return call_deepseek(prompt)

def search_knowledge(query, context=""):
    prompt = f"""
    作为公考知识库助手，请根据用户的查询，提供相关的知识点和解题技巧。

    用户查询：{query}
    相关上下文（如有）：{context}

    请按照以下结构输出：
    【知识点概述】
    - 核心概念解释

    【解题技巧】
    - 实用的解题方法和公式

    【典型例题】
    - 1-2道典型例题及解析

    【易错点提示】
    - 常见的错误类型和避免方法
    """
    return call_deepseek(prompt)

def generate_review_reminder(question_content, days_ago):
    prompt = f"""
    用户在{days_ago}天前学习了以下知识点，请生成一条友好的复习提醒消息：

    知识点/题目：{question_content}

    要求：
    1. 语气友好、亲切，像私人秘书一样提醒用户
    2. 简要回顾核心考点
    3. 建议用户做一道相关练习题巩固记忆
    """
    return call_deepseek(prompt)
