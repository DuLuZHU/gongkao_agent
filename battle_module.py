import random
import time
from llm_client import analyze_question, call_deepseek

class BattleSession:
    def __init__(self, question_type="all", duration=600):
        self.question_type = question_type
        self.duration = duration
        self.start_time = None
        self.end_time = None
        self.questions = []
        self.current_question_index = 0
        self.players = {}
        self.leaderboard = []
    
    def add_player(self, player_id, player_name):
        self.players[player_id] = {
            'name': player_name,
            'score': 0,
            'correct_count': 0,
            'total_count': 0,
            'answers': {},
            'time_spent': {}
        }
    
    def generate_questions(self, count=10):
        question_templates = {
            '行测': [
                "在一次数学考试中，小明答对了总数的3/4，答错了总数的1/6，还有5道题未答。这次考试共有多少道题？\nA. 60\nB. 80\nC. 100\nD. 120",
                "某公司去年的营业额比前年增长了20%，今年的营业额比去年下降了10%。今年的营业额与前年相比：\nA. 增长8%\nB. 增长10%\nC. 下降8%\nD. 下降10%",
                "甲、乙两人分别从A、B两地同时出发相向而行，甲每小时走5公里，乙每小时走4公里。两人相遇时，甲比乙多走了10公里。A、B两地相距多少公里？\nA. 80\nB. 90\nC. 100\nD. 110",
                "以下哪个选项中的成语使用正确？\nA. 他的演讲引人入胜，大家听得津津有味\nB. 这道数学题很简单，简直是难以置信\nC. 他的表现差强人意，让老师很失望\nD. 这本书的内容差强人意，不值得一读",
                "在市场经济条件下，资源配置的主要方式是：\nA. 政府计划\nB. 市场调节\nC. 企业自主\nD. 行业协会"
            ],
            '申论': [
                "请根据以下材料，概括我国当前面临的主要环境问题。\n\n材料：近年来，我国经济快速发展，但也付出了沉重的环境代价。大气污染严重，PM2.5超标现象普遍；水资源短缺，部分地区地下水过度开采；土壤污染加剧，食品安全受到威胁；生态系统退化，生物多样性减少。",
                "请分析当前我国农村基层治理存在的主要问题，并提出解决对策。",
                "请结合实际，谈谈你对'乡村振兴战略'的理解和认识。"
            ],
            '面试': [
                "如果你被录取为公务员，你将如何适应新的工作环境？",
                "请谈谈你对'为人民服务'宗旨的理解。",
                "如果你的工作与个人利益发生冲突，你会如何处理？"
            ]
        }
        
        if self.question_type == "all":
            all_questions = []
            for q_list in question_templates.values():
                all_questions.extend(q_list)
            self.questions = random.sample(all_questions, min(count, len(all_questions)))
        elif self.question_type in question_templates:
            self.questions = random.sample(question_templates[self.question_type], min(count, len(question_templates[self.question_type])))
        
        for i, q in enumerate(self.questions):
            analysis = analyze_question(q)
            self.questions[i] = {
                'content': q,
                'analysis': analysis,
                'correct_answer': self._extract_answer(analysis)
            }
    
    def _extract_answer(self, analysis):
        if '答案：' in analysis:
            return analysis.split('答案：')[1].strip()[:100]
        return "请参考解析"
    
    def start(self):
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration
    
    def is_active(self):
        return time.time() < self.end_time
    
    def submit_answer(self, player_id, question_index, answer):
        if player_id not in self.players:
            return False
        
        start_time = self.players[player_id]['time_spent'].get(question_index, time.time())
        time_spent = time.time() - start_time
        
        self.players[player_id]['answers'][question_index] = answer
        self.players[player_id]['time_spent'][question_index] = time_spent
        self.players[player_id]['total_count'] += 1
        
        question = self.questions[question_index]
        if self._check_answer(answer, question['correct_answer']):
            self.players[player_id]['score'] += 10
            self.players[player_id]['correct_count'] += 1
        
        return True
    
    def _check_answer(self, user_answer, correct_answer):
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        return user_answer in correct_answer or correct_answer in user_answer
    
    def get_leaderboard(self):
        leaderboard = []
        for player_id, data in self.players.items():
            accuracy = (data['correct_count'] / data['total_count'] * 100) if data['total_count'] > 0 else 0
            avg_time = sum(data['time_spent'].values()) / len(data['time_spent']) if data['time_spent'] else 0
            leaderboard.append({
                'name': data['name'],
                'score': data['score'],
                'accuracy': accuracy,
                'avg_time': avg_time
            })
        
        leaderboard.sort(key=lambda x: (-x['score'], x['avg_time']))
        return leaderboard
    
    def get_current_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            return True
        return False
    
    def get_results(self):
        results = {
            'leaderboard': self.get_leaderboard(),
            'questions': self.questions,
            'duration': self.duration,
            'time_used': time.time() - self.start_time if self.start_time else 0
        }
        return results

def generate_battle_question(question_type="行测"):
    prompt = f"""
    请生成一道公务员考试{question_type}题目，要求：
    1. 题目要有一定难度，符合公务员考试的命题风格
    2. 如果是选择题，请提供四个选项
    3. 请给出正确答案和详细解析
    
    请按照以下格式输出：
    【题目】
    题目内容...
    
    【选项】
    A. ...
    B. ...
    C. ...
    D. ...
    
    【答案】
    ...
    
    【解析】
    ...
    """
    return call_deepseek(prompt)
