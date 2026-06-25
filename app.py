import streamlit as st
import os
import time
from datetime import datetime, timedelta
from config import DB_PATH, DEEPSEEK_API_KEY
from database import (
    add_user, get_user, add_question, add_wrong_answer, get_wrong_answers,
    add_note, search_notes, add_review_task, get_pending_reviews, update_review_status,
    add_shenlun_submission, get_shenlun_submissions, add_battle_record, get_battle_stats
)
from llm_client import (
    analyze_question, critique_shenlun, simulate_interview, generate_variant_questions,
    search_knowledge, generate_review_reminder
)
from knowledge_base import add_to_knowledge_base, search_knowledge_base, build_knowledge_graph, get_review_suggestions
from battle_module import BattleSession, generate_battle_question

st.set_page_config(page_title="公考AI私教", page_icon="📚", layout="wide")

st.markdown("""
<style>
    div[data-testid="stSidebar"] button {
        border: none !important;
        background: transparent !important;
        padding: 6px 0 !important;
        text-align: left !important;
        font-size: 15px !important;
        color: #444 !important;
        font-weight: normal !important;
        box-shadow: none !important;
    }
    div[data-testid="stSidebar"] button:hover {
        color: #1a73e8 !important;
        background: rgba(26, 115, 232, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'battle_session' not in st.session_state:
    st.session_state.battle_session = None
if 'current_battle_question' not in st.session_state:
    st.session_state.current_battle_question = 0

def login():
    st.title("欢迎来到公考AI私教 📚")
    st.subheader("从'刷题机器'到'全能私教'")
    
    tab1, tab2 = st.tabs(["登录", "注册"])
    
    with tab1:
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        
        if st.button("登录"):
            if username and password:
                user = get_user(DB_PATH, username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.current_page = 'home'
                    st.success("登录成功！")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
            else:
                st.warning("请输入用户名和密码")
    
    with tab2:
        new_username = st.text_input("新用户名")
        new_password = st.text_input("新密码", type="password")
        confirm_password = st.text_input("确认密码", type="password")
        
        if st.button("注册"):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success = add_user(DB_PATH, new_username, new_password)
                    if success:
                        st.success("注册成功！请登录")
                    else:
                        st.error("用户名已存在")
                else:
                    st.error("两次密码不一致")
            else:
                st.warning("请填写完整信息")

def main_app():
    if not st.session_state.user:
        login()
        return
    
    user_id = st.session_state.user[0]
    username = st.session_state.user[1]
    
    st.sidebar.title(f"欢迎，{username}")
    st.sidebar.markdown("---")
    
    nav_items = [
        ("🏠 首页", "home"),
        ("📝 真题拆解", "question_analysis"),
        ("✍️ 申论精批", "shenlun"),
        ("🎤 面试模拟", "interview"),
        ("🧠 知识库", "knowledge"),
        ("❌ 错题本", "wrong"),
        ("⚔️ 对战模式", "battle"),
        ("🔔 学习提醒", "review")
    ]
    
    current_page = st.session_state.current_page
    
    for label, page_key in nav_items:
        is_active = current_page == page_key
        if is_active:
            st.sidebar.markdown(f"**{label}**")
        else:
            if st.sidebar.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
    
    if current_page == 'home':
        show_home(user_id)
    elif current_page == 'question_analysis':
        show_question_analysis(user_id)
    elif current_page == 'shenlun':
        show_shenlun_critique(user_id)
    elif current_page == 'interview':
        show_interview_simulation(user_id)
    elif current_page == 'knowledge':
        show_knowledge_base(user_id)
    elif current_page == 'wrong':
        show_wrong_answers(user_id)
    elif current_page == 'battle':
        show_battle_mode(user_id)
    elif current_page == 'review':
        show_review_reminders(user_id)

def show_home(user_id):
    st.title("公考AI私教 📚")
    st.subheader("你的全能备考助手")
    
    stats = get_battle_stats(DB_PATH, user_id)
    wrong_count = len(get_wrong_answers(DB_PATH, user_id))
    pending_reviews = get_pending_reviews(DB_PATH, user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("对战次数", stats['total'])
    with col2:
        st.metric("正确率", f"{(stats['correct']/stats['total']*100) if stats['total'] > 0 else 0:.1f}%")
    with col3:
        st.metric("错题数", wrong_count)
    with col4:
        st.metric("待复习", len(pending_reviews))
    
    st.markdown("---")
    
    st.subheader("今日学习建议")
    suggestions = get_review_suggestions(user_id)
    if suggestions:
        st.write(suggestions)
    else:
        st.write("暂无学习建议，开始学习吧！")
    
    st.markdown("---")
    
    st.subheader("功能导航")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("📝 **真题拆解**")
        st.markdown("深度分析每道题，掌握出题逻辑")
        if st.button("开始刷题", key="start_qa"):
            st.session_state.current_page = 'question_analysis'
            st.rerun()
    
    with col2:
        st.markdown("✍️ **申论精批**")
        st.markdown("逐句批改，提升写作能力")
        if st.button("开始练习", key="start_shenlun"):
            st.session_state.current_page = 'shenlun'
            st.rerun()
    
    with col3:
        st.markdown("🎯 **对战模式**")
        st.markdown("与好友比拼，激发学习动力")
        if st.button("开始对战", key="start_battle"):
            st.session_state.current_page = 'battle'
            st.rerun()

def show_question_analysis(user_id):
    st.title("深度真题拆解引擎")
    st.subheader("粘贴题目，AI为你深度解析")
    
    question = st.text_area("请输入题目内容", height=200)
    
    if st.button("开始分析"):
        if question:
            with st.spinner("AI正在分析题目..."):
                analysis = analyze_question(question)
                st.markdown("## 分析结果")
                st.markdown(analysis)
                
                question_id = add_question(DB_PATH, user_id, question, analysis=analysis)
                add_to_knowledge_base(user_id, f"题目：{question}\n\n分析：{analysis}")
                
                due_date = (datetime.now() + timedelta(days=3)).isoformat()
                add_review_task(DB_PATH, user_id, question_id, due_date)
                
                st.success("题目已保存到知识库，3天后将提醒你复习！")
                
                with st.expander("生成变式题"):
                    variants = generate_variant_questions(question)
                    st.markdown(variants)
        else:
            st.warning("请输入题目内容")

def show_shenlun_critique(user_id):
    st.title("申论智能对练与精批")
    st.subheader("逐句精批，提升写作能力")
    
    mode = st.radio("选择模式", ["完整批改", "小角度对练"])
    
    if mode == "完整批改":
        requirements = st.text_area("题目要求", height=100)
        material = st.text_area("材料内容（如有）", height=150)
        answer = st.text_area("你的答案", height=200)
        
        if st.button("提交批改"):
            if requirements and answer:
                with st.spinner("AI正在批改..."):
                    critique = critique_shenlun(requirements, answer, material)
                    st.markdown("## 批改结果")
                    st.markdown(critique)
                    
                    add_shenlun_submission(DB_PATH, user_id, requirements, answer, material, critique, 0)
                    add_to_knowledge_base(user_id, f"申论题目：{requirements}\n\n我的答案：{answer}\n\n批改：{critique}")
                    
                    st.success("批改完成，已保存到学习记录！")
            else:
                st.warning("请填写题目要求和答案")
    
    else:
        st.subheader("小角度对练")
        skill = st.selectbox("选择练习技能", ["概括问题", "分析原因", "提出对策", "综合分析"])
        
        if skill:
            with st.spinner("AI正在生成练习材料..."):
                prompt = f"""
                请针对"{skill}"这个申论能力点，提供一段材料和一个具体的练习任务。
                材料要简短（200-300字），任务要明确。
                """
                from llm_client import call_deepseek
                exercise = call_deepseek(prompt)
                st.markdown("## 练习材料")
                st.markdown(exercise)
                
                user_answer = st.text_area("你的答案", height=150)
                if st.button("提交练习"):
                    if user_answer:
                        critique_prompt = f"""
                        题目要求：{skill}能力练习
                        材料：{exercise}
                        考生答案：{user_answer}
                        
                        请针对"{skill}"这个能力点进行专项点评，并提供优化建议和示范答案。
                        """
                        critique = call_deepseek(critique_prompt)
                        st.markdown("## 专项点评")
                        st.markdown(critique)

def show_interview_simulation(user_id):
    st.title("面试模拟")
    st.subheader("AI考官在线测评")
    
    question = st.text_area("面试题目", height=100)
    
    if not question:
        sample_questions = [
            "如果你被录取为公务员，你将如何适应新的工作环境？",
            "请谈谈你对'为人民服务'宗旨的理解。",
            "如果你的工作与个人利益发生冲突，你会如何处理？",
            "请介绍一下你的优缺点。"
        ]
        question = st.selectbox("选择示例题目", sample_questions)
    
    answer = st.text_area("你的回答", height=200)
    
    if st.button("开始测评"):
        if answer:
            with st.spinner("AI考官正在评估..."):
                result = simulate_interview(question, answer)
                st.markdown("## 测评结果")
                st.markdown(result)
                
                add_to_knowledge_base(user_id, f"面试题：{question}\n\n我的回答：{answer}\n\n评估：{result}")
                st.success("测评完成！")
        else:
            st.warning("请输入你的回答")

def show_knowledge_base(user_id):
    st.title("专属知识库")
    st.subheader("构建你的外挂大脑")
    
    tab1, tab2, tab3 = st.tabs(["搜索知识", "知识图谱", "添加笔记"])
    
    with tab1:
        query = st.text_input("搜索关键词")
        if st.button("搜索"):
            if query:
                results = search_notes(DB_PATH, user_id, query)
                if results:
                    for note in results:
                        st.markdown(f"**笔记 {note[0]}**")
                        st.markdown(note[3])
                        if note[4]:
                            st.markdown(f"标签：{note[4]}")
                        st.markdown("---")
                else:
                    st.info("本地没有找到相关笔记，正在从知识库搜索...")
                    kb_results = search_knowledge_base(user_id, query)
                    if kb_results['documents']:
                        for doc in kb_results['documents'][0]:
                            st.markdown(doc)
                    else:
                        st.info("正在从AI知识库查询...")
                        ai_result = search_knowledge(query)
                        st.markdown(ai_result)
    
    with tab2:
        if st.button("构建知识图谱"):
            with st.spinner("AI正在构建知识图谱..."):
                graph = build_knowledge_graph(user_id)
                st.markdown(graph)
    
    with tab3:
        content = st.text_area("笔记内容", height=200)
        tags = st.text_input("标签（用逗号分隔）")
        category = st.selectbox("分类", ["行测", "申论", "面试", "常识", "其他"])
        
        if st.button("保存笔记"):
            if content:
                add_note(DB_PATH, user_id, content, tags, category)
                add_to_knowledge_base(user_id, content, {"tags": tags, "category": category})
                st.success("笔记已保存！")
            else:
                st.warning("请输入笔记内容")

def show_wrong_answers(user_id):
    st.title("错题本")
    st.subheader("温故知新，攻克薄弱")
    
    wrong_list = get_wrong_answers(DB_PATH, user_id)
    
    if wrong_list:
        for item in wrong_list:
            wa_id, uid, q_id, user_ans, correct_ans, review_count, last_review, created_at, q_content = item
            
            with st.expander(f"错题 {wa_id}"):
                st.markdown(f"**题目：** {q_content}")
                st.markdown(f"**你的答案：** {user_ans}")
                st.markdown(f"**正确答案：** {correct_ans}")
                st.markdown(f"**复习次数：** {review_count}")
                
                if st.button(f"重新做题", key=f"redo_{wa_id}"):
                    analysis = analyze_question(q_content)
                    st.markdown("## 重新分析")
                    st.markdown(analysis)
    
    else:
        st.info("暂无错题记录")

def show_battle_mode(user_id):
    st.title("小团体对战")
    st.subheader("限时抢答，激发潜能")
    
    if st.session_state.battle_session is None:
        st.subheader("创建对战房间")
        question_type = st.selectbox("题目类型", ["行测", "申论", "面试", "综合"])
        duration = st.slider("对战时长（分钟）", 5, 30, 10)
        
        if st.button("开始对战"):
            with st.spinner("正在生成题目..."):
                session = BattleSession(question_type=question_type, duration=duration*60)
                session.add_player(user_id, st.session_state.user[1])
                session.generate_questions(count=5)
                session.start()
                st.session_state.battle_session = session
                st.session_state.current_battle_question = 0
                st.success("对战开始！")
                st.rerun()
    else:
        session = st.session_state.battle_session
        current_q = st.session_state.current_battle_question
        
        if current_q < len(session.questions):
            question = session.questions[current_q]
            
            st.subheader(f"第 {current_q + 1} / {len(session.questions)} 题")
            st.markdown(f"**题目：** {question['content']}")
            
            answer = st.text_input("你的答案")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("提交答案"):
                    if answer:
                        session.submit_answer(user_id, current_q, answer)
                        st.markdown("**解析：**")
                        st.markdown(question['analysis'])
                else:
                    st.warning("请输入答案")
            
            with col2:
                if st.button("下一题"):
                    st.session_state.current_battle_question += 1
                    st.rerun()
        else:
            st.subheader("对战结束！")
            results = session.get_results()
            
            st.markdown("## 排行榜")
            for i, player in enumerate(results['leaderboard']):
                st.markdown(f"**{i+1}. {player['name']}**")
                st.markdown(f"   得分：{player['score']} | 正确率：{player['accuracy']:.1f}% | 平均用时：{player['avg_time']:.1f}秒")
            
            if st.button("再来一局"):
                st.session_state.battle_session = None
                st.session_state.current_battle_question = 0
                st.rerun()

def show_review_reminders(user_id):
    st.title("学习提醒")
    st.subheader("主动遗忘预警")
    
    pending = get_pending_reviews(DB_PATH, user_id)
    
    if pending:
        for item in pending:
            task_id, uid, q_id, due_date, status, created_at, q_content = item
            
            with st.expander(f"待复习：{q_content[:50]}..."):
                st.markdown(f"**题目：** {q_content}")
                st.markdown(f"**到期时间：** {due_date}")
                
                if st.button(f"立即复习", key=f"review_{task_id}"):
                    with st.spinner("AI正在生成复习提醒..."):
                        reminder = generate_review_reminder(q_content, 3)
                        st.markdown(reminder)
                        
                        analysis = analyze_question(q_content)
                        st.markdown("## 复习解析")
                        st.markdown(analysis)
                        
                        update_review_status(DB_PATH, task_id, 'completed')
                        st.success("复习完成！")
    
    else:
        st.info("暂无待复习任务")
        
        if st.button("生成今日复习建议"):
            with st.spinner("AI正在分析你的学习情况..."):
                suggestions = get_review_suggestions(user_id)
                if suggestions:
                    st.markdown(suggestions)
                else:
                    st.info("学习记录不足，请先开始学习！")

if __name__ == "__main__":
    if not DEEPSEEK_API_KEY:
        st.error("请设置 DEEPSEEK_API_KEY 环境变量")
    else:
        main_app()
