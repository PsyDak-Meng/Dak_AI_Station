from openai import OpenAI
import os


class LLM_API:
    def __init__(self, model:str="gpt-3.5-turbo"):
        self.model = model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.system_prompt_ta = """You are a professional investment banking manager, skilled in explaining complex fianncial reports and providing actionable insights.
                                Read the following data from company 10-K filing over the years and explain to me what you think of the company, incuding it's trends and insights in bullet points.
                                Don't tell me how to do the analysis, just give me your thoughts on what the data suggests."""
        self.system_prompt_qa = """You are a professional investment banking manager, skilled in explaining complex fianncial reports and providing actionable insights.
                                Answer my questions on the data you read when you are asked, give short, clear answers while listing out your line of thought as bullet points."""
        

    def text_analysis(self, user_prompt:str):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt_ta},
                {"role": "user", "content": user_prompt}
            ]
        )

        response = completion.choices[0].message.content
        response = ' '.join(response.replace('-','').split('\n-'))

        return response
    
    def qa(self, user_prompt:str):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt_qa},
                {"role": "user", "content": user_prompt}
            ]
        )

        response = completion.choices[0].message.content
        response = ' '.join(response.replace('-','').split('\n-'))

        return response